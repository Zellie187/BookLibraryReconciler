"""
HTML Report Writer

Not implemented yet (planned v1.4.0). Conforms to the ReportWriter
interface so callers can already be written against it.
"""

from reports.base_report import ReportWriter


class HtmlReport(ReportWriter):

    extension = ".html"

    def write_table(self, headers, rows, output_path):

        raise NotImplementedError("HTML reports are planned for v1.4.0")
