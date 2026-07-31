"""
User Settings

Reads Settings/config.json so the tool can point at a real Calibre
library instead of only the bundled sample data.

Point "library_path" at a real Calibre library folder. "metadata_db"
defaults to "<library_path>/metadata.db" (the normal location Calibre
itself uses) when left blank.
"""

import json
from pathlib import Path

from config.paths import DATA_FOLDER, ROOT

SETTINGS_FILE = ROOT / "Settings" / "config.json"


def load_settings():

    if not SETTINGS_FILE.exists():
        return {}

    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


_settings = load_settings()

_library_path = _settings.get("library_path") or ""
_metadata_db = _settings.get("metadata_db") or ""

if _library_path:
    LIBRARY_ROOT = Path(_library_path)
    METADATA_DB = Path(_metadata_db) if _metadata_db else LIBRARY_ROOT / "metadata.db"
else:
    LIBRARY_ROOT = DATA_FOLDER
    METADATA_DB = DATA_FOLDER / "metadata.db"
