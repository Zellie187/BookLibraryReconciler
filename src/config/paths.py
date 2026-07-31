"""
Filesystem Paths

Folders and files that are part of this project's own layout (as
opposed to a Calibre library's layout - see settings.py for that).
"""

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
# Files
# ----------------------------------------------------

CSV_FILE = DATA_FOLDER / "My books sample.csv"

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
