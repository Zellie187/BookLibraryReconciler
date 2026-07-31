"""
JSON Report Writer
"""

import json
from pathlib import Path

from reports.base_report import ReportWriter


class JsonReport(ReportWriter):

    extension = ".json"

    def write_table(self, headers, rows, output_path):

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = [dict(zip(headers, row)) for row in rows]

        output_path.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")

        return output_path
