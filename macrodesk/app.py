"""Fenêtre principale de Macrodesk."""

from __future__ import annotations

import webview

from . import paths
from .api import Api
from .control import clear_control_active, clear_session_active
from .engine import MacroEngine
from .screen import enable_dpi_awareness, leftmost_screen


def main() -> None:
    enable_dpi_awareness()
    clear_control_active()
    clear_session_active()
    engine = MacroEngine()
    engine.start_listeners()
    screen = leftmost_screen()
    window = webview.create_window(
        "Macrodesk",
        str(paths.UI_DIR / "index.html"),
        js_api=Api(engine),
        width=max(500, screen["width"] // 2),
        height=screen["height"],
        x=screen["left"],
        y=screen["top"],
        min_size=(420, 600),
        background_color="#10131a",
    )

    def sync_ui_bounds(window, *_args) -> None:
        engine.set_ui_bounds(window.x, window.y, window.width, window.height)

    window.events.shown += sync_ui_bounds
    window.events.moved += sync_ui_bounds
    window.events.resized += sync_ui_bounds
    webview.start(debug=False)
