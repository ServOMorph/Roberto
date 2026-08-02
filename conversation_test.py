"""Conversation Macrodesk <-> OpenCode : fait avancer le développement de Ponganoid_v6."""

from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import argparse

from app import MacroEngine, mark_session_active, clear_session_active
from workflow_test import (
    DEFAULT_WATCH_THRESHOLD,
    ContextLimitReached,
    UserAbort,
    compact_opencode,
    find_macro,
    find_zone,
    send_prompt,
    start_abort_listener,
    wait_for_answer,
    write_text,
)


def roadmap_complete(roadmap: Path) -> bool:
    """Vrai si la roadmap ne contient plus aucune phase `[EN COURS]` (toutes traitées)."""
    return "[EN COURS]" not in roadmap.read_text(encoding="utf-8")


TIMEOUT_PER_TURN = 300
DEFAULT_TURNS = 10
PROJECT_DIR = Path(r"D:\ServOMorph\Ponganoid_v6")
# _ROBERTO/ (racine du projet cible) centralise tout ce qui concerne ce projet côté
# pilotage OpenCode : roadmaps et archives de conversation. Dans le projet cible (pas
# dans Roberto/) pour qu'OpenCode y écrive sans demander de permission de sortir de son
# dossier de travail. Roberto/ ne garde que l'outillage générique (macros, scripts).
ROBERTO_DIR = PROJECT_DIR / "_ROBERTO"
ROADMAP_PATH = ROBERTO_DIR / "roadmaps" / "roadmap_10_niveaux_briques_bonus.md"
BRIDGE_DIR = ROBERTO_DIR / "conversations"


