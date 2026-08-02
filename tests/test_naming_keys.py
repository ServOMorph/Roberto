from __future__ import annotations

import pytest
from pynput import keyboard

from _compat import key_name, restore_key, safe_name


def test_safe_name_strips_forbidden_characters():
    assert safe_name("opencode/envoyer:v2") == "opencodeenvoyerv2"


def test_safe_name_keeps_allowed_characters():
    assert safe_name("opencode-envoyer_2 bis") == "opencode-envoyer_2 bis"


def test_safe_name_trims_surrounding_spaces():
    assert safe_name("  macro  ") == "macro"


def test_safe_name_truncates_to_60_characters():
    assert len(safe_name("a" * 200)) == 60


def test_safe_name_falls_back_when_empty():
    assert safe_name("///").startswith("Macro ")


def test_key_name_plain_character():
    assert key_name(keyboard.KeyCode.from_char("v")) == "v"


def test_key_name_translates_control_character():
    assert key_name(keyboard.KeyCode.from_char("\x16")) == "v"


def test_key_name_special_key():
    assert key_name(keyboard.Key.enter) == "enter"


def test_key_name_virtual_code_fallback():
    assert key_name(keyboard.KeyCode.from_vk(190)) == "vk:190"


@pytest.mark.parametrize("value", ["v", "enter", "ctrl", "vk:190"])
def test_restore_key_roundtrip(value):
    restored = restore_key(value)
    assert restored is not None
    assert key_name(restored) == value


def test_restore_key_control_character():
    assert restore_key("\x16") == keyboard.KeyCode.from_char("v")


def test_restore_key_unknown_name():
    assert restore_key("touche_inexistante") is None


def test_restore_key_invalid_virtual_code():
    assert restore_key("vk:abc") is None
