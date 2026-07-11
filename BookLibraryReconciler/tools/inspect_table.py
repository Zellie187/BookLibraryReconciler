"""
Inspect a single database table.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_FOLDER = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_FOLDER))

from core.config import METADATA_DB
from core.database import DatabaseManager
from core.schema_explorer import SchemaExplorer

LINE = "=" * 70


def inspect(table_name):

    db = DatabaseManager(METADATA_DB)

    db.connect()

    explorer = SchemaExplorer(db)

    if not explorer.table_exists(table_name):

        print(f"\nTable '{table_name}' does not exist.")

        db.close()

        return

    print(LINE)
    print(table_name.upper())
    print(LINE)

    print("\nColumns\n")

    for column in explorer.get_columns(table_name):

        print(
            f"{column['cid']:>2} | "
            f"{column['name']:<30} | "
            f"{column['type']}"
        )

    print("\nForeign Keys\n")

    foreign_keys = explorer.get_foreign_keys(table_name)

    if foreign_keys:

        for key in foreign_keys:
            print(dict(key))

    else:

        print("None")

    print("\nIndexes\n")

    indexes = explorer.get_indexes(table_name)

    if indexes:

        for index in indexes:
            print(dict(index))

    else:

        print("None")

    db.close()


if __name__ == "__main__":

    TABLE = "comments"

    inspect(TABLE)