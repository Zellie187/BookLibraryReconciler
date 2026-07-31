"""
Report Engine Base

Common interface every report format implements: write pre-shaped
tabular data (headers + rows) to a file. Subclasses only need to
implement write_table(); the two report types this project produces
(organize plan, metadata health) are built on top of it here so every
format gets them for free.
"""

from abc import ABC, abstractmethod


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
