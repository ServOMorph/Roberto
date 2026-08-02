"""Test de bout en bout du pont Macrodesk <-> OpenCode.

Pré-requis : une macro nommée ``opencode-envoyer`` enregistrée avec :
clic dans le chat, Ctrl+V, puis clic sur Envoyer.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import pyperclip
from pynput import keyboard

from app import APP_DIR, MacroEngine, MacroStore, ZoneStore, clear_session_active, extract_percent, mark_session_active, read_zone_text


BRIDGE_DIR = APP_DIR / "_workflow_test"
POLL_SECONDS = 1
DEFAULT_TIMEOUT = 180
DEFAULT_WATCH_THRESHOLD = 50


class ContextLimitReached(RuntimeError):
    pass


class UserAbort(RuntimeError):
    """Levée quand l'utilisateur appuie sur Échap pendant une session de contrôle OpenCode."""


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


def find_zone(name: str) -> dict:
    zone = ZoneStore().find_by_name(name)
    if not zone:
        raise FileNotFoundError(f"Zone « {name} » introuvable. Déclarez-la dans Macrodesk avant de lancer ce test.")
    return zone


def check_watch_zone(zone: dict | None, threshold: int) -> None:
    if zone is None:
        return
    text = read_zone_text(zone)
    percent = extract_percent(text)
    if percent is None:
        raise ContextLimitReached(
            f"Lecture OCR de la zone « {zone['name']} » impossible (texte lu : {text.strip()!r})."
        )
    if percent >= threshold:
        raise ContextLimitReached(f"Contexte à {percent}% (seuil {threshold}%) — arrêt avant envoi.")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def wait_for_answer(path: Path, timeout: int, abort_event: threading.Event | None = None) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if abort_event is not None and abort_event.is_set():
            raise UserAbort(f"Arrêt demandé par l'utilisateur (Échap) en attendant {path}.")
        if path.exists():
            answer = path.read_text(encoding="utf-8").strip()
            if answer:
                return answer
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"Aucune réponse écrite dans {path} après {timeout} secondes.")


def find_macro(name: str) -> dict:
    for summary in MacroStore().list():
        if summary["name"].casefold() == name.casefold():
            macro = MacroStore().load(summary["id"])
            if macro:
                return macro
    raise FileNotFoundError(
        f"Macro « {name} » introuvable. Créez-la dans Macrodesk avant de lancer ce test."
    )


def run_macro(engine: MacroEngine, macro: dict, abort_event: threading.Event | None = None) -> None:
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
    macro: dict,
    prompt: str,
    zone: dict | None = None,
    threshold: int = DEFAULT_WATCH_THRESHOLD,
    abort_event: threading.Event | None = None,
) -> None:
    check_watch_zone(zone, threshold)
    if abort_event is not None and abort_event.is_set():
        raise UserAbort("Arrêt demandé par l'utilisateur (Échap) avant l'envoi du prompt.")
    pyperclip.copy(prompt)
    # Le collage est volontairement enregistré dans la macro sous Ctrl+V.
    run_macro(engine, macro, abort_event)


def compact_opencode(
    engine: MacroEngine,
    macro: dict,
    archive_dir: Path,
    abort_event: threading.Event | None = None,
    timeout: int = 120,
) -> None:
    """Demande à OpenCode de compacter son contexte, puis attend la confirmation écrite."""
    pyperclip.copy("/compact")
    run_macro(engine, macro, abort_event)
    response_file = archive_dir / f"compact-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    prompt = (
        "As-tu terminé le /compact demandé juste avant ? Une fois le compactage effectivement "
        f"terminé, écris \"COMPACT TERMINE\" dans ce fichier exact : {response_file.resolve()}"
    )
    pyperclip.copy(prompt)
    run_macro(engine, macro, abort_event)
    wait_for_answer(response_file, timeout, abort_event)


def request_prompt(request_file: Path, response_file: Path) -> str:
    return f"""Tu es OpenCode et tu participes à un test local d'automatisation.

Lis précisément la demande dans le fichier :
{request_file}

Exécute uniquement cette demande dans le dossier de travail partagé. Quand c'est terminé,
écris un compte rendu concis et factuel dans ce fichier exact :
{response_file}

Ne te limite pas à une réponse dans le chat : l'écriture du fichier de réponse est le signal
attendu par le workflow. Termine ensuite ta réponse dans le chat par « FICHIER ÉCRIT ».
"""


