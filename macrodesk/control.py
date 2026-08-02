"""Signalisation de la prise de contrôle de la machine.

L'état est porté par des fichiers plutôt que par de la mémoire de processus : les scripts
de pont (``scripts/conversation.py``, ``scripts/workflow_check.py``) tournent hors du
processus de l'UI et doivent pouvoir lever le signal que l'UI affiche.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from . import paths


def _raise_flag(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")


def _lower_flag(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def mark_control_active() -> None:
    """Le clavier et la souris sont pilotés par une relecture de macro."""
    _raise_flag(paths.CONTROL_FLAG_FILE)


def clear_control_active() -> None:
    _lower_flag(paths.CONTROL_FLAG_FILE)


def mark_session_active() -> None:
    """Une session de pont vers un agent est en cours, relecture de macro comprise
    mais aussi pendant l'attente de la réponse de l'agent."""
    _raise_flag(paths.CONTROL_SESSION_FLAG_FILE)


def clear_session_active() -> None:
    _lower_flag(paths.CONTROL_SESSION_FLAG_FILE)


def is_control_active() -> bool:
    return paths.CONTROL_FLAG_FILE.exists() or paths.CONTROL_SESSION_FLAG_FILE.exists()
