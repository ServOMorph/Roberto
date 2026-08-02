from __future__ import annotations

import threading

import pytest

from _compat import UserAbort, wait_for_answer, write_text


def test_write_text_writes_utf8(tmp_path):
    path = tmp_path / "note.md"

    write_text(path, "compte rendu terminé — é à ü")

    assert path.read_text(encoding="utf-8") == "compte rendu terminé — é à ü"


def test_write_text_overwrites(tmp_path):
    path = tmp_path / "note.md"
    write_text(path, "ancien")

    write_text(path, "nouveau")

    assert path.read_text(encoding="utf-8") == "nouveau"


def test_wait_for_answer_returns_stripped_content(tmp_path):
    path = tmp_path / "reponse.md"
    path.write_text("  FICHIER ÉCRIT  \n", encoding="utf-8")

    assert wait_for_answer(path, timeout=5) == "FICHIER ÉCRIT"


def test_wait_for_answer_times_out_when_absent(tmp_path):
    with pytest.raises(TimeoutError):
        wait_for_answer(tmp_path / "jamais.md", timeout=1)


def test_wait_for_answer_ignores_empty_file(tmp_path):
    path = tmp_path / "vide.md"
    path.write_text("   \n", encoding="utf-8")

    with pytest.raises(TimeoutError):
        wait_for_answer(path, timeout=1)


def test_wait_for_answer_aborts_on_user_event(tmp_path):
    abort = threading.Event()
    abort.set()

    with pytest.raises(UserAbort):
        wait_for_answer(tmp_path / "jamais.md", timeout=30, abort_event=abort)


def test_wait_for_answer_prefers_existing_answer_over_abort(tmp_path):
    """L'abandon est testé avant la lecture : un abort déjà posé l'emporte."""
    path = tmp_path / "reponse.md"
    path.write_text("terminé", encoding="utf-8")
    abort = threading.Event()
    abort.set()

    with pytest.raises(UserAbort):
        wait_for_answer(path, timeout=5, abort_event=abort)
