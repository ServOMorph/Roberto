"""Emplacements de fichiers de l'application.

Les autres modules importent ce module (``from . import paths``) et lisent ses attributs
au moment de l'appel, jamais par ``from .paths import X`` : une redirection de chemin
(tests, instance alternative) reste ainsi effective partout.
"""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
APP_DIR = PACKAGE_DIR.parent
UI_DIR = PACKAGE_DIR / "ui"

DATA_DIR = APP_DIR / "data"
MACROS_DIR = DATA_DIR / "macros"
ZONES_FILE = DATA_DIR / "zones.json"
CONTROL_FLAG_FILE = DATA_DIR / "control.flag"
CONTROL_SESSION_FLAG_FILE = DATA_DIR / "control_session.flag"
