"""
Report Viewer Widget

Read-only GUI equivalent of the CLI's `report` command (minus writing
a file to disk): pick one of the same four presets - health,
duplicates, series, statistics - and see the same numbers formatted as
text, reusing the exact same analyzers `preview`/`health`/`analyze`/
`report` already use (MetadataScorer, DuplicateDetector,
AuthorDuplicateFinder, find_series_order_issues, LibraryStatistics).
No new business logic, and nothing is written to metadata.db or disk.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from analyzers.library_statistics import LibraryStatistics
from metadata.author_duplicate_finder import AuthorDuplicateFinder
from metadata.duplicate_detector import DuplicateDetector
from metadata.metadata_score import MetadataScorer
from metadata.series_order import find_series_order_issues

REPORT_TYPES = ("health", "duplicates", "series", "statistics")
REPORT_LABELS = {
    "health": "Health",
    "duplicates": "Duplicates",
    "series": "Series",
    "statistics": "Statistics",
}

DEFAULT_LIMIT = 20
TOP_N = 10


def generate_report_text(report_type, library_service, limit=DEFAULT_LIMIT):
    """
    Pure data-to-text step, kept separate from the widget so it's
    testable without constructing any Qt widgets.
    """

    if report_type not in REPORT_TYPES:
        raise ValueError(f"Unknown report type: {report_type!r}")

    books = library_service.get_all_books()

    if report_type == "health":
        return _health_report(books, limit)
    if report_type == "duplicates":
        return _duplicates_report(books, library_service, limit)
    if report_type == "series":
        return _series_report(books, limit)

    return _statistics_report(books)


# ---------------------------------------------------------------------------


def _health_report(books, limit):

    scorer = MetadataScorer()
    reports = scorer.score_library(books)

    lines = [f"Average Metadata Health Score : {scorer.average_score(books)}%", ""]
    lines.append(f"{limit} books most in need of attention:")
    lines.append("")

    worst = sorted(reports, key=lambda report: report.score)[:limit]

    for report in worst:
        failed = ", ".join(report.failed) if report.failed else "none"
        lines.append(
            f"[{report.score:>3}%] #{report.book_id:<6} {report.title!r:<50} missing: {failed}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------


def _duplicates_report(books, library_service, limit):

    isbn_groups = DuplicateDetector().find_isbn_duplicates(books)
    title_groups = DuplicateDetector().find_title_duplicates(books)
    author_groups = AuthorDuplicateFinder().find_duplicates(
        library_service.get_all_author_records()
    )

    lines = [
        f"ISBN duplicate groups   : {len(isbn_groups):,}",
        f"Title duplicate groups  : {len(title_groups):,}",
        f"Duplicate author groups : {len(author_groups):,}",
    ]

    if isbn_groups:
        lines.append("")
        lines.append("ISBN duplicates:")
        for group in isbn_groups[:limit]:
            lines.append(f"  {group.reason}: books {group.book_ids}")

    if title_groups:
        lines.append("")
        lines.append("Title duplicates:")
        for group in title_groups[:limit]:
            lines.append(f"  {group.reason}: books {group.book_ids}")

    if author_groups:
        lines.append("")
        lines.append("Duplicate author groups:")
        for group in author_groups[:limit]:
            lines.append(f"  {group.names} -> merge into author #{group.canonical_author_id}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------


def _series_report(books, limit):

    issues = find_series_order_issues(books)

    lines = [f"Series order issues : {len(issues):,}", ""]

    if not issues:
        return "\n".join(lines)

    for issue in issues[:limit]:
        lines.append(f"  {issue.series_name!r} {issue.issue_type}: {issue.detail}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------


def _statistics_report(books):

    stats = LibraryStatistics(books)

    lines = [f"Total books : {len(books):,}", ""]

    lines.append(f"Top {TOP_N} authors by book count:")
    for author, count in stats.books_per_author()[:TOP_N]:
        lines.append(f"  {author}: {count}")

    lines.append("")
    lines.append(f"Top {TOP_N} series by book count:")
    for series, count in stats.books_per_series()[:TOP_N]:
        lines.append(f"  {series}: {count}")

    lines.append("")
    lines.append("Books per language:")
    for language, count in stats.books_per_language()[:TOP_N]:
        lines.append(f"  {language}: {count}")

    lines.append("")
    lines.append(f"Largest {TOP_N} books (by format size):")
    for book in stats.largest_books(TOP_N):
        lines.append(f"  #{book.id} {book.title!r}: {book.size:,} bytes")

    return "\n".join(lines)


class ReportViewerWidget(QWidget):

    def __init__(self, library_service, parent=None):

        super().__init__(parent)

        self.library_service = library_service

        self.report_box = QComboBox()
        for report_type in REPORT_TYPES:
            self.report_box.addItem(REPORT_LABELS[report_type], userData=report_type)

        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self.generate)

        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Report:"))
        controls_row.addWidget(self.report_box)
        controls_row.addWidget(generate_button)
        controls_row.addStretch()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFontFamily("Consolas")

        layout = QVBoxLayout(self)
        layout.addLayout(controls_row)
        layout.addWidget(self.output)

        self.generate()

    # ---------------------------------------------------------

    def generate(self):

        report_type = self.report_box.currentData()
        self.output.setPlainText(generate_report_text(report_type, self.library_service))
