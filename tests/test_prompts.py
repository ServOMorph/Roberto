from __future__ import annotations

from pathlib import Path

from _compat import build_turn_prompt, follow_up_prompt, request_prompt, roadmap_complete

PROJECT = Path(r"D:\Projet")
ROADMAP = PROJECT / "_ROBERTO" / "roadmaps" / "roadmap.md"
RESPONSE = PROJECT / "_ROBERTO" / "conversations" / "reponse-01.md"


def test_roadmap_complete_false_when_phase_running(tmp_path):
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("## Phase 1 [FAIT]\n## Phase 2 [EN COURS]\n", encoding="utf-8")

    assert roadmap_complete(roadmap) is False


def test_roadmap_complete_true_when_nothing_running(tmp_path):
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("## Phase 1 [FAIT]\n## Phase 2 [FAIT]\n", encoding="utf-8")

    assert roadmap_complete(roadmap) is True


def test_roadmap_complete_true_on_empty_roadmap(tmp_path):
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("", encoding="utf-8")

    assert roadmap_complete(roadmap) is True


def test_turn_prompt_carries_roadmap_and_response_paths():
    prompt = build_turn_prompt(1, 10, PROJECT, ROADMAP, RESPONSE, None)

    assert str(ROADMAP) in prompt
    assert str(RESPONSE) in prompt


def test_turn_prompt_first_turn_asks_to_inspect_state():
    prompt = build_turn_prompt(1, 10, PROJECT, ROADMAP, RESPONSE, None)

    assert "inspecte" in prompt.casefold()
    assert str(PROJECT) in prompt


def test_turn_prompt_next_turns_reference_running_phase():
    prompt = build_turn_prompt(2, 10, PROJECT, ROADMAP, RESPONSE, "compte rendu du tour 1")

    assert "[EN COURS]" in prompt
    assert "inspecte" not in prompt.casefold()


def test_turn_prompt_does_not_echo_previous_response():
    """Décision du 2026-08-02 : l'écho du compte rendu précédent est une redondance."""
    previous = "COMPTE RENDU PRECEDENT INTEGRAL"

    assert previous not in build_turn_prompt(3, 10, PROJECT, ROADMAP, RESPONSE, previous)


def test_turn_prompt_labels_progress_when_total_known():
    assert "3/10" in build_turn_prompt(3, 10, PROJECT, ROADMAP, RESPONSE, "x")


def test_turn_prompt_labels_turn_only_when_total_unknown():
    prompt = build_turn_prompt(3, 0, PROJECT, ROADMAP, RESPONSE, "x")

    assert "Tour 3" in prompt
    assert "3/0" not in prompt


def test_request_prompt_carries_both_paths(tmp_path):
    request = tmp_path / "demande.md"
    response = tmp_path / "reponse.md"

    prompt = request_prompt(request, response)

    assert str(request) in prompt
    assert str(response) in prompt


def test_follow_up_prompt_carries_all_paths(tmp_path):
    previous = tmp_path / "reponse-1.md"
    response = tmp_path / "reponse-2.md"
    artifact = tmp_path / "artefact.txt"

    prompt = follow_up_prompt(previous, response, artifact)

    assert str(previous) in prompt
    assert str(response) in prompt
    assert str(artifact) in prompt
