"""
Book Repository
"""

from builders.book_builder import BookBuilder

from repositories.author_repository import AuthorRepository
from repositories.comment_repository import CommentRepository
from repositories.identifier_repository import IdentifierRepository
from repositories.series_repository import SeriesRepository


class BookRepository:

    def __init__(self, database_manager):

        self.db = database_manager

        self.author_repo = AuthorRepository(database_manager)
        self.identifier_repo = IdentifierRepository(database_manager)
        self.series_repo = SeriesRepository(database_manager)
        self.comment_repo = CommentRepository(database_manager)

    # ---------------------------------------------------------

    def get_book_count(self):

        cursor = self.db.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")

        row = cursor.fetchone()

        return row[0] if row else 0

    # ---------------------------------------------------------

    def get_books(self, limit=10):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT

                id,
                uuid,
                title,
                sort,
                author_sort,
                path,
                has_cover,
                timestamp,
                series_index

            FROM books

            ORDER BY id

            LIMIT ?
            """,
            (limit,),
        )

        author_cache = self.author_repo.get_all_authors()
        identifier_cache = self.identifier_repo.get_all_identifiers()

        books = []

        for row in cursor.fetchall():

            builder = BookBuilder()

            book = (
                builder
                .set_basic_info(row)
                .add_authors(author_cache.get(row["id"], []))
                .add_identifiers(identifier_cache.get(row["id"], {}))
                .set_series(self.series_repo.get_series_for_book(row["id"]))
                .set_comments(self.comment_repo.get_comment_for_book(row["id"]))
                .build()
            )

            books.append(book)

        return books