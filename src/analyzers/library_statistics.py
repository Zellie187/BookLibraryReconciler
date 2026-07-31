"""
Library Statistics

Long-format breakdowns for the Statistics report: books per author,
series, language, and publication year, plus the largest/smallest
books by total format size. "Long format" (one row per data point,
rather than one column per breakdown) is deliberate - it lets every
report format (CSV/JSON/Excel/HTML/PDF) render this the same way any
other flat table is rendered, with no interface changes.
"""

import re
from collections import Counter

_PUBDATE_YEAR = re.compile(r"^(\d{4})")

# Calibre's own sentinel for "no publish date recorded" - not a real year.
_UNKNOWN_YEAR = "0101"


class LibraryStatistics:

    def __init__(self, books):

        self.books = books

    # ---------------------------------------------------------

    def books_per_author(self):

        counter = Counter()

        for book in self.books:
            for author in book.authors:
                counter[author.name] += 1

        return counter.most_common()

    # ---------------------------------------------------------

    def books_per_series(self):

        counter = Counter()

        for book in self.books:
            if book.series is not None:
                counter[book.series.name] += 1

        return counter.most_common()

    # ---------------------------------------------------------

    def books_per_language(self):

        counter = Counter()

        for book in self.books:
            for language in book.languages:
                counter[language] += 1

        return counter.most_common()

    # ---------------------------------------------------------

    def books_per_year(self):

        counter = Counter()

        for book in self.books:

            match = _PUBDATE_YEAR.match(book.pubdate or "")

            if not match:
                continue

            year = match.group(1)

            if year == _UNKNOWN_YEAR:
                continue

            counter[year] += 1

        return sorted(counter.items())

    # ---------------------------------------------------------

    def largest_books(self, limit=10):

        return sorted(self.books, key=lambda book: book.size, reverse=True)[:limit]

    # ---------------------------------------------------------

    def smallest_books(self, limit=10):

        with_a_format = [book for book in self.books if book.size > 0]

        return sorted(with_a_format, key=lambda book: book.size)[:limit]
