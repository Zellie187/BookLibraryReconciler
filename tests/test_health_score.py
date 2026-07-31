from metadata.health_score import MetadataScorer
from repositories.book_repository import BookRepository


def test_complete_book_scores_100(database_manager):

    books = BookRepository(database_manager).get_books()
    book = next(book for book in books if book.id == 1)

    scorer = MetadataScorer()
    report = scorer.score_book(book)

    assert report.score == 100
    assert report.failed == []


def test_incomplete_book_reports_missing_fields(database_manager):

    books = BookRepository(database_manager).get_books()
    book = next(book for book in books if book.id == 2)

    scorer = MetadataScorer()
    report = scorer.score_book(book)

    assert report.score == 20
    assert set(report.failed) == {"isbn", "cover", "description", "author"}


def test_average_score(database_manager):

    books = BookRepository(database_manager).get_books()

    scorer = MetadataScorer()

    assert scorer.average_score(books) == 60


def test_average_score_empty_library():

    scorer = MetadataScorer()

    assert scorer.average_score([]) == 0
