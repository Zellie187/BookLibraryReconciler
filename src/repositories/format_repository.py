"""
Format Repository

Loads the on-disk format files (EPUB, PDF, MOBI, ...) for each book
from Calibre's `data` table.
"""

from collections import defaultdict

from models.format_file import FormatFile


class FormatRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_formats_for_book(self, book_id):

        return self.get_all_formats().get(book_id, [])

    # ---------------------------------------------------------

    def get_all_formats(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT

                book,
                format,
                name,
                uncompressed_size

            FROM data

            ORDER BY book
            """)

        books = defaultdict(list)

        for row in cursor.fetchall():

            format_file = FormatFile(
                format=row["format"],
                name=row["name"],
                size=row["uncompressed_size"] or 0,
            )

            books[row["book"]].append(format_file)

        return books

    # ---------------------------------------------------------

    def rename_format(self, book_id, old_format, new_name):
        """
        Update the stored filename (without extension) for one
        book/format pair after the file has been renamed on disk.
        """

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            UPDATE data

            SET name = ?

            WHERE book = ? AND format = ?
            """,
            (new_name, book_id, old_format),
        )

        self.db.connection.commit()
