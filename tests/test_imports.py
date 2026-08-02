"""Garde-fou de restructuration : tout module du projet doit rester importable."""

from __future__ import annotations

import importlib

import pytest

MODULES = [
    "run",
    "macrodesk",
    "macrodesk.api",
    "macrodesk.app",
    "macrodesk.control",
    "macrodesk.engine",
    "macrodesk.keys",
    "macrodesk.ocr",
    "macrodesk.paths",
    "macrodesk.screen",
    "macrodesk.store",
    "agents",
    "agents.base",
    "agents.opencode",
    "bridge",
    "bridge.errors",
    "bridge.files",
    "bridge.lookup",
    "bridge.session",
    "scripts",
    "scripts.common",
    "scripts.context_watch",
    "scripts.conversation",
    "scripts.ocr_reliability",
    "scripts.workflow_check",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    assert importlib.import_module(name) is not None


def test_bridge_exports_are_resolvable():
    import bridge

    for name in bridge.__all__:
        assert getattr(bridge, name) is not None


def test_ui_assets_ship_with_the_package():
    from macrodesk import paths

    assert (paths.UI_DIR / "index.html").is_file()
    assert (paths.UI_DIR / "app.js").is_file()
    assert (paths.UI_DIR / "style.css").is_file()
