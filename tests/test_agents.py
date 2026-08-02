"""Tests du registre d'agents : le point d'extension pour brancher un second agent."""

from __future__ import annotations

import pytest

import agents
from agents.base import CONTEXT_REMAINING, CONTEXT_USED, AgentProfile


def test_opencode_is_registered():
    assert "opencode" in agents.keys()


def test_default_agent_is_registered():
    assert agents.DEFAULT_AGENT in agents.keys()


def test_get_is_case_insensitive():
    assert agents.get("OpenCode") is agents.get("opencode")


def test_get_unknown_agent_lists_available_ones():
    with pytest.raises(KeyError, match="opencode"):
        agents.get("agent-inexistant")


def test_opencode_profile_fields():
    profile = agents.get("opencode")

    assert profile.label == "OpenCode"
    assert profile.send_macro == "opencode-envoyer"
    assert profile.context_zone == "OPENCODE_context"
    assert profile.compact_command == "/compact"
    assert profile.context_metric == CONTEXT_USED


def test_profile_is_immutable():
    with pytest.raises(Exception):
        agents.get("opencode").send_macro = "autre-macro"


def test_unknown_context_metric_is_rejected():
    with pytest.raises(ValueError, match="context_metric"):
        AgentProfile(key="x", label="X", send_macro="m", context_zone="z", context_metric="autre")


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(0, False), (49, False), (50, True), (99, True)],
)
def test_context_used_exceeds_at_or_above_threshold(percent, expected):
    profile = AgentProfile(key="x", label="X", send_macro="m", context_zone="z", context_metric=CONTEXT_USED)

    assert profile.context_exceeded(percent, 50) is expected


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(0, True), (20, True), (21, False), (99, False)],
)
def test_context_remaining_exceeds_at_or_below_threshold(percent, expected):
    """Un agent affichant le contexte restant inverse la comparaison de seuil."""
    profile = AgentProfile(key="x", label="X", send_macro="m", context_zone="z", context_metric=CONTEXT_REMAINING)

    assert profile.context_exceeded(percent, 20) is expected


def test_every_registered_profile_is_consistent():
    for key in agents.keys():
        profile = agents.get(key)
        assert profile.key == key
        assert profile.send_macro
        assert profile.context_zone
        assert profile.compact_command
