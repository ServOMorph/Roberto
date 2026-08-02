"""Test automatisé de fiabilité OCR : plusieurs échanges avec OpenCode, vérifie que la
lecture de la zone de contexte reste lisible et non décroissante au fil des tours."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import cv2

from app import APP_DIR, MacroEngine, extract_percent, grab_bgr, read_zone_text
from workflow_test import find_macro, find_zone, send_prompt, wait_for_answer, write_text


BRIDGE_DIR = APP_DIR / "_workflow_test"
TIMEOUT_PER_TURN = 180
TURNS = 5


def prompt_for_turn(turn: int, response_file: Path) -> str:
    return f"""Tu es OpenCode, test de fiabilité OCR, échange {turn}/{TURNS}.

Réponds en deux phrases courtes sur un sujet libre, puis écris ta réponse dans ce fichier exact :
{response_file}

Termine ensuite ta réponse dans le chat par « FICHIER ÉCRIT »."""


def save_crop(zone: dict, folder: Path, label: str) -> None:
    box = {"left": zone["left"], "top": zone["top"], "width": zone["width"], "height": zone["height"]}
    cv2.imwrite(str(folder / f"{label}.png"), grab_bgr(box))


def main() -> int:
    macro = find_macro("opencode-envoyer")
    zone = find_zone("OPENCODE_context")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = BRIDGE_DIR / f"ocr-reliability-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    readings: list[dict[str, str]] = []
    failures: list[str] = []
    best_percent = -1
    engine = MacroEngine()
    engine.start_listeners()

    def check(label: str) -> None:
        nonlocal best_percent
        text = read_zone_text(zone)
        percent = extract_percent(text)
        readings.append({"label": label, "text": text.strip(), "percent": str(percent)})
        print(f"{label} -- {percent}% (texte : {text.strip()!r})", flush=True)
        if percent is None:
            save_crop(zone, root, f"echec-{label}")
            failures.append(f"{label} : lecture illisible ({text.strip()!r})")
        elif percent < best_percent:
            save_crop(zone, root, f"echec-{label}")
            failures.append(f"{label} : contexte en baisse ({percent}% après {best_percent}%)")
        else:
            best_percent = percent

    try:
        check("avant-tour-01")
        for turn in range(1, TURNS + 1):
            response_file = root / f"reponse-{turn:02d}.md"
            print(f"Tour {turn}/{TURNS} -- envoi du prompt...", flush=True)
            send_prompt(engine, macro, prompt_for_turn(turn, response_file.resolve()))
            print(f"Tour {turn}/{TURNS} -- attente de {response_file.name}...", flush=True)
            wait_for_answer(response_file, TIMEOUT_PER_TURN)
            check(f"apres-tour-{turn:02d}")

        status = "passed" if not failures else "unreliable"
        write_text(
            manifest,
            json.dumps(
                {"status": status, "macro": macro["name"], "zone": zone["name"], "readings": readings, "failures": failures},
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"OCR {status.upper()} -- {len(failures)} echec(s) sur {len(readings)} lectures. Manifeste : {manifest}", flush=True)
        return 0 if status == "passed" else 1
    except Exception as error:
        write_text(manifest, json.dumps({"status": "blocked", "error": str(error), "readings": readings, "failures": failures}, ensure_ascii=False, indent=2))
        print(f"OCR TEST BLOQUÉ : {error}", file=sys.stderr, flush=True)
        return 2
    finally:
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())
