"""
Book Library Toolkit Configuration
"""

import json
from pathlib import Path

# ----------------------------------------------------
# Project Root
# ----------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

# ----------------------------------------------------
# Folders
# ----------------------------------------------------

DATA_FOLDER = ROOT / "data"
OUTPUT_FOLDER = ROOT / "output"
REPORT_FOLDER = ROOT / "reports"
LOG_FOLDER = ROOT / "logs"
COVER_FOLDER = ROOT / "covers"

# ----------------------------------------------------
# Settings/config.json overrides
#
# Point "library_path" at a real Calibre library folder to work with
# it instead of the bundled sample data. "metadata_db" defaults to
# "<library_path>/metadata.db" when left blank.
# ----------------------------------------------------

SETTINGS_FILE = ROOT / "Settings" / "config.json"


def _load_settings():

    if not SETTINGS_FILE.exists():
        return {}

    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


_settings = _load_settings()

_library_path = _settings.get("library_path") or ""
_metadata_db = _settings.get("metadata_db") or ""

# ----------------------------------------------------
# Files
# ----------------------------------------------------

CSV_FILE = DATA_FOLDER / "My books sample.csv"

if _library_path:
    LIBRARY_ROOT = Path(_library_path)
    METADATA_DB = Path(_metadata_db) if _metadata_db else LIBRARY_ROOT / "metadata.db"
else:
    LIBRARY_ROOT = DATA_FOLDER
    METADATA_DB = DATA_FOLDER / "metadata.db"

# ----------------------------------------------------
# Create folders automatically
# ----------------------------------------------------

for folder in (
    OUTPUT_FOLDER,
    REPORT_FOLDER,
    LOG_FOLDER,
    COVER_FOLDER,
):
    folder.mkdir(exist_ok=True)