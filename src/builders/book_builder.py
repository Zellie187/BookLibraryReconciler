"""
Book Builder

Responsible for assembling complete Book objects.
"""

from models.book import Book


class BookBuilder:

    def __init__(self):

        self.book = Book()

    # ---------------------------------------------------------

    def set_basic_info(self, row):

        self.book.id = row["id"]
        self.book.uuid = row["uuid"]

        self.book.title = row["title"]
        self.book.title_sort = row["sort"]

        self.book.author_sort = row["author_sort"]

        self.book.path = row["path"]

        self.book.timestamp = row["timestamp"]

        self.book.pubdate = row["pubdate"] or ""

        self.book.has_cover = bool(row["has_cover"])

        self.book.series_index = row["series_index"] or 0

        return self

    # ---------------------------------------------------------

    def add_authors(self, authors):

        self.book.authors.extend(authors)

        return self

    # ---------------------------------------------------------

    def add_identifiers(self, identifiers):

        self.book.identifiers = identifiers

        self.book.isbn = identifiers.get("isbn", "")

        return self

    # ---------------------------------------------------------

    def set_series(self, series):

        self.book.series = series

        return self

    # ---------------------------------------------------------

    def set_comments(self, comments):

        self.book.comments = comments

        return self

    # ---------------------------------------------------------

    def set_publisher(self, publisher):

        self.book.publisher = publisher or ""

        return self

    # ---------------------------------------------------------

    def set_rating(self, rating):

        self.book.rating = rating or 0

        return self

    # ---------------------------------------------------------

    def add_languages(self, languages):

        self.book.languages = list(languages)

        return self

    # ---------------------------------------------------------

    def add_tags(self, tags):

        self.book.tags = list(tags)

        return self

    # ---------------------------------------------------------

    def add_formats(self, format_files):

        self.book.format_files = list(format_files)

        self.book.formats = [f.format for f in format_files]

        self.book.size = sum(f.size for f in format_files)

        return self

    # ---------------------------------------------------------

    def build(self):

        return self.book
