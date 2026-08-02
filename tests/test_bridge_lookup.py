from __future__ import annotations

import pytest

from _compat import ContextLimitReached, check_watch_zone, find_macro, find_zone
from conftest import make_macro

ZONE = {"id": "z1", "name": "OPENCODE_context", "left": 0, "top": 0, "width": 10, "height": 10}


def test_find_macro_is_case_insensitive(macro_store):
    make_macro(macro_store, "opencode-envoyer")

    assert find_macro("OPENCODE-ENVOYER")["name"] == "opencode-envoyer"


def test_find_macro_missing_raises(macro_store):
    with pytest.raises(FileNotFoundError, match="introuvable"):
        find_macro("macro-absente")


def test_find_zone_is_case_insensitive(zone_store):
    zone_store.add(ZONE)

    assert find_zone("opencode_context")["id"] == "z1"


def test_find_zone_missing_raises(zone_store):
    with pytest.raises(FileNotFoundError, match="introuvable"):
        find_zone("zone-absente")


def test_check_watch_zone_without_zone_is_noop():
    check_watch_zone(None, threshold=50)


def test_check_watch_zone_below_threshold_passes(zone_reader):
    zone_reader("7%")

    check_watch_zone(ZONE, threshold=50)


def test_check_watch_zone_at_threshold_raises(zone_reader):
    zone_reader("50%")

    with pytest.raises(ContextLimitReached, match="50"):
        check_watch_zone(ZONE, threshold=50)


def test_check_watch_zone_above_threshold_raises(zone_reader):
    zone_reader("88 %")

    with pytest.raises(ContextLimitReached):
        check_watch_zone(ZONE, threshold=50)


def test_check_watch_zone_unreadable_raises(zone_reader):
    zone_reader("~~~")

    with pytest.raises(ContextLimitReached, match="impossible"):
        check_watch_zone(ZONE, threshold=50)
