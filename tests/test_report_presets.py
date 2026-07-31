import json

from metadata.author_duplicate_finder import AuthorDuplicateGroup
from metadata.duplicate_detector import DuplicateGroup
from metadata.series_order import SeriesOrderIssue
from models.author import Author
from models.book import Book
from reports.csv_report import CsvReport
from reports.json_report import JsonReport


def make_library():

    complete = Book(
        id=1,
        title="Doctor Sleep",
        isbn="9780306406157",
        comments="A book.",
        publisher="Scribner",
        has_cover=True,
        languages=["eng"],
        formats=["EPUB"],
        size=1000,
    )
    complete.add_author(Author(name="Stephen King"))

    incomplete = Book(id=2, title="Mystery Book", size=200)

    return [complete, incomplete]


def test_write_library_health_summary(tmp_path):

    books = make_library()

    output_path = CsvReport().write_library_health_summary(books, tmp_path / "health.csv")

    content = output_path.read_text(encoding="utf-8")

    assert "metric,value" in content
    assert "total_books" in content
    assert "2" in content
    assert "missing_isbn" in content


def test_write_duplicate_report_includes_all_three_types(tmp_path):

    isbn_groups = [DuplicateGroup(reason="isbn=123", book_ids=[1, 2])]
    title_groups = [DuplicateGroup(reason="similar title, same author", book_ids=[3, 4])]
    author_groups = [
        AuthorDuplicateGroup(canonical_author_id=1, duplicate_author_ids=[2], names=["A", "B"])
    ]

    output_path = JsonReport().write_duplicate_report(
        isbn_groups, title_groups, tmp_path / "dupes.json", author_groups=author_groups
    )

    records = json.loads(output_path.read_text(encoding="utf-8"))

    types = {record["type"] for record in records}
    assert types == {"isbn", "title", "author"}


def test_write_duplicate_report_without_author_groups(tmp_path):

    isbn_groups = [DuplicateGroup(reason="isbn=123", book_ids=[1, 2])]

    output_path = JsonReport().write_duplicate_report(isbn_groups, [], tmp_path / "dupes.json")

    records = json.loads(output_path.read_text(encoding="utf-8"))

    assert len(records) == 1
    assert records[0]["type"] == "isbn"


def test_write_series_report(tmp_path):

    issues = [SeriesOrderIssue(series_name="Dark Tower", issue_type="gap", detail="missing 3")]

    output_path = CsvReport().write_series_report(issues, tmp_path / "series.csv")

    content = output_path.read_text(encoding="utf-8")

    assert "Dark Tower" in content
    assert "gap" in content


def test_write_statistics_report_covers_every_breakdown(tmp_path):

    books = make_library()

    output_path = JsonReport().write_statistics_report(books, tmp_path / "stats.json")

    records = json.loads(output_path.read_text(encoding="utf-8"))
    categories = {record["category"] for record in records}

    assert "books_per_author" in categories
    assert "largest_books" in categories
    assert "smallest_books" in categories
