from __future__ import annotations

import json

from conftest import make_macro


def test_macro_store_save_then_load(macro_store):
    macro = make_macro(macro_store, "opencode-envoyer")

    assert macro_store.load(macro["id"]) == macro


def test_macro_store_load_unknown_returns_none(macro_store):
    assert macro_store.load("inconnu") is None


def test_macro_store_list_summarises_events(macro_store):
    make_macro(macro_store, "opencode-envoyer", "id-1")

    items = macro_store.list()

    assert len(items) == 1
    assert items[0]["name"] == "opencode-envoyer"
    assert items[0]["events"] == 1


def test_macro_store_list_sorts_newest_first(macro_store):
    macro_store.save({"id": "vieux", "name": "vieux", "createdAt": "2026-01-01T00:00:00", "events": []})
    macro_store.save({"id": "recent", "name": "recent", "createdAt": "2026-08-02T00:00:00", "events": []})

    assert [item["id"] for item in macro_store.list()] == ["recent", "vieux"]


def test_macro_store_list_skips_corrupted_entries(macro_store, macros_dir):
    make_macro(macro_store, "valide", "id-ok")
    corrupted = macros_dir / "id-ko"
    corrupted.mkdir(parents=True)
    (corrupted / "macro.json").write_text("{ pas du json", encoding="utf-8")

    assert [item["id"] for item in macro_store.list()] == ["id-ok"]


def test_macro_store_delete(macro_store):
    macro = make_macro(macro_store, "a-supprimer")

    assert macro_store.delete(macro["id"]) is True
    assert macro_store.load(macro["id"]) is None
    assert macro_store.delete(macro["id"]) is False


def test_zone_store_starts_empty(zone_store):
    assert zone_store.list() == []


def test_zone_store_add_and_find(zone_store):
    zone_store.add({"id": "z1", "name": "OPENCODE_context", "left": 0, "top": 0, "width": 10, "height": 10})

    assert zone_store.find("z1")["name"] == "OPENCODE_context"
    assert zone_store.find("inconnue") is None


def test_zone_store_find_by_name_is_case_insensitive(zone_store):
    zone_store.add({"id": "z1", "name": "OPENCODE_context", "left": 0, "top": 0, "width": 10, "height": 10})

    assert zone_store.find_by_name("opencode_context")["id"] == "z1"
    assert zone_store.find_by_name("absente") is None


def test_zone_store_rename_sanitises_name(zone_store):
    zone_store.add({"id": "z1", "name": "zone", "left": 0, "top": 0, "width": 10, "height": 10})

    zone_store.rename("z1", "nouvelle/zone")

    assert zone_store.find("z1")["name"] == "nouvellezone"


def test_zone_store_delete(zone_store):
    zone_store.add({"id": "z1", "name": "zone", "left": 0, "top": 0, "width": 10, "height": 10})

    assert zone_store.delete("z1") is True
    assert zone_store.list() == []
    assert zone_store.delete("z1") is False


def test_zone_store_survives_corrupted_file(zone_store, zones_file):
    zones_file.write_text("{ cassé", encoding="utf-8")

    assert zone_store.list() == []


def test_zone_store_writes_readable_json(zone_store, zones_file):
    zone_store.add({"id": "z1", "name": "zone", "left": -1920, "top": 0, "width": 10, "height": 10})

    payload = json.loads(zones_file.read_text(encoding="utf-8"))

    assert payload[0]["left"] == -1920