def follow_up_prompt(previous_response: Path, response_file: Path, artifact: Path) -> str:
    return f"""Poursuis le test local d'automatisation.

Lis le premier compte rendu :
{previous_response}

Vérifie que le fichier attendu existe et contient exactement `macro bridge OK` :
{artifact}

Écris ton verdict final (SUCCÈS ou ÉCHEC, avec une phrase de justification) dans ce fichier exact :
{response_file}

Ne te limite pas au chat : l'écriture de ce fichier est obligatoire. Termine ensuite dans le chat
par « FICHIER ÉCRIT ».
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Teste l'envoi de prompts vers OpenCode au moyen d'une macro Macrodesk.")
    parser.add_argument("--macro", default="opencode-envoyer", help="nom exact de la macro d'envoi")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="délai maximal par réponse, en secondes")
    parser.add_argument("--watch-zone", default=None, help="nom de la zone Macrodesk à lire par OCR avant chaque envoi")
    parser.add_argument("--watch-threshold", type=int, default=DEFAULT_WATCH_THRESHOLD, help="pourcentage de contexte au-delà duquel l'envoi est refusé")
    args = parser.parse_args()

    if args.timeout < 10:
        parser.error("--timeout doit être d'au moins 10 secondes")

    macro = find_macro(args.macro)
    watch_zone = find_zone(args.watch_zone) if args.watch_zone else None
    BRIDGE_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    request = BRIDGE_DIR / f"{stamp}-demande.md"
    response_one = BRIDGE_DIR / f"{stamp}-reponse-1.md"
    response_two = BRIDGE_DIR / f"{stamp}-reponse-2.md"
    artifact = BRIDGE_DIR / f"{stamp}-artefact.txt"
    manifest = BRIDGE_DIR / f"{stamp}-manifest.json"

    write_text(
        request,
        f"""# Test Macrodesk / OpenCode

Crée le fichier `{artifact}` et écris-y exactement :

macro bridge OK

Ne modifie aucun autre fichier que ceux explicitement demandés dans ce test.
""",
    )
    write_text(
        manifest,
        json.dumps(
            {"macro": macro["name"], "startedAt": datetime.now().isoformat(timespec="seconds"), "status": "started"},
            ensure_ascii=False,
            indent=2,
        ),
    )

    engine = MacroEngine()
    engine.start_listeners()
    abort_event = threading.Event()
    abort_listener = start_abort_listener(engine, abort_event)
    mark_session_active()
    try:
        print("Étape 1/2 — envoi de la demande à OpenCode…")
        send_prompt(engine, macro, request_prompt(request.resolve(), response_one.resolve()), watch_zone, args.watch_threshold, abort_event)
        print(f"Attente de la réponse dans {response_one.name}…")
        first_response = wait_for_answer(response_one, args.timeout, abort_event)
        print("Réponse 1 reçue.")

        print("Étape 2/2 — demande de vérification à OpenCode…")
        send_prompt(engine, macro, follow_up_prompt(response_one.resolve(), response_two.resolve(), artifact.resolve()), watch_zone, args.watch_threshold, abort_event)
        print(f"Attente de la réponse dans {response_two.name}…")
        final_response = wait_for_answer(response_two, args.timeout, abort_event)

        expected = "macro bridge OK"
        artifact_ok = artifact.exists() and artifact.read_text(encoding="utf-8").strip() == expected
        response_ok = "succès" in final_response.casefold() or "succes" in final_response.casefold()
        status = "passed" if artifact_ok and response_ok else "failed"
        write_text(
            manifest,
            json.dumps(
                {
                    "macro": macro["name"],
                    "startedAt": stamp,
                    "status": status,
                    "artifact": str(artifact),
                    "firstResponse": first_response,
                    "finalResponse": final_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"Test {status.upper()} — résultat : {manifest}")
        return 0 if status == "passed" else 1
    except UserAbort as error:
        write_text(
            manifest,
            json.dumps({"macro": macro["name"], "startedAt": stamp, "status": "interrompu_utilisateur", "message": str(error)}, ensure_ascii=False, indent=2),
        )
        print(f"ARRÊT UTILISATEUR (Échap) : {error} — état noté dans {manifest}", file=sys.stderr)
        return 4
    except ContextLimitReached as error:
        print(f"ARRÊT CONTEXTE : {error}", file=sys.stderr)
        return 3
    except (FileNotFoundError, RuntimeError, TimeoutError) as error:
        print(f"TEST BLOQUÉ : {error}", file=sys.stderr)
        return 2
    finally:
        clear_session_active()
        abort_listener.stop()
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())
