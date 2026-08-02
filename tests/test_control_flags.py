from __future__ import annotations

from _compat import (
    clear_control_active,
    clear_session_active,
    is_control_active,
    mark_control_active,
    mark_session_active,
)


def test_no_flag_means_no_control(control_flags):
    assert is_control_active() is False


def test_control_flag_marks_control(control_flags):
    control, _session = control_flags

    mark_control_active()

    assert control.exists()
    assert is_control_active() is True


def test_session_flag_marks_control(control_flags):
    _control, session = control_flags

    mark_session_active()

    assert session.exists()
    assert is_control_active() is True


def test_clearing_one_flag_leaves_the_other(control_flags):
    mark_control_active()
    mark_session_active()

    clear_control_active()

    assert is_control_active() is True

    clear_session_active()

    assert is_control_active() is False


def test_clearing_absent_flag_is_silent(control_flags):
    clear_control_active()
    clear_session_active()

    assert is_control_active() is False


def test_flag_creates_missing_parent_directory(tmp_path, monkeypatch):
    import _compat

    control = tmp_path / "profond" / "control.flag"
    session = tmp_path / "profond" / "control_session.flag"
    _compat.set_control_flags(monkeypatch, control, session)

    mark_control_active()

    assert control.exists()
