from analyzers.library_statistics import LibraryStatistics
from models.author import Author
from models.book import Book
from models.series import Series


def make_book(book_id, title, author_name=None, series_name=None, language=None, pubdate="", size=0):

    book = Book(id=book_id, title=title, pubdate=pubdate, size=size)

    if author_name:
        book.add_author(Author(name=author_name))

    if series_name:
        book.series = Series(name=series_name)

    if language:
        book.languages = [language]

    return book


def test_books_per_author_counts_and_sorts_descending():

    books = [
        make_book(1, "A", author_name="Stephen King"),
        make_book(2, "B", author_name="Stephen King"),
        make_book(3, "C", author_name="Terry Pratchett"),
    ]

    result = LibraryStatistics(books).books_per_author()

    assert result[0] == ("Stephen King", 2)
    assert result[1] == ("Terry Pratchett", 1)


def test_books_per_series_ignores_books_without_a_series():

    books = [make_book(1, "A", series_name="Dark Tower"), make_book(2, "B")]

    result = LibraryStatistics(books).books_per_series()

    assert result == [("Dark Tower", 1)]


def test_books_per_language():

    books = [make_book(1, "A", language="eng"), make_book(2, "B", language="eng"), make_book(3, "C", language="fra")]

    result = LibraryStatistics(books).books_per_language()

    assert ("eng", 2) in result
    assert ("fra", 1) in result


def test_books_per_year_excludes_the_calibre_unknown_sentinel():

    books = [
        make_book(1, "A", pubdate="2020-01-01 00:00:00+00:00"),
        make_book(2, "B", pubdate="0101-01-01 00:00:00+00:00"),
        make_book(3, "C", pubdate=""),
    ]

    result = LibraryStatistics(books).books_per_year()

    assert result == [("2020", 1)]


def test_largest_books_sorted_descending_by_size():

    books = [make_book(1, "Small", size=100), make_book(2, "Big", size=5000), make_book(3, "Medium", size=1000)]

    result = LibraryStatistics(books).largest_books(limit=2)

    assert [book.title for book in result] == ["Big", "Medium"]


def test_smallest_books_excludes_zero_size_and_sorts_ascending():

    books = [
        make_book(1, "NoFormat", size=0),
        make_book(2, "Small", size=100),
        make_book(3, "Big", size=5000),
    ]

    result = LibraryStatistics(books).smallest_books(limit=5)

    assert [book.title for book in result] == ["Small", "Big"]


def test_empty_library_produces_empty_results():

    stats = LibraryStatistics([])

    assert stats.books_per_author() == []
    assert stats.books_per_series() == []
    assert stats.books_per_language() == []
    assert stats.books_per_year() == []
    assert stats.largest_books() == []
    assert stats.smallest_books() == []
