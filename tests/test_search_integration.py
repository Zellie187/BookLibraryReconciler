from controllers.search_controller import SearchController
from repositories.book_repository import BookRepository
from services.search_service import SearchService


def test_search_end_to_end_against_a_real_database(database_manager):

    repository = BookRepository(database_manager)
    service = SearchService(repository)
    controller = SearchController(service)

    results = controller.search(["author=King", "isbn:present"])

    assert [book.id for book in results] == [1]


def test_search_last_modified_is_populated_from_the_database(database_manager):

    repository = BookRepository(database_manager)
    books = repository.get_books()

    book = next(book for book in books if book.id == 1)

    assert book.last_modified != ""
