from metadata.metadata_repair import MetadataRepair
from models.author import Author
from models.book import Book


def test_suggests_stripped_title_for_by_clause():

    book = Book(id=2, title="The Maze of Bones by Rick Riordan")

    suggestions = MetadataRepair().suggest_for_book(book)

    assert len(suggestions) == 1
    assert suggestions[0].suggested_value == "The Maze of Bones"
    assert suggestions[0].field == "title"


def test_no_suggestion_for_clean_title():

    book = Book(id=1, title="Doctor Sleep")
    book.add_author(Author(name="Stephen King"))

    suggestions = MetadataRepair().suggest_for_book(book)

    assert suggestions == []


def test_flags_but_does_not_guess_when_title_is_author_name():

    book = Book(id=4, title="Taylor, Roger")
    book.add_author(Author(name="Taylor, Roger"))

    suggestions = MetadataRepair().suggest_for_book(book)

    assert len(suggestions) == 1
    assert suggestions[0].suggested_value == ""
    assert "cannot be suggested" in suggestions[0].reason


def test_suggest_for_library_aggregates_all_books():

    clean = Book(id=1, title="Doctor Sleep")
    messy = Book(id=2, title="The Maze of Bones by Rick Riordan")

    suggestions = MetadataRepair().suggest_for_library([clean, messy])

    assert len(suggestions) == 1
    assert suggestions[0].book_id == 2
