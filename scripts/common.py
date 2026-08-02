"""Plomberie partagée par les scripts de pilotage d'agent."""

from __future__ import annotations

import argparse
import threading
from contextlib import contextmanager
from typing import Any, Iterator

import agents
from bridge import DEFAULT_WATCH_THRESHOLD, find_zone, start_abort_listener
from macrodesk import paths
from macrodesk.control import clear_session_active, mark_session_active
from macrodesk.engine import MacroEngine

RUNS_DIR = paths.APP_DIR / "_workflow_test"


def add_agent_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--agent",
        default=agents.DEFAULT_AGENT,
        choices=agents.keys(),
        help="agent à piloter",
    )
    parser.add_argument(
        "--watch-zone",
        default=None,
        help="nom de la zone Macrodesk à lire par OCR avant chaque envoi (sans cette option, aucune surveillance)",
    )
    parser.add_argument(
        "--watch-threshold",
        type=int,
        default=DEFAULT_WATCH_THRESHOLD,
        help="pourcentage de contexte au-delà duquel l'envoi est refusé",
    )


def resolve_watch_zone(args: argparse.Namespace) -> dict[str, Any] | None:
    """Résout la zone de surveillance demandée. Sans --watch-zone, aucune surveillance.

    La zone du profil de l'agent n'est pas prise par défaut ici : surveiller le contexte
    reste un choix explicite pour les sessions longues.
    """
    if not args.watch_zone:
        return None
    return find_zone(args.watch_zone)


@contextmanager
def controlled_session() -> Iterator[tuple[MacroEngine, threading.Event]]:
    """Ouvre une prise de contrôle machine et garantit son nettoyage.

    Le drapeau de session reste levé pendant toute la session, y compris l'attente des
    réponses de l'agent, pour que l'UI affiche la bannière de contrôle sans interruption.
    """
    engine = MacroEngine()
    engine.start_listeners()
    abort_event = threading.Event()
    abort_listener = start_abort_listener(engine, abort_event)
    mark_session_active()
    try:
        yield engine, abort_event
    finally:
        clear_session_active()
        abort_listener.stop()
        engine.stop_listeners()
