"""
Schema Explorer

Provides methods for inspecting a SQLite database.
"""

class SchemaExplorer:

    def __init__(self, database_manager):
        self.db = database_manager

    # ----------------------------------------------------------

    def get_tables(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        return [row["name"] for row in cursor.fetchall()]

    # ----------------------------------------------------------

    def get_columns(self, table_name):

        cursor = self.db.connection.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")

        return cursor.fetchall()

    # ----------------------------------------------------------

    def get_foreign_keys(self, table_name):

        cursor = self.db.connection.cursor()

        cursor.execute(f"PRAGMA foreign_key_list({table_name})")

        return cursor.fetchall()

    # ----------------------------------------------------------

    def get_indexes(self, table_name):

        cursor = self.db.connection.cursor()

        cursor.execute(f"PRAGMA index_list({table_name})")

        return cursor.fetchall()

    # ----------------------------------------------------------

    def table_exists(self, table_name):

        return table_name in self.get_tables()