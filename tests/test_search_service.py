import pytest

from models.author import Author
from models.book import Book
from models.search_criteria import SearchCriteria
from models.series import Series
from services.search_service import SearchService


def make_library():

    doctor_sleep = Book(
        id=1,
        title="Doctor Sleep",
        title_sort="Doctor Sleep",
        isbn="9781501144525",
        rating=4,
        has_cover=True,
        languages=["eng"],
        tags=["Horror"],
        formats=["EPUB", "PDF"],
        timestamp="2020-01-01",
        last_modified="2020-06-01",
        series=Series(name="The Shining"),
        series_index=2.0,
        size=1000,
    )
    doctor_sleep.add_author(Author(name="Stephen King", sort="King, Stephen"))

    gunslinger = Book(
        id=2,
        title="The Gunslinger",
        title_sort="Gunslinger, The",
        rating=0,
        has_cover=False,
        languages=[],
        tags=[],
        formats=["MOBI"],
        timestamp="2019-01-01",
        last_modified="2019-01-01",
        series=Series(name="Dark Tower"),
        series_index=1.0,
        size=500,
    )
    gunslinger.add_author(Author(name="Stephen King", sort="King, Stephen"))

    riordan = Book(
        id=3,
        title="The Maze of Bones by Rick Riordan",
        title_sort="Maze of Bones",
        rating=0,
        has_cover=False,
        timestamp="2021-01-01",
        last_modified="2021-01-01",
        size=200,
    )

    return [doctor_sleep, gunslinger, riordan]


@pytest.fixture
def library():

    return make_library()


def search(library, **criteria_kwargs):

    service = SearchService(book_repository=None)
    criteria = SearchCriteria(**criteria_kwargs)

    return service.search(criteria_list=[criteria], books=library)


def test_contains_match_on_title(library):

    results = search(library, field="title", operator="contains", value="gunslinger")

    assert [book.id for book in results] == [2]


def test_exact_match_is_case_insensitive_but_whole_string(library):

    results = search(library, field="title", operator="exact", value="doctor sleep")

    assert [book.id for book in results] == [1]


def test_author_field_checks_every_author(library):

    results = search(library, field="author", operator="contains", value="king")

    assert {book.id for book in results} == {1, 2}


def test_missing_series_matches_book_without_series(library):

    results = search(library, field="series", operator="missing")

    assert [book.id for book in results] == [3]


def test_present_isbn_matches_only_books_with_isbn(library):

    results = search(library, field="isbn", operator="present")

    assert [book.id for book in results] == [1]


def test_missing_isbn_matches_books_without_isbn(library):

    results = search(library, field="isbn", operator="missing")

    assert {book.id for book in results} == {2, 3}


def test_has_cover_eq_true(library):

    results = search(library, field="has_cover", operator="eq", value=1)

    assert [book.id for book in results] == [1]


def test_rating_numeric_gte(library):

    results = search(library, field="rating", operator="gte", value=4)

    assert [book.id for book in results] == [1]


def test_starts_with_and_ends_with(library):

    starts = search(library, field="title", operator="starts_with", value="the")
    ends = search(library, field="title", operator="ends_with", value="riordan")

    assert {book.id for book in starts} == {2, 3}
    assert [book.id for book in ends] == [3]


def test_regex_match(library):

    results = search(library, field="title", operator="regex", value=r"^The Maze")

    assert [book.id for book in results] == [3]


def test_invalid_regex_raises_value_error(library):

    service = SearchService(book_repository=None)
    criteria = SearchCriteria(field="title", operator="regex", value="(unclosed")

    with pytest.raises(ValueError):
        service.search(criteria_list=[criteria], books=library)


def test_fuzzy_match(library):

    results = search(library, field="title", operator="fuzzy", value="doctor sleap")

    assert [book.id for book in results] == [1]


def test_unknown_field_raises_value_error(library):

    service = SearchService(book_repository=None)
    criteria = SearchCriteria(field="not_a_real_field", operator="contains", value="x")

    with pytest.raises(ValueError):
        service.search(criteria_list=[criteria], books=library)


def test_unknown_operator_raises_value_error(library):

    service = SearchService(book_repository=None)
    criteria = SearchCriteria(field="title", operator="not_a_real_operator", value="x")

    with pytest.raises(ValueError):
        service.search(criteria_list=[criteria], books=library)


def test_multiple_criteria_are_and_combined(library):

    service = SearchService(book_repository=None)
    criteria = [
        SearchCriteria(field="author", operator="contains", value="king"),
        SearchCriteria(field="isbn", operator="present"),
    ]

    results = service.search(criteria_list=criteria, books=library)

    assert [book.id for book in results] == [1]


def test_sort_by_series_orders_by_name_then_index(library):

    service = SearchService(book_repository=None)

    results = service.search(criteria_list=[], sort_by="series", books=library)

    series_names = [book.series_name for book in results]
    assert series_names == ["", "Dark Tower", "The Shining"]


def test_sort_descending(library):

    service = SearchService(book_repository=None)

    results = service.search(criteria_list=[], sort_by="rating", descending=True, books=library)

    assert [book.id for book in results] == [1, 2, 3]


def test_limit_truncates_results(library):

    service = SearchService(book_repository=None)

    results = service.search(criteria_list=[], limit=1, books=library)

    assert len(results) == 1


def test_unknown_sort_field_raises_value_error(library):

    service = SearchService(book_repository=None)

    with pytest.raises(ValueError):
        service.search(criteria_list=[], sort_by="not_a_real_sort_field", books=library)


def test_no_criteria_returns_everything(library):

    service = SearchService(book_repository=None)

    results = service.search(criteria_list=[], books=library)

    assert len(results) == len(library)
