from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _compat


@pytest.fixture
def macros_dir(tmp_path, monkeypatch):
    root = tmp_path / "macros"
    _compat.set_macros_dir(monkeypatch, root)
    return root


@pytest.fixture
def macro_store(macros_dir):
    return _compat.MacroStore()


@pytest.fixture
def zones_file(tmp_path, monkeypatch):
    path = tmp_path / "zones.json"
    _compat.set_zones_file(monkeypatch, path)
    return path


@pytest.fixture
def zone_store(zones_file):
    return _compat.ZoneStore()


@pytest.fixture
def control_flags(tmp_path, monkeypatch):
    control = tmp_path / "control.flag"
    session = tmp_path / "control_session.flag"
    _compat.set_control_flags(monkeypatch, control, session)
    return control, session


@pytest.fixture
def fake_virtual_desktop(monkeypatch):
    """Remplace la capture d'écran par un bureau virtuel déterministe."""

    def install(left: int, top: int, width: int, height: int) -> None:
        class FakeMss:
            monitors = [{"left": left, "top": top, "width": width, "height": height}]

        class FakeModule:
            @staticmethod
            @contextmanager
            def mss():
                yield FakeMss()

        _compat.set_screen_capture(monkeypatch, FakeModule)

    return install


@pytest.fixture
def zone_reader(monkeypatch):
    """Force le texte renvoyé par la lecture OCR d'une zone."""

    def install(text: str) -> None:
        _compat.set_zone_reader(monkeypatch, lambda _zone: text)

    return install


def make_macro(store, name: str, macro_id: str = "abc123") -> dict:
    macro = {
        "id": macro_id,
        "name": name,
        "createdAt": "2026-08-02T10:00:00",
        "events": [{"kind": "key_down", "key": "a", "at": 0.1}],
    }
    store.save(macro)
    return macro
