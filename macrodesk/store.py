"""Stockage local des macros et des zones de surveillance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import paths
from .keys import safe_name


class MacroStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else paths.MACROS_DIR
        self.root.mkdir(parents=True, exist_ok=True)

    def folder(self, macro_id: str) -> Path:
        return self.root / macro_id

    def list(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for metadata_path in self.root.glob("*/macro.json"):
            try:
                macro = json.loads(metadata_path.read_text(encoding="utf-8"))
                items.append({
                    "id": macro["id"],
                    "name": macro["name"],
                    "createdAt": macro["createdAt"],
                    "events": len(macro.get("events", [])),
                })
            except (OSError, KeyError, json.JSONDecodeError):
                continue
        return sorted(items, key=lambda item: item["createdAt"], reverse=True)

    def load(self, macro_id: str) -> dict[str, Any] | None:
        try:
            return json.loads((self.folder(macro_id) / "macro.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        for summary in self.list():
            if summary["name"].casefold() == name.casefold():
                macro = self.load(summary["id"])
                if macro:
                    return macro
        return None

    def save(self, macro: dict[str, Any]) -> None:
        folder = self.folder(macro["id"])
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "macro.json").write_text(json.dumps(macro, ensure_ascii=False, indent=2), encoding="utf-8")

    def delete(self, macro_id: str) -> bool:
        folder = self.folder(macro_id)
        if not folder.is_dir():
            return False
        # Files created by this app only; remove them individually before the empty folder.
        for child in folder.iterdir():
            if child.is_file():
                child.unlink()
        folder.rmdir()
        return True


class ZoneStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path if path is not None else paths.ZONES_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def list(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def find(self, zone_id: str) -> dict[str, Any] | None:
        for zone in self.list():
            if zone["id"] == zone_id:
                return zone
        return None

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        for zone in self.list():
            if zone["name"].casefold() == name.casefold():
                return zone
        return None

    def save_all(self, zones: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(zones, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, zone: dict[str, Any]) -> None:
        zones = self.list()
        zones.append(zone)
        self.save_all(zones)

    def rename(self, zone_id: str, name: str) -> None:
        zones = self.list()
        for zone in zones:
            if zone["id"] == zone_id:
                zone["name"] = safe_name(name)
        self.save_all(zones)

    def delete(self, zone_id: str) -> bool:
        zones = self.list()
        remaining = [zone for zone in zones if zone["id"] != zone_id]
        if len(remaining) == len(zones):
            return False
        self.save_all(remaining)
        return True
