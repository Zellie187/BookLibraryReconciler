"""
Library Service
"""

from core.timer import Timer
from repositories.book_repository import BookRepository


class LibraryService:

    def __init__(self, database_manager):

        self.book_repository = BookRepository(database_manager)

    # ---------------------------------------------------------

    def get_book_count(self):

        return self.book_repository.get_book_count()

    # ---------------------------------------------------------

    def get_books(self, limit=10):

        timer = Timer()

        timer.start()

        books = self.book_repository.get_books(limit)

        elapsed = timer.stop()

        print(f"\nLoaded {len(books):,} books in {elapsed:.3f} seconds")

        return books