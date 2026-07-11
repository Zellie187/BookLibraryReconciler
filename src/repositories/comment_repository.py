"""
Comment Repository

Loads book descriptions/comments from Calibre.
"""


class CommentRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_comment_for_book(self, book_id):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT text

            FROM comments

            WHERE book = ?
            """,
            (book_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return ""

        return row["text"] or ""