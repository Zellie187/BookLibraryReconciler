"""
Publisher Repository

Loads publisher names from Calibre.
"""

from collections import defaultdict


class PublisherRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_publisher_for_book(self, book_id):

        return self.get_all_publishers().get(book_id, "")

    # ---------------------------------------------------------

    def get_all_publishers(self):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT

                bpl.book,
                p.name

            FROM books_publishers_link bpl

            JOIN publishers p

                ON p.id = bpl.publisher

            ORDER BY bpl.book
            """
        )

        books = defaultdict(str)

        for row in cursor.fetchall():

            # A book may only have one publisher in practice; keep the first.
            if not books[row["book"]]:
                books[row["book"]] = row["name"]

        return books
