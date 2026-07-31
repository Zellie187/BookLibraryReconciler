from models.author import Author
from models.book import Book
from models.series import Series


def test_book_author_names_defaults_to_unknown():

    book = Book(title="Untitled")

    assert book.author_names == "Unknown"


def test_book_author_names_joins_multiple_authors():

    book = Book(title="Good Omens")
    book.add_author(Author(name="Terry Pratchett"))
    book.add_author(Author(name="Neil Gaiman"))

    assert book.author_names == "Terry Pratchett, Neil Gaiman"


def test_book_series_name_empty_when_no_series():

    book = Book(title="Standalone")

    assert book.series_name == ""


def test_book_series_name_reflects_series():

    book = Book(title="Doctor Sleep", series=Series(name="The Shining"))

    assert book.series_name == "The Shining"


def test_book_str():

    book = Book(title="Doctor Sleep")
    book.add_author(Author(name="Stephen King"))

    assert str(book) == "Doctor Sleep - Stephen King"
