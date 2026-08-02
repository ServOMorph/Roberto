"""Pont générique entre Macrodesk et un agent : indépendant de l'agent piloté.

Tout ce qui est propre à un agent (nom de macro, zone OCR, commande de compactage) est
porté par un `AgentProfile` du package `agents`.
"""

from .errors import ContextLimitReached, UserAbort
from .files import wait_for_answer, write_text
from .lookup import find_macro, find_zone
from .session import (
    DEFAULT_WATCH_THRESHOLD,
    check_watch_zone,
    compact_agent,
    run_macro,
    send_prompt,
    start_abort_listener,
)

__all__ = [
    "ContextLimitReached",
    "DEFAULT_WATCH_THRESHOLD",
    "UserAbort",
    "check_watch_zone",
    "compact_agent",
    "find_macro",
    "find_zone",
    "run_macro",
    "send_prompt",
    "start_abort_listener",
    "wait_for_answer",
    "write_text",
]
