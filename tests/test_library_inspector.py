from metadata.library_inspector import LibraryInspector
from models.author import Author
from models.book import Book
from models.series import Series


def make_book(book_id, title, author_name=None, isbn="", series_name=None, series_index=0):

    book = Book(
        id=book_id,
        title=title,
        isbn=isbn,
        series=Series(name=series_name) if series_name else None,
        series_index=series_index,
    )

    if author_name:
        book.add_author(Author(name=author_name, sort=author_name))

    return book


def test_inspect_combines_all_checks():

    books = [
        make_book(1, "Doctor Sleep", "Stephen King", isbn="9780306406157", series_name="The Shining", series_index=2),
        make_book(2, "Doctor Sleep", "Stephen King", isbn="9780306406157", series_name="The Shining", series_index=2),
    ]

    inspection = LibraryInspector().inspect(books)

    assert len(inspection.book_analyses) == 2
    assert len(inspection.isbn_duplicate_groups) == 1
    assert len(inspection.title_duplicate_groups) == 1
    assert len(inspection.series_order_issues) == 1
    assert inspection.series_order_issues[0].issue_type == "duplicate_position"


def test_books_needing_attention_property():

    clean = make_book(1, "Doctor Sleep", "Stephen King", isbn="9780306406157")
    clean.comments = "A book."
    clean.has_cover = True

    messy = make_book(2, "The Maze of Bones by Rick Riordan")

    inspection = LibraryInspector().inspect([clean, messy])

    assert [a.book_id for a in inspection.books_needing_attention] == [2]


def test_average_score_matches_scorer():

    books = [make_book(1, "A"), make_book(2, "B")]

    inspection = LibraryInspector().inspect(books)

    assert inspection.average_score == LibraryInspector().metadata_engine.scorer.average_score(books)


def test_empty_library_produces_empty_inspection():

    inspection = LibraryInspector().inspect([])

    assert inspection.book_analyses == []
    assert inspection.isbn_duplicate_groups == []
    assert inspection.title_duplicate_groups == []
    assert inspection.series_order_issues == []
    assert inspection.average_score == 0
