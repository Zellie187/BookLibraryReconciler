import json

from metadata.metadata_score import HealthReport
from repair.file_organizer import FormatRename, OrganizePlan
from reports.csv_report import CsvReport
from reports.excel_report import ExcelReport
from reports.html_report import HtmlReport
from reports.json_report import JsonReport
from reports.pdf_report import PdfReport


def make_plan():

    return OrganizePlan(
        book_id=1,
        title="Doctor Sleep",
        author="Stephen King",
        current_path="Stephen King/Doctor Sleep (1)",
        proposed_path="Stephen King/Doctor Sleep",
        format_renames=[
            FormatRename(
                format="EPUB", old_name="Doctor Sleep - Stephen King", new_name="Doctor Sleep"
            )
        ],
    )


def make_health_report():

    report = HealthReport(book_id=1, title="Doctor Sleep")
    report.passed = ["title", "author"]
    report.failed = ["isbn", "cover", "description"]

    return report


def test_csv_report_writes_organize_plan(tmp_path):

    output_path = CsvReport().write_organize_plan([make_plan()], tmp_path / "plan.csv")

    content = output_path.read_text(encoding="utf-8")

    assert "book_id,title,author,current_path,proposed_path,format_renames" in content
    assert "Doctor Sleep - Stephen King -> Doctor Sleep" in content


def test_csv_report_writes_health_report(tmp_path):

    output_path = CsvReport().write_health_report([make_health_report()], tmp_path / "health.csv")

    content = output_path.read_text(encoding="utf-8")

    assert "book_id,title,score,failed_checks" in content
    assert "isbn, cover, description" in content


def test_json_report_writes_organize_plan(tmp_path):

    output_path = JsonReport().write_organize_plan([make_plan()], tmp_path / "plan.json")

    records = json.loads(output_path.read_text(encoding="utf-8"))

    assert records[0]["proposed_path"] == "Stephen King/Doctor Sleep"


def test_excel_report_writes_a_workbook(tmp_path):

    output_path = ExcelReport().write_organize_plan([make_plan()], tmp_path / "plan.xlsx")

    from openpyxl import load_workbook

    workbook = load_workbook(output_path)
    sheet = workbook.active

    header_row = [cell.value for cell in sheet[1]]
    assert header_row == [
        "book_id",
        "title",
        "author",
        "current_path",
        "proposed_path",
        "format_renames",
    ]
    assert sheet[1][0].font.bold is True

    data_row = [cell.value for cell in sheet[2]]
    assert data_row[0] == 1
    assert data_row[4] == "Stephen King/Doctor Sleep"


def test_html_report_writes_an_escaped_table(tmp_path):

    plan = make_plan()
    plan.title = "<script>alert(1)</script>"

    output_path = HtmlReport().write_organize_plan([plan], tmp_path / "plan.html")

    content = output_path.read_text(encoding="utf-8")

    assert "<table>" in content
    assert "<th>book_id</th>" in content
    assert "&lt;script&gt;" in content
    assert "<script>alert(1)</script>" not in content


def test_pdf_report_writes_a_real_pdf_file(tmp_path):

    output_path = PdfReport().write_organize_plan([make_plan()], tmp_path / "plan.pdf")

    content = output_path.read_bytes()

    assert output_path.exists()
    assert content.startswith(b"%PDF")
