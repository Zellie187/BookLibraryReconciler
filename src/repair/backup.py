"""
Database Backup

Copies metadata.db aside before any repair operation writes to it.
"""

import shutil
from datetime import datetime
from pathlib import Path


def backup_database(database_path):

    database_path = Path(database_path)

    if not database_path.exists():
        raise FileNotFoundError(f"Database not found:\n{database_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = database_path.with_name(
        f"{database_path.stem}.{timestamp}.bak"
    )

    shutil.copy2(database_path, backup_path)

    return backup_path
