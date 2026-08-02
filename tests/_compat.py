"""Point d'adaptation unique entre la suite de tests et l'arborescence du code.

Les tests n'importent jamais directement les modules applicatifs : ils passent par les
alias définis ici. Une restructuration des packages ne modifie donc que ce fichier,
jamais les assertions.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge import files as bridge_files
from bridge import lookup as bridge_lookup
from bridge import session as bridge_session
from bridge.errors import ContextLimitReached, UserAbort
from macrodesk import ocr as ocr_mod
from macrodesk import paths as paths_mod
from macrodesk import screen as screen_mod
from macrodesk.control import (
    clear_control_active,
    clear_session_active,
    is_control_active,
    mark_control_active,
    mark_session_active,
)
from macrodesk.keys import key_name, restore_key, safe_name
from macrodesk.store import MacroStore, ZoneStore
from scripts import conversation as conversation_mod
from scripts import workflow_check as workflow_mod

extract_percent = ocr_mod.extract_percent
preprocess_zone = ocr_mod.preprocess_zone
clamp_box = screen_mod.clamp_box

write_text = bridge_files.write_text
wait_for_answer = bridge_files.wait_for_answer
find_macro = bridge_lookup.find_macro
find_zone = bridge_lookup.find_zone
check_watch_zone = bridge_session.check_watch_zone

request_prompt = workflow_mod.request_prompt
follow_up_prompt = workflow_mod.follow_up_prompt
roadmap_complete = conversation_mod.roadmap_complete
prompt_for_turn = conversation_mod.prompt_for_turn


def set_macros_dir(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(paths_mod, "MACROS_DIR", path)


def set_zones_file(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(paths_mod, "ZONES_FILE", path)


def set_control_flags(monkeypatch, control: Path, session: Path) -> None:
    monkeypatch.setattr(paths_mod, "CONTROL_FLAG_FILE", control)
    monkeypatch.setattr(paths_mod, "CONTROL_SESSION_FLAG_FILE", session)


def set_screen_capture(monkeypatch, fake_mss) -> None:
    monkeypatch.setattr(screen_mod, "mss", fake_mss)


def set_zone_reader(monkeypatch, reader) -> None:
    monkeypatch.setattr(bridge_session, "read_zone_text", reader)


def build_turn_prompt(turn: int, total: int, project: Path, roadmap: Path, response: Path, previous: str | None) -> str:
    return prompt_for_turn(turn, total, project, roadmap, response, previous)
