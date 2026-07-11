"""
Database Manager

Responsible for opening and closing
the SQLite database connection.
"""

import sqlite3
from pathlib import Path


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

        return self.connection

    def close(self):
        """
        Close the database.
        """

        if self.connection:
            self.connection.close()