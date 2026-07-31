"""
Language Repository

Loads the languages assigned to each book from Calibre.
"""

from collections import defaultdict


class LanguageRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_languages_for_book(self, book_id):

        return self.get_all_languages().get(book_id, [])

    # ---------------------------------------------------------

    def get_all_languages(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT

                bll.book,
                l.lang_code

            FROM books_languages_link bll

            JOIN languages l

                ON l.id = bll.lang_code

            ORDER BY bll.book, bll.item_order
            """)

        books = defaultdict(list)

        for row in cursor.fetchall():

            books[row["book"]].append(row["lang_code"])

        return books
