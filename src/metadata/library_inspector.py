"""
Library Inspector

Ties per-book quality (MetadataEngine) together with library-wide
checks (duplicate detection, series order) into one whole-library
report - the "Identify Problems" step from the project spec, at
library scope rather than per-book.
"""

from dataclasses import dataclass, field

from metadata.duplicate_detector import DuplicateDetector
from metadata.metadata_engine import MetadataEngine
from metadata.series_order import find_series_order_issues


@dataclass
class LibraryInspection:

    book_analyses: list = field(default_factory=list)
    isbn_duplicate_groups: list = field(default_factory=list)
    title_duplicate_groups: list = field(default_factory=list)
    series_order_issues: list = field(default_factory=list)
    average_score: int = 0

    @property
    def books_needing_attention(self):

        return [analysis for analysis in self.book_analyses if analysis.needs_attention]


class LibraryInspector:

    def __init__(self, metadata_engine=None, duplicate_detector=None):

        self.metadata_engine = metadata_engine or MetadataEngine()
        self.duplicate_detector = duplicate_detector or DuplicateDetector()

    # ---------------------------------------------------------

    def inspect(self, books):

        return LibraryInspection(
            book_analyses=self.metadata_engine.analyze_library(books),
            isbn_duplicate_groups=self.duplicate_detector.find_isbn_duplicates(books),
            title_duplicate_groups=self.duplicate_detector.find_title_duplicates(books),
            series_order_issues=find_series_order_issues(books),
            average_score=self.metadata_engine.scorer.average_score(books),
        )
