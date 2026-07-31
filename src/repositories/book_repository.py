"""
Book Repository
"""

from builders.book_builder import BookBuilder
from repositories.author_repository import AuthorRepository
from repositories.comment_repository import CommentRepository
from repositories.format_repository import FormatRepository
from repositories.identifier_repository import IdentifierRepository
from repositories.language_repository import LanguageRepository
from repositories.publisher_repository import PublisherRepository
from repositories.rating_repository import RatingRepository
from repositories.series_repository import SeriesRepository
from repositories.tag_repository import TagRepository


class BookRepository:

    def __init__(self, database_manager):

        self.db = database_manager

        self.author_repo = AuthorRepository(database_manager)
        self.identifier_repo = IdentifierRepository(database_manager)
        self.series_repo = SeriesRepository(database_manager)
        self.comment_repo = CommentRepository(database_manager)
        self.publisher_repo = PublisherRepository(database_manager)
        self.rating_repo = RatingRepository(database_manager)
        self.language_repo = LanguageRepository(database_manager)
        self.tag_repo = TagRepository(database_manager)
        self.format_repo = FormatRepository(database_manager)

    # ---------------------------------------------------------

    def get_book_count(self):

        cursor = self.db.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")

        row = cursor.fetchone()

        return row[0] if row else 0

    # ---------------------------------------------------------

    def get_books(self, limit=None):

        cursor = self.db.connection.cursor()

        query = """
            SELECT

                id,
                uuid,
                title,
                sort,
                author_sort,
                path,
                has_cover,
                timestamp,
                last_modified,
                pubdate,
                series_index

            FROM books

            ORDER BY id
            """

        if limit is None:
            cursor.execute(query)
        else:
            cursor.execute(query + " LIMIT ?", (limit,))

        author_cache = self.author_repo.get_all_authors()
        identifier_cache = self.identifier_repo.get_all_identifiers()
        publisher_cache = self.publisher_repo.get_all_publishers()
        rating_cache = self.rating_repo.get_all_ratings()
        language_cache = self.language_repo.get_all_languages()
        tag_cache = self.tag_repo.get_all_tags()
        format_cache = self.format_repo.get_all_formats()

        books = []

        for row in cursor.fetchall():

            builder = BookBuilder()

            book = (
                builder.set_basic_info(row)
                .add_authors(author_cache.get(row["id"], []))
                .add_identifiers(identifier_cache.get(row["id"], {}))
                .set_series(self.series_repo.get_series_for_book(row["id"]))
                .set_comments(self.comment_repo.get_comment_for_book(row["id"]))
                .set_publisher(publisher_cache.get(row["id"], ""))
                .set_rating(rating_cache.get(row["id"], 0))
                .add_languages(language_cache.get(row["id"], []))
                .add_tags(tag_cache.get(row["id"], []))
                .add_formats(format_cache.get(row["id"], []))
                .build()
            )

            books.append(book)

        return books

    # ---------------------------------------------------------

    def update_path(self, book_id, new_path):

        cursor = self.db.connection.cursor()

        cursor.execute(
            "UPDATE books SET path = ? WHERE id = ?",
            (new_path, book_id),
        )

        self.db.connection.commit()
