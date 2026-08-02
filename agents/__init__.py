"""Registre des agents pilotables.

Pour brancher un nouvel agent : créer `agents/<nom>.py` exposant un `AgentProfile`
nommé `PROFILE`, puis l'ajouter à `_PROFILES` ci-dessous. Rien d'autre à modifier.
"""

from __future__ import annotations

from .base import CONTEXT_REMAINING, CONTEXT_USED, AgentProfile
from .opencode import PROFILE as OPENCODE

_PROFILES: dict[str, AgentProfile] = {
    OPENCODE.key: OPENCODE,
}

DEFAULT_AGENT = OPENCODE.key

__all__ = ["AgentProfile", "CONTEXT_REMAINING", "CONTEXT_USED", "DEFAULT_AGENT", "OPENCODE", "get", "keys"]


def keys() -> list[str]:
    return sorted(_PROFILES)


def get(key: str) -> AgentProfile:
    try:
        return _PROFILES[key.casefold()]
    except KeyError:
        raise KeyError(f"Agent inconnu : {key!r}. Agents disponibles : {', '.join(keys())}.") from None
