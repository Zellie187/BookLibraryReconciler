"""
Metadata Health Scorer

Checks a Book's completeness across the fields that matter most for a
clean library (title, author, ISBN, cover, description) and produces a
percentage score plus the list of checks that failed.
"""

from dataclasses import dataclass, field

CHECKS = (
    ("title", lambda book: bool(book.title.strip())),
    ("author", lambda book: bool(book.authors)),
    ("isbn", lambda book: bool(book.isbn)),
    ("cover", lambda book: book.has_cover),
    ("description", lambda book: bool(book.comments.strip())),
)


@dataclass
class HealthReport:

    book_id: int = 0
    title: str = ""
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def score(self):

        total = len(self.passed) + len(self.failed)

        if total == 0:
            return 0

        return round((len(self.passed) / total) * 100)


class MetadataScorer:

    def score_book(self, book):

        report = HealthReport(book_id=book.id, title=book.title)

        for name, check in CHECKS:

            if check(book):
                report.passed.append(name)
            else:
                report.failed.append(name)

        return report

    # ---------------------------------------------------------

    def score_library(self, books):

        return [self.score_book(book) for book in books]

    # ---------------------------------------------------------

    def average_score(self, books):

        reports = self.score_library(books)

        if not reports:
            return 0

        return round(sum(report.score for report in reports) / len(reports))