def prompt_for_turn(
    turn: int,
    total_turns: int,
    project: Path,
    roadmap: Path,
    response_file: Path,
    previous_response: str | None,
) -> str:
    context = (
        f"Aucun compte rendu de tour précédent dans cette session : inspecte l'état actuel de "
        f"`{project}` et de `{roadmap}` avant de commencer."
        if not previous_response
        else "Continue selon la phase [EN COURS] de la roadmap."
    )
    turn_label = f"{turn}/{total_turns}" if total_turns else str(turn)
    return f"""Tour {turn_label}.

Roadmap : `{roadmap}`

{context}

Fichier de compte rendu de ce tour : `{response_file}`
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Conversation Macrodesk <-> OpenCode pour faire avancer Ponganoid_v6.")
    parser.add_argument("--watch-zone", default=None, help="nom de la zone Macrodesk à lire par OCR avant chaque envoi")
    parser.add_argument("--watch-threshold", type=int, default=DEFAULT_WATCH_THRESHOLD, help="pourcentage de contexte au-delà duquel l'envoi est refusé")
    parser.add_argument("--turns", type=int, default=None, help="nombre de tours à jouer dans cette session (illimité par défaut si --duration est utilisé)")
    parser.add_argument("--duration", type=float, default=None, help="durée maximale de la session en minutes ; passé ce délai, aucun nouveau tour n'est envoyé (le tour en cours va jusqu'à son terme)")
    args = parser.parse_args()
    if args.turns is not None:
        turn_count = max(1, args.turns)
    elif args.duration:
        turn_count = sys.maxsize
    else:
        turn_count = DEFAULT_TURNS
    deadline = time.monotonic() + args.duration * 60 if args.duration else None

    if not ROADMAP_PATH.exists():
        print(f"Roadmap introuvable : {ROADMAP_PATH}", file=sys.stderr)
        return 2

    macro = find_macro("opencode-envoyer")
    watch_zone = find_zone(args.watch_zone) if args.watch_zone else None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = BRIDGE_DIR / f"session-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    responses: list[dict[str, str]] = []
    engine = MacroEngine()
    engine.start_listeners()
    abort_event = threading.Event()
    abort_listener = start_abort_listener(engine, abort_event)
    mark_session_active()
    turn = 0

    try:
        previous_response: str | None = None
        stopped_by_duration = False
        stopped_by_roadmap_complete = False
        turn = 0
        while turn < turn_count:
            if deadline is not None and time.monotonic() >= deadline:
                stopped_by_duration = True
                print(
                    f"Durée maximale ({args.duration} min) atteinte — arrêt de l'envoi de nouveaux tours "
                    f"après {len(responses)} tour(s) complété(s).",
                    flush=True,
                )
                break
            if turn > 0 and roadmap_complete(ROADMAP_PATH):
                stopped_by_roadmap_complete = True
                print(
                    f"Roadmap terminée (plus aucune phase [EN COURS]) — arrêt après "
                    f"{len(responses)} tour(s) complété(s).",
                    flush=True,
                )
                break
            turn += 1
            response_file = root / f"reponse-{turn:02d}.md"
            prompt_file = root / f"prompt-{turn:02d}.md"
            turn_label = f"{turn}/{turn_count}" if not args.duration else str(turn)
            print(f"Tour {turn_label} — envoi du prompt…", flush=True)
            display_total = turn_count if not args.duration else 0
            prompt = prompt_for_turn(turn, display_total, PROJECT_DIR, ROADMAP_PATH, response_file.resolve(), previous_response)
            write_text(prompt_file, prompt)
            try:
                send_prompt(engine, macro, prompt, watch_zone, args.watch_threshold, abort_event)
            except ContextLimitReached:
                print(f"Tour {turn_label} — contexte élevé, demande de /compact à OpenCode…", flush=True)
                compact_opencode(engine, macro, root, abort_event)
                print(f"Tour {turn_label} — /compact confirmé, nouvel envoi du prompt…", flush=True)
                send_prompt(engine, macro, prompt, watch_zone, args.watch_threshold, abort_event)
            print(f"Tour {turn_label} — attente de {response_file.name}…", flush=True)
            previous_response = wait_for_answer(response_file, TIMEOUT_PER_TURN, abort_event)
            responses.append({"turn": str(turn), "response": previous_response})
            print(f"Tour {turn_label} — réponse reçue.", flush=True)

        if stopped_by_roadmap_complete:
            status = "roadmap_terminee"
        elif stopped_by_duration:
            status = "arrete_duree_max"
        elif len(responses) == turn_count:
            status = "passed"
        else:
            status = "failed"
        write_text(
            manifest,
            json.dumps(
                {
                    "status": status,
                    "macro": macro["name"],
                    "project": str(PROJECT_DIR),
                    "roadmap": str(ROADMAP_PATH),
                    "durationMinutes": args.duration,
                    "turnsCompleted": len(responses),
                    "responses": responses,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"CONVERSATION {status.upper()} — manifeste : {manifest}", flush=True)
        return 0 if status in ("passed", "arrete_duree_max", "roadmap_terminee") else 1
    except UserAbort as error:
        write_text(
            manifest,
            json.dumps(
                {
                    "status": "interrompu_utilisateur",
                    "message": str(error),
                    "project": str(PROJECT_DIR),
                    "roadmap": str(ROADMAP_PATH),
                    "turnsCompleted": len(responses),
                    "turnInterrompu": turn,
                    "responses": responses,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(
            f"ARRÊT UTILISATEUR (Échap) au tour {turn}/{turn_count} — {len(responses)} tour(s) complété(s). "
            f"État noté dans {manifest}. Reprise : relire {ROADMAP_PATH} pour la phase [EN COURS] réelle.",
            file=sys.stderr,
            flush=True,
        )
        return 4
    except Exception as error:
        write_text(
            manifest,
            json.dumps(
                {
                    "status": "blocked",
                    "error": str(error),
                    "project": str(PROJECT_DIR),
                    "roadmap": str(ROADMAP_PATH),
                    "turnsCompleted": len(responses),
                    "turnInterrompu": turn,
                    "responses": responses,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"CONVERSATION BLOQUÉE : {error}", file=sys.stderr, flush=True)
        return 2
    finally:
        clear_session_active()
        abort_listener.stop()
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())
