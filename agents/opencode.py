"""Profil de l'agent OpenCode."""

from __future__ import annotations

from .base import CONTEXT_USED, AgentProfile

PROFILE = AgentProfile(
    key="opencode",
    label="OpenCode",
    send_macro="opencode-envoyer",
    context_zone="OPENCODE_context",
    context_metric=CONTEXT_USED,
    compact_command="/compact",
    compact_ack="COMPACT TERMINE",
)
