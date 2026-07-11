"""
Library Analyzer

Analyses the loaded library and produces useful statistics.
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

            if book["authors"]:

                for author in book["authors"].split("&"):
                    authors.add(author.strip())

        return len(authors)

    # -------------------------------------------------

    def unique_series(self):

        series = set()

        for book in self.books:

            if book["series"]:
                series.add(book["series"])

        return len(series)

    # -------------------------------------------------

    def books_missing_isbn(self):

        count = 0

        for book in self.books:

            if not book["isbn"]:
                count += 1

        return count

    # -------------------------------------------------

    def books_missing_series(self):

        count = 0

        for book in self.books:

            if not book["series"]:
                count += 1

        return count

    # -------------------------------------------------

    def books_missing_comments(self):

        count = 0

        for book in self.books:

            if not book["comments"]:
                count += 1

        return count

    # -------------------------------------------------

    def top_authors(self, limit=10):

        counter = Counter()

        for book in self.books:

            if book["authors"]:

                for author in book["authors"].split("&"):
                    counter[author.strip()] += 1

        return counter.most_common(limit)