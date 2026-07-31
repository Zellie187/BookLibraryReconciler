"""
Excel Report Writer

Not implemented yet (planned v1.4.0 - needs the openpyxl dependency,
which isn't installed yet). Conforms to the ReportWriter interface so
callers can already be written against it.
"""

from reports.base_report import ReportWriter


class ExcelReport(ReportWriter):

    extension = ".xlsx"

    def write_table(self, headers, rows, output_path):

        raise NotImplementedError(
            "Excel reports are planned for v1.4.0 (requires the openpyxl dependency)"
        )
