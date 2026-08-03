from PySide6.QtCore import Qt

from gui.book_table_model import COLUMNS, BookTableModel
from models.author import Author
from models.book import Book


def make_book(book_id=1, title="Doctor Sleep", isbn="", has_cover=False, rating=0):

    book = Book(id=book_id, title=title, isbn=isbn, has_cover=has_cover, rating=rating)
    book.add_author(Author(name="Stephen King"))

    return book


def test_row_and_column_counts(qt_app):

    model = BookTableModel([make_book(), make_book(book_id=2)])

    assert model.rowCount() == 2
    assert model.columnCount() == len(COLUMNS)


def test_header_data_matches_columns(qt_app):

    model = BookTableModel()

    for column, label in enumerate(COLUMNS):
        assert model.headerData(column, Qt.Orientation.Horizontal) == label


def test_header_data_ignores_vertical_orientation(qt_app):

    model = BookTableModel()

    assert model.headerData(0, Qt.Orientation.Vertical) is None


def test_data_returns_expected_fields_per_column(qt_app):

    book = make_book(book_id=7, title="The Shining", isbn="9780307743657", has_cover=True, rating=5)
    model = BookTableModel([book])

    values = [model.data(model.index(0, column)) for column in range(len(COLUMNS))]

    assert values == [7, "The Shining", "Stephen King", "", 5, "9780307743657", "Yes"]


def test_data_shows_dash_for_missing_isbn_and_no_for_missing_cover(qt_app):

    book = make_book(isbn="", has_cover=False)
    model = BookTableModel([book])

    assert model.data(model.index(0, COLUMNS.index("ISBN"))) == "-"
    assert model.data(model.index(0, COLUMNS.index("Cover"))) == "No"


def test_data_returns_none_for_invalid_index(qt_app):

    model = BookTableModel([make_book()])

    assert model.data(model.index(5, 0)) is None


def test_set_books_replaces_contents_and_resets_model(qt_app):

    model = BookTableModel([make_book(book_id=1)])
    model.set_books([make_book(book_id=2), make_book(book_id=3)])

    assert model.rowCount() == 2
    assert model.book_at(0).id == 2
    assert model.book_at(1).id == 3


def test_book_at_returns_none_for_out_of_range_row(qt_app):

    model = BookTableModel([make_book()])

    assert model.book_at(-1) is None
    assert model.book_at(99) is None
