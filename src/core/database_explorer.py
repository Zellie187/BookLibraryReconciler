"""
Database Explorer

Provides tools for exploring the SQLite database.
"""


class DatabaseExplorer:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_tables(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        return [row["name"] for row in cursor.fetchall()]

    # ---------------------------------------------------------

    def get_columns(self, table_name):

        cursor = self.db.connection.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")

        return cursor.fetchall()
