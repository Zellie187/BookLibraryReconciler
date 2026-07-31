from metadata.metadata_validator import MetadataValidator
from models.author import Author
from models.book import Book
from models.series import Series


def test_clean_book_has_no_issues():

    book = Book(id=1, title="Doctor Sleep")
    book.add_author(Author(name="Stephen King", sort="King, Stephen"))

    report = MetadataValidator().validate_book(book)

    assert report.is_clean is True


def test_flags_title_matching_author_name():

    book = Book(id=4, title="Taylor, Roger")
    book.add_author(Author(name="Taylor, Roger", sort="Taylor, Roger"))

    report = MetadataValidator().validate_book(book)

    assert not report.is_clean
    assert any(issue.code == "title_matches_author" for issue in report.issues)


def test_flags_by_clause_even_without_linked_author():

    book = Book(id=2, title="The Maze of Bones by Rick Riordan")

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "title_contains_by_clause" for issue in report.issues)


def test_does_not_flag_a_real_title_ending_in_by_and_a_single_word():

    # Regression: "Married by Morning" (Lisa Kleypas) and "Dexter by
    # Design" (Jeff Lindsay) are real titles, not author-echoed ones -
    # the by-clause pattern must require 2+ capitalized words after
    # "by" or these get misidentified as "Title by Author".
    for title in ("Married by Morning", "Dexter by Design"):

        book = Book(id=7, title=title)

        report = MetadataValidator().validate_book(book)

        assert not any(issue.code == "title_contains_by_clause" for issue in report.issues), title


def test_flags_empty_title():

    book = Book(id=3, title="   ")

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "empty_title" for issue in report.issues)


def test_flags_series_index_zero():

    book = Book(id=5, title="Something", series=Series(name="A Series"), series_index=0)

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "series_index_zero" for issue in report.issues)


def test_flags_invalid_isbn():

    book = Book(id=6, title="Something", isbn="1234567890")

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "invalid_isbn" for issue in report.issues)


def test_valid_isbn_does_not_flag():

    book = Book(id=6, title="Something", isbn="978-0-306-40615-7")

    report = MetadataValidator().validate_book(book)

    assert not any(issue.code == "invalid_isbn" for issue in report.issues)


def test_books_with_issues_filters_clean_books():

    clean = Book(id=1, title="Doctor Sleep")
    clean.add_author(Author(name="Stephen King"))

    messy = Book(id=2, title="The Maze of Bones by Rick Riordan")

    reports = MetadataValidator().books_with_issues([clean, messy])

    assert len(reports) == 1
    assert reports[0].book_id == 2
