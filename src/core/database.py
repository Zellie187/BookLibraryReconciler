"""
Database Manager

Responsible for opening and closing
the SQLite database connection.
"""

import sqlite3
from pathlib import Path

from core.calibre_functions import calculate_title_sort


class DatabaseManager:
    """
    Simple SQLite connection manager.
    """

    def __init__(self, database_path):

        self.database_path = Path(database_path)
        self.connection = None

    def connect(self):
        """
        Open the SQLite database.
        """

        self.connection = sqlite3.connect(self.database_path)

        # Return rows as dictionaries
        self.connection.row_factory = sqlite3.Row

        # Calibre's own books_update_trg/books_insert_trg triggers call
        # a custom title_sort() SQL function - see calibre_functions.py.
        self.connection.create_function("title_sort", 1, calculate_title_sort)

        return self.connection

    def close(self):
        """
        Close the database.
        """

        if self.connection:
            self.connection.close()
