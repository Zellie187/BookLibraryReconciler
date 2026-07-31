from repositories.book_repository import BookRepository


def test_get_book_count(database_manager):

    repository = BookRepository(database_manager)

    assert repository.get_book_count() == 2


def test_get_books_assembles_full_metadata(database_manager):

    repository = BookRepository(database_manager)

    books = repository.get_books()

    assert len(books) == 2

    book = next(book for book in books if book.id == 1)

    assert book.title == "Doctor Sleep"
    assert book.author_names == "Stephen King"
    assert book.isbn == "9781501144525"
    assert book.comments == "A haunted boy grows up."
    assert book.publisher == "Scribner"
    assert book.rating == 4
    assert book.languages == ["eng"]
    assert book.tags == ["Horror"]
    assert book.series_name == "The Shining"
    assert book.has_cover is True
    assert [f.format for f in book.format_files] == ["EPUB"]
    assert book.size == 1000


def test_get_books_handles_missing_metadata(database_manager):

    repository = BookRepository(database_manager)

    books = repository.get_books()

    book = next(book for book in books if book.id == 2)

    assert book.author_names == "Unknown"
    assert book.isbn == ""
    assert book.comments == ""
    assert book.publisher == ""
    assert book.rating == 0
    assert book.series is None


def test_get_books_respects_limit(database_manager):

    repository = BookRepository(database_manager)

    books = repository.get_books(limit=1)

    assert len(books) == 1


def test_update_path(database_manager):

    repository = BookRepository(database_manager)

    repository.update_path(1, "Stephen King/Doctor Sleep")

    books = repository.get_books()
    book = next(book for book in books if book.id == 1)

    assert book.path == "Stephen King/Doctor Sleep"
