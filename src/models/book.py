"""
Book Model

Represents a single Calibre book.
"""

from dataclasses import dataclass, field

from models.author import Author
from models.format_file import FormatFile
from models.series import Series


@dataclass
class Book:

    # Database
    id: int = 0
    uuid: str = ""

    # Titles
    title: str = ""
    title_sort: str = ""

    # Authors
    authors: list[Author] = field(default_factory=list)
    author_sort: str = ""

    # Series
    series: Series | None = None
    series_index: float = 0.0

    # Publication
    publisher: str = ""
    pubdate: str = ""

    # Metadata
    isbn: str = ""
    identifiers: dict = field(default_factory=dict)

    languages: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    comments: str = ""

    rating: int = 0

    formats: list[str] = field(default_factory=list)
    format_files: list[FormatFile] = field(default_factory=list)

    has_cover: bool = False

    path: str = ""

    timestamp: str = ""
    last_modified: str = ""

    size: int = 0

    def add_author(self, author: Author):

        self.authors.append(author)

    @property
    def author_names(self):

        if not self.authors:
            return "Unknown"

        return ", ".join(author.name for author in self.authors)

    @property
    def series_name(self):

        if self.series is None:
            return ""

        return self.series.name

    def __str__(self):

        return f"{self.title} - {self.author_names}"
