"""
Library Service
"""

from core.timer import Timer


class LibraryService:

    def __init__(self, book_repository):

        self.book_repository = book_repository

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

    # ---------------------------------------------------------

    def get_all_books(self):

        return self.get_books(limit=None)

    # ---------------------------------------------------------

    def update_book_path(self, book_id, new_path):

        self.book_repository.update_path(book_id, new_path)

    # ---------------------------------------------------------

    def rename_format(self, book_id, old_format, new_name):

        self.book_repository.format_repo.rename_format(book_id, old_format, new_name)
