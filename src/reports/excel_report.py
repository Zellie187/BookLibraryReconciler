"""
Excel Report Writer

Needs the optional `openpyxl` dependency - only imported when this
class is actually instantiated to write a table, so every other report
format (and the rest of the app) works without it installed.
"""

from pathlib import Path

from reports.base_report import ReportWriter


class ExcelReport(ReportWriter):

    extension = ".xlsx"

    def write_table(self, headers, rows, output_path):

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
        except ImportError as error:
            raise ImportError(
                "Excel reports need the optional 'openpyxl' dependency - "
                "install it with: pip install openpyxl"
            ) from error

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Report"

        sheet.append(list(headers))

        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for row in rows:
            sheet.append(list(row))

        for column_cells in sheet.columns:

            longest_value = max(
                (len(str(cell.value)) for cell in column_cells if cell.value is not None),
                default=10,
            )
            sheet.column_dimensions[column_cells[0].column_letter].width = min(longest_value + 2, 60)

        workbook.save(output_path)

        return output_path
