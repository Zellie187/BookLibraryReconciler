"""
Book Library Reconciler

Developer Tool

Explore the SQLite database.
"""

import sys
from pathlib import Path

# ----------------------------------------------------
# Allow imports from src/
# ----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_FOLDER = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_FOLDER))

# ----------------------------------------------------

from config.constants import LINE
from config.settings import METADATA_DB
from core.database import DatabaseManager


def main():

    print(LINE)
    print("DATABASE EXPLORER")
    print(LINE)

    db = DatabaseManager(METADATA_DB)

    db.connect()

    cursor = db.connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    report = []

    for table in tables:

        table_name = table["name"]

        print(f"\n{table_name}")

        report.append("=" * 70)
        report.append(table_name)
        report.append("=" * 70)

        cursor.execute(f"PRAGMA table_info({table_name})")

        columns = cursor.fetchall()

        for column in columns:

            line = (
                f"{column['cid']:>2} | "
                f"{column['name']:<30} | "
                f"{column['type']}"
            )

            print(line)

            report.append(line)

        report.append("")

    db.close()

    report_folder = PROJECT_ROOT / "reports"

    report_file = report_folder / "database_schema.txt"

    report_file.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\n")

    print(LINE)
    print("Schema written to:")
    print(report_file)
    print(LINE)


if __name__ == "__main__":
    main()