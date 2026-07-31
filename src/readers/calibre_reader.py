"""
Calibre Database Reader

Reads information from Calibre's metadata.db
"""

import sqlite3
from pathlib import Path


class CalibreReader:

    def __init__(self, database_path):

        self.database_path = Path(database_path)
        self.connection = None

    # -------------------------------------------------

    def connect(self):

        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

    # -------------------------------------------------

    def close(self):

        if self.connection:
            self.connection.close()

    # -------------------------------------------------

    def get_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        return [row[0] for row in cursor.fetchall()]

    # -------------------------------------------------

    def get_book_count(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM books
        """)

        return cursor.fetchone()[0]

    # -------------------------------------------------

    def get_first_books(self, limit=10):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                author_sort,
                path,
                has_cover
            FROM books
            ORDER BY id
            LIMIT ?
        """,
            (limit,),
        )

        return cursor.fetchall()
