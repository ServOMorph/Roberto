"""Prise de contrôle de la machine pour envoyer un prompt à un agent."""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import pyperclip
from pynput import keyboard

from agents.base import AgentProfile
from macrodesk.engine import MacroEngine
from macrodesk.ocr import extract_percent, read_zone_text

from .errors import ContextLimitReached, UserAbort
from .files import wait_for_answer

DEFAULT_WATCH_THRESHOLD = 50
DEFAULT_COMPACT_TIMEOUT = 120


def start_abort_listener(engine: MacroEngine, abort_event: threading.Event) -> keyboard.Listener:
    """Échap : coupe la prise de contrôle en cours (comme F9) et arrête toute la session."""

    def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == keyboard.Key.esc:
            abort_event.set()
            if engine.status == "playing":
                engine.stop_event.set()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener


def check_watch_zone(
    zone: dict[str, Any] | None,
    threshold: int,
    agent: AgentProfile | None = None,
) -> None:
    """Refuse l'envoi si le contexte de l'agent est saturé ou illisible."""
    if zone is None:
        return
    text = read_zone_text(zone)
    percent = extract_percent(text)
    if percent is None:
        raise ContextLimitReached(
            f"Lecture OCR de la zone « {zone['name']} » impossible (texte lu : {text.strip()!r})."
        )
    exceeded = agent.context_exceeded(percent, threshold) if agent else percent >= threshold
    if exceeded:
        raise ContextLimitReached(f"Contexte à {percent}% (seuil {threshold}%) — arrêt avant envoi.")


def run_macro(engine: MacroEngine, macro: dict[str, Any], abort_event: threading.Event | None = None) -> None:
    """Rejoue la macro tout en laissant F9/Échap disponibles comme arrêt d'urgence."""
    with engine.lock:
        engine.status = "playing"
        engine.stop_event.clear()
        engine.message = "Workflow : envoi du prompt en cours — F9 ou Échap pour arrêter."
    engine.play(macro["id"])
    if abort_event is not None and abort_event.is_set():
        raise UserAbort("Arrêt demandé par l'utilisateur (Échap) pendant la prise de contrôle.")
    outcome = engine.message.casefold()
    if "bloqué" in outcome or "interrompue" in outcome or "arrêt demandé" in outcome:
        raise RuntimeError(f"La macro ne s'est pas terminée correctement : {engine.message}")


def send_prompt(
    engine: MacroEngine,
    macro: dict[str, Any],
    prompt: str,
    zone: dict[str, Any] | None = None,
    threshold: int = DEFAULT_WATCH_THRESHOLD,
    abort_event: threading.Event | None = None,
    agent: AgentProfile | None = None,
) -> None:
    check_watch_zone(zone, threshold, agent)
    if abort_event is not None and abort_event.is_set():
        raise UserAbort("Arrêt demandé par l'utilisateur (Échap) avant l'envoi du prompt.")
    pyperclip.copy(prompt)
    # Le collage est volontairement enregistré dans la macro sous Ctrl+V.
    run_macro(engine, macro, abort_event)


def compact_agent(
    engine: MacroEngine,
    macro: dict[str, Any],
    archive_dir: Path,
    agent: AgentProfile,
    abort_event: threading.Event | None = None,
    timeout: int = DEFAULT_COMPACT_TIMEOUT,
) -> None:
    """Demande à l'agent de compacter son contexte, puis attend sa confirmation écrite."""
    pyperclip.copy(agent.compact_command)
    run_macro(engine, macro, abort_event)
    response_file = archive_dir / f"compact-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    prompt = (
        f"As-tu terminé le {agent.compact_command} demandé juste avant ? Une fois le compactage "
        f"effectivement terminé, écris \"{agent.compact_ack}\" dans ce fichier exact : "
        f"{response_file.resolve()}"
    )
    pyperclip.copy(prompt)
    run_macro(engine, macro, abort_event)
    wait_for_answer(response_file, timeout, abort_event)
