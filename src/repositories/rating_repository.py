"""
Rating Repository

Loads star ratings from Calibre.

Calibre stores ratings on a 0-10 scale (half-star steps); this
repository converts them to the familiar 0-5 star scale.
"""

from collections import defaultdict


class RatingRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_rating_for_book(self, book_id):

        return self.get_all_ratings().get(book_id, 0)

    # ---------------------------------------------------------

    def get_all_ratings(self):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT

                brl.book,
                r.rating

            FROM books_ratings_link brl

            JOIN ratings r

                ON r.id = brl.rating

            WHERE r.rating > 0
            """
        )

        books = defaultdict(int)

        for row in cursor.fetchall():

            books[row["book"]] = row["rating"] / 2

        return books
