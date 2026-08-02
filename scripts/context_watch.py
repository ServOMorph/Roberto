"""Test de bout en bout : lecture OCR de la zone de contexte d'un agent sur 3 échanges.

Lancer : ``py -m scripts.context_watch``
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import agents
from agents.base import AgentProfile
from bridge import find_macro, find_zone, send_prompt, wait_for_answer, write_text
from macrodesk.ocr import extract_percent, read_zone_text

from .common import RUNS_DIR, add_agent_arguments, controlled_session

TIMEOUT_PER_TURN = 180
TURNS = 3


def prompt_for_turn(turn: int, response_file: Path, agent: AgentProfile) -> str:
    return f"""Tu es {agent.label}, test de lecture du contexte, échange {turn}/{TURNS}.

Réponds en une phrase courte confirmant que tu as bien reçu ce message, puis écris cette même
phrase dans ce fichier exact :
{response_file}

Termine ensuite ta réponse dans le chat par « {agent.write_ack} »."""


def log_reading(readings: list[dict[str, str]], turn: int, moment: str, text: str, percent: int | None) -> None:
    print(f"Tour {turn}/{TURNS} — lecture {moment} : {percent}% (texte brut : {text.strip()!r})", flush=True)
    readings.append({"turn": str(turn), "when": moment, "text": text.strip(), "percent": str(percent)})


def main() -> int:
    parser = argparse.ArgumentParser(description="Vérifie la lecture OCR du contexte d'un agent sur plusieurs échanges.")
    add_agent_arguments(parser)
    args = parser.parse_args()
    agent = agents.get(args.agent)

    macro = find_macro(agent.send_macro)
    zone = find_zone(args.watch_zone or agent.context_zone)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = RUNS_DIR / f"context-watch-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    readings: list[dict[str, str]] = []

    with controlled_session() as (engine, abort_event):
        try:
            for turn in range(1, TURNS + 1):
                text = read_zone_text(zone)
                log_reading(readings, turn, "avant envoi", text, extract_percent(text))

                response_file = root / f"reponse-{turn:02d}.md"
                print(f"Tour {turn}/{TURNS} — envoi du prompt…", flush=True)
                send_prompt(engine, macro, prompt_for_turn(turn, response_file.resolve(), agent), abort_event=abort_event, agent=agent)
                print(f"Tour {turn}/{TURNS} — attente de {response_file.name}…", flush=True)
                wait_for_answer(response_file, TIMEOUT_PER_TURN, abort_event)
                print(f"Tour {turn}/{TURNS} — réponse reçue.", flush=True)

                text_after = read_zone_text(zone)
                log_reading(readings, turn, "après réponse", text_after, extract_percent(text_after))

            write_text(
                manifest,
                json.dumps(
                    {"status": "passed", "agent": agent.key, "macro": macro["name"], "zone": zone["name"], "readings": readings},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            print(f"TEST CONTEXTE TERMINÉ — manifeste : {manifest}", flush=True)
            return 0
        except Exception as error:
            write_text(
                manifest,
                json.dumps({"status": "blocked", "agent": agent.key, "error": str(error), "readings": readings}, ensure_ascii=False, indent=2),
            )
            print(f"TEST CONTEXTE BLOQUÉ : {error}", file=sys.stderr, flush=True)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
