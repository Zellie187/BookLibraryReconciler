"""
Series Repository
"""

from models.series import Series


class SeriesRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_series_for_book(self, book_id):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT
                s.id,
                s.name,
                s.sort,
                s.link

            FROM series s

            INNER JOIN books_series_link l

                ON s.id = l.series

            WHERE l.book = ?
            """,
            (book_id,),
        )

        row = cursor.fetchone()

        if row is None:

            return None

        series = Series()

        series.id = row["id"]
        series.name = row["name"]
        series.sort = row["sort"]
        series.link = row["link"]

        return series
