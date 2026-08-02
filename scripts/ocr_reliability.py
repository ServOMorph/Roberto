"""Test automatisé de fiabilité OCR : plusieurs échanges avec un agent, vérifie que la
lecture de la zone de contexte reste lisible et cohérente au fil des tours.

Lancer : ``py -m scripts.ocr_reliability``
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2

import agents
from agents.base import AgentProfile
from bridge import find_macro, find_zone, send_prompt, wait_for_answer, write_text
from macrodesk.ocr import extract_percent, read_zone_text
from macrodesk.screen import grab_bgr

from .common import RUNS_DIR, add_agent_arguments, controlled_session

TIMEOUT_PER_TURN = 180
TURNS = 5


def prompt_for_turn(turn: int, response_file: Path, agent: AgentProfile) -> str:
    return f"""Tu es {agent.label}, test de fiabilité OCR, échange {turn}/{TURNS}.

Réponds en deux phrases courtes sur un sujet libre, puis écris ta réponse dans ce fichier exact :
{response_file}

Termine ensuite ta réponse dans le chat par « {agent.write_ack} »."""


def save_crop(zone: dict, folder: Path, label: str) -> None:
    box = {"left": zone["left"], "top": zone["top"], "width": zone["width"], "height": zone["height"]}
    cv2.imwrite(str(folder / f"{label}.png"), grab_bgr(box))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mesure la fiabilité de la lecture OCR du contexte d'un agent.")
    add_agent_arguments(parser)
    args = parser.parse_args()
    agent = agents.get(args.agent)

    macro = find_macro(agent.send_macro)
    zone = find_zone(args.watch_zone or agent.context_zone)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = RUNS_DIR / f"ocr-reliability-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    readings: list[dict[str, str]] = []
    failures: list[str] = []
    best_percent = -1

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

    with controlled_session() as (engine, abort_event):
        try:
            check("avant-tour-01")
            for turn in range(1, TURNS + 1):
                response_file = root / f"reponse-{turn:02d}.md"
                print(f"Tour {turn}/{TURNS} -- envoi du prompt...", flush=True)
                send_prompt(engine, macro, prompt_for_turn(turn, response_file.resolve(), agent), abort_event=abort_event, agent=agent)
                print(f"Tour {turn}/{TURNS} -- attente de {response_file.name}...", flush=True)
                wait_for_answer(response_file, TIMEOUT_PER_TURN, abort_event)
                check(f"apres-tour-{turn:02d}")

            status = "passed" if not failures else "unreliable"
            write_text(
                manifest,
                json.dumps(
                    {
                        "status": status,
                        "agent": agent.key,
                        "macro": macro["name"],
                        "zone": zone["name"],
                        "readings": readings,
                        "failures": failures,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            print(f"OCR {status.upper()} -- {len(failures)} echec(s) sur {len(readings)} lectures. Manifeste : {manifest}", flush=True)
            return 0 if status == "passed" else 1
        except Exception as error:
            write_text(
                manifest,
                json.dumps(
                    {"status": "blocked", "agent": agent.key, "error": str(error), "readings": readings, "failures": failures},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            print(f"OCR TEST BLOQUÉ : {error}", file=sys.stderr, flush=True)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
