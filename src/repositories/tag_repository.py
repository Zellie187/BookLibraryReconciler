"""
Tag Repository

Loads the tags assigned to each book from Calibre.
"""

from collections import defaultdict


class TagRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_tags_for_book(self, book_id):

        return self.get_all_tags().get(book_id, [])

    # ---------------------------------------------------------

    def get_all_tags(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT

                btl.book,
                t.name

            FROM books_tags_link btl

            JOIN tags t

                ON t.id = btl.tag

            ORDER BY btl.book, t.name
            """)

        books = defaultdict(list)

        for row in cursor.fetchall():

            books[row["book"]].append(row["name"])

        return books
