from metadata.metadata_engine import MetadataEngine
from models.author import Author
from models.book import Book


def test_analyze_book_combines_score_and_validation():

    book = Book(id=2, title="The Maze of Bones by Rick Riordan")

    analysis = MetadataEngine().analyze_book(book)

    assert analysis.book_id == 2
    assert analysis.score < 100
    assert any("by <author>" in issue for issue in analysis.issues)
    assert analysis.repair_suggestions[0].suggested_value == "The Maze of Bones"
    assert analysis.needs_attention is True


def test_complete_clean_book_does_not_need_attention():

    book = Book(id=1, title="Doctor Sleep", isbn="123", comments="A book.", has_cover=True)
    book.add_author(Author(name="Stephen King"))

    analysis = MetadataEngine().analyze_book(book)

    assert analysis.score == 100
    assert analysis.issues == []
    assert analysis.needs_attention is False


def test_books_needing_attention_filters_the_library():

    clean = Book(id=1, title="Doctor Sleep", isbn="123", comments="A book.", has_cover=True)
    clean.add_author(Author(name="Stephen King"))

    messy = Book(id=2, title="The Maze of Bones by Rick Riordan")

    engine = MetadataEngine()
    flagged = engine.books_needing_attention([clean, messy])

    assert len(flagged) == 1
    assert flagged[0].book_id == 2
