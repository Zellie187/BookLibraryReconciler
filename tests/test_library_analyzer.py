from analyzers.library_analyzer import LibraryAnalyzer
from repositories.book_repository import BookRepository


def test_analyzer_stats(database_manager):

    books = BookRepository(database_manager).get_books()

    analyzer = LibraryAnalyzer(books)

    assert analyzer.total_books() == 2
    assert analyzer.unique_authors() == 1
    assert analyzer.unique_series() == 1
    assert analyzer.books_missing_isbn() == 1
    assert analyzer.books_missing_series() == 1
    assert analyzer.books_missing_comments() == 1
    assert analyzer.books_missing_cover() == 1
    assert analyzer.top_authors(limit=1) == [("Stephen King", 1)]
