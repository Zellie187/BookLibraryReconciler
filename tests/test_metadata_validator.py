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


def test_flags_empty_title():

    book = Book(id=3, title="   ")

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "empty_title" for issue in report.issues)


def test_flags_series_index_zero():

    book = Book(id=5, title="Something", series=Series(name="A Series"), series_index=0)

    report = MetadataValidator().validate_book(book)

    assert any(issue.code == "series_index_zero" for issue in report.issues)


def test_books_with_issues_filters_clean_books():

    clean = Book(id=1, title="Doctor Sleep")
    clean.add_author(Author(name="Stephen King"))

    messy = Book(id=2, title="The Maze of Bones by Rick Riordan")

    reports = MetadataValidator().books_with_issues([clean, messy])

    assert len(reports) == 1
    assert reports[0].book_id == 2
