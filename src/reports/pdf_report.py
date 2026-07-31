"""
PDF Report Writer

Needs the optional `fpdf2` dependency (import name `fpdf`) - only
imported when this class is actually instantiated to write a table.

This is a plain tabular dump, not a polished layout: columns are fixed
width and long values are truncated rather than wrapped. Good enough
for "get this data into a PDF"; a nicer layout is future work.
"""

from pathlib import Path

from reports.base_report import ReportWriter

_MAX_HEADER_CHARS = 40
_MAX_CELL_CHARS = 60


class PdfReport(ReportWriter):

    extension = ".pdf"

    def write_table(self, headers, rows, output_path):

        try:
            from fpdf import FPDF
        except ImportError as error:
            raise ImportError(
                "PDF reports need the optional 'fpdf2' dependency - "
                "install it with: pip install fpdf2"
            ) from error

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pdf = FPDF(orientation="L")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        column_count = max(len(headers), 1)
        page_width = pdf.w - 2 * pdf.l_margin
        column_width = page_width / column_count

        pdf.set_font("Helvetica", style="B", size=9)
        for header in headers:
            pdf.cell(column_width, 8, str(header)[:_MAX_HEADER_CHARS], border=1)
        pdf.ln()

        pdf.set_font("Helvetica", size=8)
        for row in rows:
            for value in row:
                pdf.cell(column_width, 7, str(value)[:_MAX_CELL_CHARS], border=1)
            pdf.ln()

        pdf.output(str(output_path))

        return output_path
