"""
HTML Report Writer

Self-contained - no template engine dependency, just html.escape() and
an f-string.
"""

from html import escape
from pathlib import Path

from reports.base_report import ReportWriter

_PAGE_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>BookLibraryReconciler Report</title>
<style>
  body {{ font-family: sans-serif; margin: 2rem; color: #222; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
  th {{ background: #f0f0f0; }}
  tr:nth-child(even) {{ background: #fafafa; }}
</style>
</head>
<body>
<table>
<thead><tr>{header_html}</tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>
"""


class HtmlReport(ReportWriter):

    extension = ".html"

    def write_table(self, headers, rows, output_path):

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)

        rows_html = "\n".join(
            "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
            for row in rows
        )

        html = _PAGE_TEMPLATE.format(header_html=header_html, rows_html=rows_html)

        output_path.write_text(html, encoding="utf-8")

        return output_path
