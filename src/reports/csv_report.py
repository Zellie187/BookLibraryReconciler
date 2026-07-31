"""
CSV Report Writer
"""

import csv
from pathlib import Path

from reports.base_report import ReportWriter


class CsvReport(ReportWriter):

    extension = ".csv"

    def write_table(self, headers, rows, output_path):

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:

            writer = csv.writer(csv_file)
            writer.writerow(headers)
            writer.writerows(rows)

        return output_path
