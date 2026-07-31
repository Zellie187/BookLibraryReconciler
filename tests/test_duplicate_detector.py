from metadata.duplicate_detector import DuplicateDetector
from models.author import Author
from models.book import Book


def make_book(book_id, title, author_name=None, author_sort=None, isbn=""):

    book = Book(id=book_id, title=title, isbn=isbn)

    if author_name:
        book.add_author(Author(name=author_name, sort=author_sort or author_name))

    return book


def test_finds_isbn_duplicates():

    books = [
        make_book(1, "Doctor Sleep", isbn="9780306406157"),
        make_book(2, "Doctor Sleep (reimport)", isbn="9780306406157"),
        make_book(3, "Unrelated", isbn="0306406152"),
    ]

    groups = DuplicateDetector().find_isbn_duplicates(books)

    assert len(groups) == 1
    assert set(groups[0].book_ids) == {1, 2}


def test_no_isbn_duplicates_when_all_unique():

    books = [make_book(1, "A", isbn="9780306406157"), make_book(2, "B", isbn="0306406152")]

    assert DuplicateDetector().find_isbn_duplicates(books) == []


def test_finds_exact_title_duplicates_for_same_author():

    books = [
        make_book(1, "Doctor Sleep", "Stephen King"),
        make_book(2, "Doctor Sleep", "Stephen King"),
        make_book(3, "The Gunslinger", "Stephen King"),
    ]

    groups = DuplicateDetector().find_title_duplicates(books)

    assert len(groups) == 1
    assert set(groups[0].book_ids) == {1, 2}


def test_same_title_different_author_is_not_a_duplicate():

    books = [
        make_book(1, "Night Watch", "Terry Pratchett"),
        make_book(2, "Night Watch", "Sergei Lukyanenko"),
    ]

    assert DuplicateDetector().find_title_duplicates(books) == []


def test_excludes_titles_that_are_just_the_author_name():

    books = [
        make_book(1, "Taylor, Roger", "Taylor, Roger", author_sort="Taylor, Roger"),
        make_book(2, "Taylor, Roger", "Taylor, Roger", author_sort="Taylor, Roger"),
    ]

    assert DuplicateDetector().find_title_duplicates(books) == []


def test_excludes_author_name_echo_regardless_of_word_order_or_punctuation():

    books = [
        make_book(1, "Steve Berry", "Berry, Steve", author_sort="Berry, Steve"),
        make_book(2, "Berry Steve", "Berry, Steve", author_sort="Berry, Steve"),
    ]

    assert DuplicateDetector().find_title_duplicates(books) == []


def test_excludes_titles_that_differ_only_by_a_volume_number():

    books = [
        make_book(1, "Elminster 1 - Greenwood, Ed", "Ed Greenwood"),
        make_book(2, "Elminster 2 - Greenwood, Ed", "Ed Greenwood"),
        make_book(3, "042 - Maxwell Grant", "Maxwell Grant"),
        make_book(4, "043 - Maxwell Grant", "Maxwell Grant"),
    ]

    assert DuplicateDetector().find_title_duplicates(books) == []


def test_still_flags_identical_titles_with_a_trailing_reimport_marker():

    # Calibre appends "(1)", "(2)"... on re-import of the same title -
    # this is exactly the kind of real duplicate the detector should catch.
    books = [
        make_book(1, "Point Blank - Coulter, Catherine", "Catherine Coulter"),
        make_book(2, "Point Blank - Coulter, Catherine(1)", "Catherine Coulter"),
    ]

    groups = DuplicateDetector().find_title_duplicates(books)

    assert len(groups) == 1
    assert set(groups[0].book_ids) == {1, 2}


def test_books_with_no_author_are_still_compared_to_each_other():

    books = [make_book(1, "Mystery Book"), make_book(2, "Mystery Book")]

    groups = DuplicateDetector().find_title_duplicates(books)

    assert len(groups) == 1
    assert set(groups[0].book_ids) == {1, 2}


def test_custom_threshold_is_respected():

    books = [make_book(1, "Doctor Sleep", "Stephen King"), make_book(2, "Doctor Sleeq", "Stephen King")]

    assert DuplicateDetector().find_title_duplicates(books, threshold=0.99) == []
    assert len(DuplicateDetector().find_title_duplicates(books, threshold=0.8)) == 1
