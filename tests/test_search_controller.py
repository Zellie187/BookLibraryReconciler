import pytest

from controllers.search_controller import SearchController


@pytest.fixture
def controller():

    return SearchController(search_service=None)


def test_parse_simple_field_value(controller):

    criteria = controller.parse_term("author=King")

    assert criteria.field == "author"
    assert criteria.operator == "contains"
    assert criteria.value == "King"


def test_parse_field_mode_value(controller):

    criteria = controller.parse_term("series:exact=Dark Tower")

    assert criteria.field == "series"
    assert criteria.operator == "exact"
    assert criteria.value == "Dark Tower"


def test_parse_missing_shorthand(controller):

    criteria = controller.parse_term("isbn:missing")

    assert criteria.field == "isbn"
    assert criteria.operator == "missing"
    assert criteria.value is None


def test_parse_present_shorthand(controller):

    criteria = controller.parse_term("has_cover:present")

    assert criteria.field == "has_cover"
    assert criteria.operator == "present"


@pytest.mark.parametrize(
    "symbol,operator",
    [(">=", "gte"), ("<=", "lte"), (">", "gt"), ("<", "lt")],
)
def test_parse_numeric_comparisons(controller, symbol, operator):

    criteria = controller.parse_term(f"rating{symbol}4")

    assert criteria.field == "rating"
    assert criteria.operator == operator
    assert criteria.value == "4"


def test_numeric_field_without_mode_defaults_to_eq(controller):

    criteria = controller.parse_term("rating=4")

    assert criteria.field == "rating"
    assert criteria.operator == "eq"
    assert criteria.value == "4"


@pytest.mark.parametrize(
    "alias,field,operator",
    [
        ("missing-isbn", "isbn", "missing"),
        ("missing-cover", "has_cover", "missing"),
        ("has-cover", "has_cover", "present"),
        ("missing-series", "series", "missing"),
        ("missing-description", "comments", "missing"),
    ],
)
def test_aliases_resolve_to_full_terms(controller, alias, field, operator):

    criteria = controller.parse_term(alias)

    assert criteria.field == field
    assert criteria.operator == operator


def test_colon_in_value_does_not_confuse_the_parser(controller):

    criteria = controller.parse_term(r"path=C:\Books\Doctor Sleep.epub")

    assert criteria.field == "path"
    assert criteria.operator == "contains"
    assert criteria.value == r"C:\Books\Doctor Sleep.epub"


def test_unparseable_term_raises_value_error(controller):

    with pytest.raises(ValueError):
        controller.parse_term("just some text")


def test_parse_terms_returns_a_list(controller):

    criteria = controller.parse_terms(["author=King", "isbn:missing"])

    assert len(criteria) == 2
    assert criteria[0].field == "author"
    assert criteria[1].field == "isbn"


def test_search_delegates_to_search_service():

    class FakeSearchService:

        def __init__(self):
            self.called_with = None

        def search(self, criteria_list, sort_by, descending, limit, books):
            self.called_with = (criteria_list, sort_by, descending, limit, books)
            return ["fake-result"]

    fake_service = FakeSearchService()
    controller = SearchController(fake_service)

    results = controller.search(["author=King"], sort_by="title", descending=True, limit=5)

    assert results == ["fake-result"]

    criteria_list, sort_by, descending, limit, books = fake_service.called_with
    assert len(criteria_list) == 1
    assert criteria_list[0].field == "author"
    assert sort_by == "title"
    assert descending is True
    assert limit == 5
    assert books is None
