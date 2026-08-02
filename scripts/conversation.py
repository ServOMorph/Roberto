"""Conversation Macrodesk <-> agent : fait avancer une roadmap dans un projet cible.

Lancer : ``py -m scripts.conversation --watch-zone OPENCODE_context --duration 60``
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import agents
from bridge import ContextLimitReached, UserAbort, compact_agent, find_macro, send_prompt, wait_for_answer, write_text

from .common import add_agent_arguments, controlled_session, resolve_watch_zone

TIMEOUT_PER_TURN = 300
DEFAULT_TURNS = 10
# _ROBERTO/ (racine du projet cible) centralise tout ce qui concerne ce projet côté
# pilotage : roadmaps et archives de conversation. Dans le projet cible (pas dans
# Roberto/) pour que l'agent y écrive sans demander de permission de sortir de son
# dossier de travail. Roberto/ ne garde que l'outillage générique (macros, scripts).
DEFAULT_PROJECT = Path(r"D:\ServOMorph\Ponganoid_v6")
DEFAULT_ROADMAP_NAME = "roadmap_10_niveaux_briques_bonus.md"


def roberto_dir(project: Path) -> Path:
    return project / "_ROBERTO"


def default_roadmap(project: Path) -> Path:
    return roberto_dir(project) / "roadmaps" / DEFAULT_ROADMAP_NAME


def conversations_dir(project: Path) -> Path:
    return roberto_dir(project) / "conversations"


def roadmap_complete(roadmap: Path) -> bool:
    """Vrai si la roadmap ne contient plus aucune phase `[EN COURS]` (toutes traitées)."""
    return "[EN COURS]" not in roadmap.read_text(encoding="utf-8")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conversation Macrodesk <-> agent pour faire avancer une roadmap.")
    add_agent_arguments(parser)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT, help="racine du projet cible")
    parser.add_argument("--roadmap", type=Path, default=None, help="roadmap à faire avancer (défaut : roadmap du projet)")
    parser.add_argument("--turns", type=int, default=None, help="nombre de tours à jouer (illimité si --duration est utilisé)")
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="durée maximale en minutes ; passé ce délai, aucun nouveau tour n'est envoyé (le tour en cours va à son terme)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = agents.get(args.agent)
    project = args.project
    roadmap_path = args.roadmap or default_roadmap(project)

    if args.turns is not None:
        turn_count = max(1, args.turns)
    elif args.duration:
        turn_count = sys.maxsize
    else:
        turn_count = DEFAULT_TURNS
    deadline = time.monotonic() + args.duration * 60 if args.duration else None

    if not roadmap_path.exists():
        print(f"Roadmap introuvable : {roadmap_path}", file=sys.stderr)
        return 2

    macro = find_macro(agent.send_macro)
    watch_zone = resolve_watch_zone(args)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = conversations_dir(project) / f"session-{stamp}"
    root.mkdir(parents=True)
    manifest = root / "manifest.json"
    responses: list[dict[str, str]] = []
    turn = 0

    def write_manifest(payload: dict) -> None:
        write_text(manifest, json.dumps({"agent": agent.key, **payload}, ensure_ascii=False, indent=2))

    with controlled_session() as (engine, abort_event):
        try:
            previous_response: str | None = None
            stopped_by_duration = False
            stopped_by_roadmap_complete = False
            while turn < turn_count:
                if deadline is not None and time.monotonic() >= deadline:
                    stopped_by_duration = True
                    print(
                        f"Durée maximale ({args.duration} min) atteinte — arrêt de l'envoi de nouveaux tours "
                        f"après {len(responses)} tour(s) complété(s).",
                        flush=True,
                    )
                    break
                if turn > 0 and roadmap_complete(roadmap_path):
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
                prompt = prompt_for_turn(turn, display_total, project, roadmap_path, response_file.resolve(), previous_response)
                write_text(prompt_file, prompt)
                try:
                    send_prompt(engine, macro, prompt, watch_zone, args.watch_threshold, abort_event, agent)
                except ContextLimitReached:
                    print(f"Tour {turn_label} — contexte élevé, demande de {agent.compact_command}…", flush=True)
                    compact_agent(engine, macro, root, agent, abort_event)
                    print(f"Tour {turn_label} — compactage confirmé, nouvel envoi du prompt…", flush=True)
                    send_prompt(engine, macro, prompt, watch_zone, args.watch_threshold, abort_event, agent)
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
            write_manifest(
                {
                    "status": status,
                    "macro": macro["name"],
                    "project": str(project),
                    "roadmap": str(roadmap_path),
                    "durationMinutes": args.duration,
                    "turnsCompleted": len(responses),
                    "responses": responses,
                }
            )
            print(f"CONVERSATION {status.upper()} — manifeste : {manifest}", flush=True)
            return 0 if status in ("passed", "arrete_duree_max", "roadmap_terminee") else 1
        except UserAbort as error:
            write_manifest(
                {
                    "status": "interrompu_utilisateur",
                    "message": str(error),
                    "project": str(project),
                    "roadmap": str(roadmap_path),
                    "turnsCompleted": len(responses),
                    "turnInterrompu": turn,
                    "responses": responses,
                }
            )
            print(
                f"ARRÊT UTILISATEUR (Échap) au tour {turn}/{turn_count} — {len(responses)} tour(s) complété(s). "
                f"État noté dans {manifest}. Reprise : relire {roadmap_path} pour la phase [EN COURS] réelle.",
                file=sys.stderr,
                flush=True,
            )
            return 4
        except Exception as error:
            write_manifest(
                {
                    "status": "blocked",
                    "error": str(error),
                    "project": str(project),
                    "roadmap": str(roadmap_path),
                    "turnsCompleted": len(responses),
                    "turnInterrompu": turn,
                    "responses": responses,
                }
            )
            print(f"CONVERSATION BLOQUÉE : {error}", file=sys.stderr, flush=True)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
