"""
Report Engine Base

Common interface every report format implements: write pre-shaped
tabular data (headers + rows) to a file. Subclasses only need to
implement write_table(); the two report types this project produces
(organize plan, metadata health) are built on top of it here so every
format gets them for free.
"""

from abc import ABC, abstractmethod

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
