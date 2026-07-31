"""
Library Analyzer

Analyses a loaded set of Book objects and produces useful statistics.
"""

from collections import Counter


class LibraryAnalyzer:

    def __init__(self, books):

        self.books = books

    # -------------------------------------------------

    def total_books(self):
        return len(self.books)

    # -------------------------------------------------

    def unique_authors(self):

        authors = set()

        for book in self.books:

            for author in book.authors:
                authors.add(author.name)

        return len(authors)

    # -------------------------------------------------

    def unique_series(self):

        series = set()

        for book in self.books:

            if book.series is not None:
                series.add(book.series.name)

        return len(series)

    # -------------------------------------------------

    def books_missing_isbn(self):

        return sum(1 for book in self.books if not book.isbn)

    # -------------------------------------------------

    def books_missing_series(self):

        return sum(1 for book in self.books if book.series is None)

    # -------------------------------------------------

    def books_missing_comments(self):

        return sum(1 for book in self.books if not book.comments)

    # -------------------------------------------------

    def books_missing_cover(self):

        return sum(1 for book in self.books if not book.has_cover)

    # -------------------------------------------------

    def top_authors(self, limit=10):

        counter = Counter()

        for book in self.books:

            for author in book.authors:
                counter[author.name] += 1

        return counter.most_common(limit)
