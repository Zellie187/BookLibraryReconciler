"""
Identifier Repository

Loads all identifiers from Calibre.
"""

from collections import defaultdict


class IdentifierRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_identifiers_for_book(self, book_id):

        return self.get_all_identifiers().get(book_id, {})

    # ---------------------------------------------------------

    def get_all_identifiers(self):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT

                book,
                type,
                val

            FROM identifiers
            """
        )

        books = defaultdict(dict)

        for row in cursor.fetchall():

            books[row["book"]][row["type"]] = row["val"]

        return books