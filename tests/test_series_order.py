from metadata.series_order import find_series_order_issues
from models.book import Book
from models.series import Series


def make_book(book_id, series_name, series_index):

    series = Series(name=series_name) if series_name is not None else None

    return Book(id=book_id, title=f"Book {book_id}", series=series, series_index=series_index)


def test_no_issues_for_clean_sequential_series():

    books = [make_book(1, "Dark Tower", 1), make_book(2, "Dark Tower", 2), make_book(3, "Dark Tower", 3)]

    assert find_series_order_issues(books) == []


def test_flags_duplicate_position():

    books = [make_book(1, "Dark Tower", 1), make_book(2, "Dark Tower", 1)]

    issues = find_series_order_issues(books)

    assert len(issues) == 1
    assert issues[0].issue_type == "duplicate_position"
    assert issues[0].series_name == "Dark Tower"


def test_flags_gap_in_whole_number_sequence():

    books = [make_book(1, "Dark Tower", 1), make_book(2, "Dark Tower", 2), make_book(3, "Dark Tower", 4)]

    issues = find_series_order_issues(books)

    assert len(issues) == 1
    assert issues[0].issue_type == "gap"
    assert "3" in issues[0].detail


def test_series_index_zero_is_ignored_not_a_duplicate():

    books = [make_book(1, "Dark Tower", 0), make_book(2, "Dark Tower", 0)]

    assert find_series_order_issues(books) == []


def test_fractional_index_counts_for_duplicates_but_not_gaps():

    books = [
        make_book(1, "Dark Tower", 1),
        make_book(2, "Dark Tower", 1.5),
        make_book(3, "Dark Tower", 2),
    ]

    # 1.5 is a legitimate between-volumes novella - no gap between 1 and 2.
    assert find_series_order_issues(books) == []

    duplicate_novella = make_book(4, "Dark Tower", 1.5)
    issues = find_series_order_issues(books + [duplicate_novella])

    assert len(issues) == 1
    assert issues[0].issue_type == "duplicate_position"


def test_books_without_a_series_are_ignored():

    books = [make_book(1, None, 0), make_book(2, None, 0)]

    assert find_series_order_issues(books) == []


def test_single_book_series_has_no_gap():

    books = [make_book(1, "Standalone Trilogy", 1)]

    assert find_series_order_issues(books) == []


def test_different_series_are_checked_independently():

    books = [
        make_book(1, "Dark Tower", 1),
        make_book(2, "Dark Tower", 3),
        make_book(3, "Discworld", 1),
        make_book(4, "Discworld", 2),
    ]

    issues = find_series_order_issues(books)

    assert len(issues) == 1
    assert issues[0].series_name == "Dark Tower"
    assert issues[0].issue_type == "gap"
