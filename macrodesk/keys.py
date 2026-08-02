"""Sérialisation des touches clavier entre enregistrement et relecture."""

from __future__ import annotations

import re
from datetime import datetime

from pynput import keyboard


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9 _-]", "", name).strip()
    return cleaned[:60] or datetime.now().strftime("Macro %Y-%m-%d %H-%M")


def key_name(key: keyboard.Key | keyboard.KeyCode) -> str:
    if isinstance(key, keyboard.KeyCode):
        value = key.char
        # Windows reports Ctrl+V as the control character \x16. Store the
        # physical key instead so replaying it while Ctrl is held pastes.
        if value and 1 <= ord(value) <= 26:
            value = chr(ord(value) + 96)
        return value or f"vk:{key.vk}"
    return key.name or str(key)


def restore_key(value: str) -> keyboard.Key | keyboard.KeyCode | None:
    if len(value) == 1:
        if 1 <= ord(value) <= 26:
            value = chr(ord(value) + 96)
        return keyboard.KeyCode.from_char(value)
    if value.startswith("vk:"):
        try:
            return keyboard.KeyCode.from_vk(int(value[3:]))
        except ValueError:
            return None
    return getattr(keyboard.Key, value, None)
