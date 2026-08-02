"""Protocole de fichiers partagés entre le pont et l'agent.

L'agent signale la fin d'un tour en écrivant un fichier de réponse : c'est ce signal,
et non son message de chat, que le pont attend.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

from .errors import UserAbort

POLL_SECONDS = 1


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
