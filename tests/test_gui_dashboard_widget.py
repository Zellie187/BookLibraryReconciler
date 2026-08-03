from gui.dashboard_widget import compute_stats
from models.author import Author
from models.book import Book
from models.series import Series


def make_book(
    book_id=1,
    title="Title",
    isbn="",
    has_cover=False,
    comments="",
    author_name="Author",
    series=None,
):

    book = Book(
        id=book_id, title=title, isbn=isbn, has_cover=has_cover, comments=comments, series=series
    )

    if author_name:
        book.add_author(Author(name=author_name))

    return book


def stats_dict(books):

    return dict(compute_stats(books))


def test_total_books_and_unique_authors():

    books = [
        make_book(book_id=1, author_name="Stephen King"),
        make_book(book_id=2, author_name="Stephen King"),
        make_book(book_id=3, author_name="Jane Austen"),
    ]

    stats = stats_dict(books)

    assert stats["Total books"] == "3"
    assert stats["Unique authors"] == "2"


def test_unique_series_counts_distinct_series_only():

    books = [
        make_book(book_id=1, series=Series(name="Dark Tower")),
        make_book(book_id=2, series=Series(name="Dark Tower")),
        make_book(book_id=3, series=None),
    ]

    stats = stats_dict(books)

    assert stats["Unique series"] == "1"


def test_missing_field_counts():

    books = [
        make_book(book_id=1, isbn="", has_cover=False, comments=""),
        make_book(book_id=2, isbn="9780307743657", has_cover=True, comments="A book."),
    ]

    stats = stats_dict(books)

    assert stats["Missing ISBN"] == "1"
    assert stats["Missing cover"] == "1"
    assert stats["Missing description"] == "1"


def test_average_health_score_and_needing_attention_present():

    books = [make_book(book_id=1, isbn="", has_cover=False, comments="")]

    stats = stats_dict(books)

    assert stats["Average health score"].endswith("%")
    assert stats["Books needing attention"] == "1"


def test_empty_library_reports_zero_for_everything():

    stats = stats_dict([])

    assert stats["Total books"] == "0"
    assert stats["Average health score"] == "0%"
    assert stats["ISBN duplicate groups"] == "0"


def test_stats_come_back_as_label_value_pairs_in_a_stable_order():

    stats = compute_stats([make_book()])
    labels = [label for label, _ in stats]

    assert labels[0] == "Total books"
    assert "Average health score" in labels
    assert "Series order issues" in labels
