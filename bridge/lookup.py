"""Résolution des ressources Macrodesk nécessaires au pont."""

from __future__ import annotations

from typing import Any

from macrodesk.store import MacroStore, ZoneStore


def find_macro(name: str) -> dict[str, Any]:
    macro = MacroStore().find_by_name(name)
    if not macro:
        raise FileNotFoundError(
            f"Macro « {name} » introuvable. Créez-la dans Macrodesk avant de lancer ce script."
        )
    return macro


def find_zone(name: str) -> dict[str, Any]:
    zone = ZoneStore().find_by_name(name)
    if not zone:
        raise FileNotFoundError(
            f"Zone « {name} » introuvable. Déclarez-la dans Macrodesk avant de lancer ce script."
        )
    return zone
