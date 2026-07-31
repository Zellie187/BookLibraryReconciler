"""
Report Engine Base

Common interface every report format implements: write pre-shaped
tabular data (headers + rows) to a file. Subclasses only need to
implement write_table(); the two report types this project produces
(organize plan, metadata health) are built on top of it here so every
format gets them for free.
"""

from abc import ABC, abstractmethod

from analyzers.library_analyzer import LibraryAnalyzer
from analyzers.library_statistics import LibraryStatistics
from metadata.metadata_score import MetadataScorer


class ReportWriter(ABC):

    extension = ""

    @abstractmethod
    def write_table(self, headers, rows, output_path):
        """
        Write rows (a list of value lists) under the given headers.
        Returns the path actually written.
        """

        raise NotImplementedError

    # ---------------------------------------------------------

    def write_organize_plan(self, plans, output_path):

        headers = ["book_id", "title", "author", "current_path", "proposed_path", "format_renames"]

        rows = [
            [
                plan.book_id,
                plan.title,
                plan.author,
                plan.current_path,
                plan.proposed_path,
                "; ".join(
                    f"{rename.old_name} -> {rename.new_name}"
                    for rename in plan.format_renames
                    if rename.changed
                ),
            ]
            for plan in plans
        ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_health_report(self, reports, output_path):

        headers = ["book_id", "title", "score", "failed_checks"]

        rows = [
            [report.book_id, report.title, report.score, ", ".join(report.failed)]
            for report in reports
        ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_library_analysis(self, book_analyses, output_path):

        headers = ["book_id", "title", "score", "failed_checks", "issues", "repair_suggestions"]

        rows = [
            [
                analysis.book_id,
                analysis.title,
                analysis.score,
                ", ".join(analysis.failed_checks),
                "; ".join(analysis.issues),
                "; ".join(
                    f"{s.field}: {s.suggested_value or '(review manually)'}"
                    for s in analysis.repair_suggestions
                ),
            ]
            for analysis in book_analyses
        ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_repair_suggestions(self, suggestions, output_path):

        headers = ["book_id", "field", "current_value", "suggested_value", "reason"]

        rows = [
            [s.book_id, s.field, s.current_value, s.suggested_value, s.reason] for s in suggestions
        ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_library_health_summary(self, books, output_path, scorer=None, analyzer=None):
        """
        The spec's "Library Health" report: library-wide counts, not
        one row per book (that's write_health_report/write_library_analysis).
        """

        scorer = scorer or MetadataScorer()
        analyzer = analyzer or LibraryAnalyzer(books)

        unique_formats = {format_name for book in books for format_name in book.formats}

        headers = ["metric", "value"]

        rows = [
            ["total_books", len(books)],
            ["unique_authors", analyzer.unique_authors()],
            ["unique_series", analyzer.unique_series()],
            ["unique_formats", len(unique_formats)],
            ["average_metadata_score", scorer.average_score(books)],
            ["missing_isbn", analyzer.books_missing_isbn()],
            ["missing_description", analyzer.books_missing_comments()],
            ["missing_cover", analyzer.books_missing_cover()],
            ["missing_publisher", sum(1 for book in books if not book.publisher)],
            ["missing_language", sum(1 for book in books if not book.languages)],
        ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_duplicate_report(self, isbn_groups, title_groups, output_path, author_groups=None):

        headers = ["type", "reason", "ids"]

        rows = [["isbn", group.reason, str(group.book_ids)] for group in isbn_groups]
        rows += [["title", group.reason, str(group.book_ids)] for group in title_groups]

        if author_groups:
            rows += [
                ["author", ", ".join(group.names), str(group.all_author_ids)]
                for group in author_groups
            ]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_series_report(self, issues, output_path):

        headers = ["series_name", "issue_type", "detail"]

        rows = [[issue.series_name, issue.issue_type, issue.detail] for issue in issues]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_statistics_report(self, books, output_path, statistics=None):
        """
        Long-format ("category", "label", "value") rather than one
        section per breakdown, so every format writer handles this the
        same way any other flat table is handled - see
        analyzers/library_statistics.py for why.
        """

        statistics = statistics or LibraryStatistics(books)

        headers = ["category", "label", "value"]

        rows = []
        rows += [["books_per_author", name, count] for name, count in statistics.books_per_author()]
        rows += [["books_per_series", name, count] for name, count in statistics.books_per_series()]
        rows += [
            ["books_per_language", language, count]
            for language, count in statistics.books_per_language()
        ]
        rows += [["books_per_year", year, count] for year, count in statistics.books_per_year()]
        rows += [["largest_books", book.title, book.size] for book in statistics.largest_books()]
        rows += [["smallest_books", book.title, book.size] for book in statistics.smallest_books()]

        return self.write_table(headers, rows, output_path)

    # ---------------------------------------------------------

    def write_search_results(self, books, output_path, scorer=None):

        scorer = scorer or MetadataScorer()

        headers = [
            "book_id",
            "title",
            "author",
            "series",
            "rating",
            "metadata_score",
            "isbn",
            "formats",
            "has_cover",
        ]

        rows = [
            [
                book.id,
                book.title,
                book.author_names,
                book.series_name,
                book.rating,
                scorer.score_book(book).score,
                book.isbn,
                ", ".join(book.formats),
                book.has_cover,
            ]
            for book in books
        ]

        return self.write_table(headers, rows, output_path)
