"""
Book Library Toolkit Configuration
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

# ----------------------------------------------------
# Debug Information
# ----------------------------------------------------

print(f"Project Root : {ROOT}")
print(f"CSV File     : {CSV_FILE}")
print(f"Metadata DB  : {METADATA_DB}")