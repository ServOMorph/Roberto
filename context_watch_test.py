"""Test de bout en bout : lecture OCR du contexte OpenCode sur 3 échanges."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from app import APP_DIR, MacroEngine, extract_percent, read_zone_text
from workflow_test import find_macro, find_zone, send_prompt, wait_for_answer, write_text


BRIDGE_DIR = APP_DIR / "_workflow_test"
TIMEOUT_PER_TURN = 180
TURNS = 3


def prompt_for_turn(turn: int, response_file: Path) -> str:
    return f"""Tu es OpenCode, test de lecture du contexte, échange {turn}/{TURNS}.

Réponds en une phrase courte confirmant que tu as bien reçu ce message, puis écris cette même
phrase dans ce fichier exact :
{response_file}

Termine ensuite ta réponse dans le chat par « FICHIER ÉCRIT »."""


def log_reading(readings: list[dict[str, str]], turn: int, moment: str, text: str, percent: int | None) -> None:
    print(f"Tour {turn}/{TURNS} — lecture {moment} : {percent}% (texte brut : {text.strip()!r})", flush=True)
    readings.append({"turn": str(turn), "when": moment, "text": text.strip(), "percent": str(percent)})


def main() -> int:
    macro = find_macro("opencode-envoyer")
    zone = find_zone("OPENCODE_context")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = BRIDGE_DIR / f"context-watch-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    readings: list[dict[str, str]] = []
    engine = MacroEngine()
    engine.start_listeners()

    try:
        for turn in range(1, TURNS + 1):
            text = read_zone_text(zone)
            log_reading(readings, turn, "avant envoi", text, extract_percent(text))

            response_file = root / f"reponse-{turn:02d}.md"
            print(f"Tour {turn}/{TURNS} — envoi du prompt…", flush=True)
            send_prompt(engine, macro, prompt_for_turn(turn, response_file.resolve()))
            print(f"Tour {turn}/{TURNS} — attente de {response_file.name}…", flush=True)
            wait_for_answer(response_file, TIMEOUT_PER_TURN)
            print(f"Tour {turn}/{TURNS} — réponse reçue.", flush=True)

            text_after = read_zone_text(zone)
            log_reading(readings, turn, "après réponse", text_after, extract_percent(text_after))

        write_text(manifest, json.dumps({"status": "passed", "macro": macro["name"], "zone": zone["name"], "readings": readings}, ensure_ascii=False, indent=2))
        print(f"TEST CONTEXTE TERMINÉ — manifeste : {manifest}", flush=True)
        return 0
    except Exception as error:
        write_text(manifest, json.dumps({"status": "blocked", "error": str(error), "readings": readings}, ensure_ascii=False, indent=2))
        print(f"TEST CONTEXTE BLOQUÉ : {error}", file=sys.stderr, flush=True)
        return 2
    finally:
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())
