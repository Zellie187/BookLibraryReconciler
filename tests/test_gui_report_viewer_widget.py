import pytest

from gui.report_viewer_widget import generate_report_text
from models.author import Author
from models.book import Book
from models.series import Series


class FakeLibraryService:

    def __init__(self, books, author_records=None):

        self.books = books
        self.author_records = author_records or []

    def get_all_books(self):

        return self.books

    def get_all_author_records(self):

        return self.author_records


def make_book(
    book_id=1,
    title="Title",
    isbn="",
    has_cover=False,
    comments="",
    author_name="Author",
    series=None,
    size=0,
):

    book = Book(
        id=book_id,
        title=title,
        isbn=isbn,
        has_cover=has_cover,
        comments=comments,
        series=series,
        size=size,
    )

    if author_name:
        book.add_author(Author(name=author_name))

    return book


def test_unknown_report_type_raises_value_error():

    with pytest.raises(ValueError):
        generate_report_text("nonsense", FakeLibraryService([]))


def test_health_report_shows_average_score_and_worst_books():

    books = [make_book(book_id=1, isbn="", has_cover=False, comments="")]

    text = generate_report_text("health", FakeLibraryService(books))

    assert "Average Metadata Health Score" in text
    assert "#1" in text
    assert "missing:" in text


def test_duplicates_report_shows_group_counts():

    books = [
        make_book(book_id=1, isbn="9780307743657"),
        make_book(book_id=2, isbn="9780307743657"),
    ]

    text = generate_report_text("duplicates", FakeLibraryService(books))

    assert "ISBN duplicate groups   : 1" in text
    assert "books [1, 2]" in text


def test_duplicates_report_with_no_duplicates_shows_zero_counts():

    books = [make_book(book_id=1), make_book(book_id=2, title="Something else entirely")]

    text = generate_report_text("duplicates", FakeLibraryService(books))

    assert "ISBN duplicate groups   : 0" in text
    assert "Title duplicate groups  : 0" in text


def test_series_report_shows_issue_count():

    text = generate_report_text("series", FakeLibraryService([make_book()]))

    assert "Series order issues : 0" in text


def test_statistics_report_shows_totals_and_breakdowns():

    books = [
        make_book(
            book_id=1, author_name="Stephen King", series=Series(name="Dark Tower"), size=1000
        ),
        make_book(
            book_id=2, author_name="Stephen King", series=Series(name="Dark Tower"), size=2000
        ),
    ]

    text = generate_report_text("statistics", FakeLibraryService(books))

    assert "Total books : 2" in text
    assert "Stephen King: 2" in text
    assert "Dark Tower: 2" in text


def test_limit_controls_how_many_worst_books_are_shown_in_health_report():

    books = [
        make_book(book_id=index, isbn="", has_cover=False, comments="") for index in range(1, 6)
    ]

    text = generate_report_text("health", FakeLibraryService(books), limit=2)

    assert text.count("missing:") == 2
