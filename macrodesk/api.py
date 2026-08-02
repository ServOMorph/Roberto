"""Pont JavaScript <-> Python exposé à la fenêtre PyWebView."""

from __future__ import annotations

from typing import Any

from .engine import MacroEngine


class Api:
    def __init__(self, engine: MacroEngine) -> None:
        self.engine = engine

    def get_state(self) -> dict[str, Any]:
        return self.engine.state()

    def prepare_recording(self, name: str) -> dict[str, Any]:
        return self.engine.prepare_recording(name)

    def set_action_mode(self, mode: str) -> dict[str, Any]:
        return self.engine.set_action_mode(mode)

    def set_record_mouse_moves(self, enabled: bool) -> dict[str, Any]:
        return self.engine.set_record_mouse_moves(enabled)

    def select_macro(self, macro_id: str | None) -> dict[str, Any]:
        return self.engine.select(macro_id)

    def rename_macro(self, macro_id: str, name: str) -> dict[str, Any]:
        return self.engine.rename(macro_id, name)

    def delete_macro(self, macro_id: str) -> dict[str, Any]:
        return self.engine.delete(macro_id)

    def set_ui_bounds(self, left: int, top: int, width: int, height: int) -> None:
        self.engine.set_ui_bounds(int(left), int(top), int(width), int(height))

    def create_zone(self, name: str) -> dict[str, Any]:
        return self.engine.create_zone(name)

    def rename_zone(self, zone_id: str, name: str) -> dict[str, Any]:
        return self.engine.rename_zone(zone_id, name)

    def delete_zone(self, zone_id: str) -> dict[str, Any]:
        return self.engine.delete_zone(zone_id)

    def test_zone_ocr(self, zone_id: str) -> dict[str, Any]:
        return self.engine.test_zone_ocr(zone_id)
