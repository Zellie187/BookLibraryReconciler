"""
Search Service

Filters and sorts a library's books against a list of SearchCriteria
(AND-combined). Operates on plain Book objects in memory, the same way
LibraryAnalyzer/MetadataEngine/FileOrganizer do - for a library sized
in the thousands this is simpler and just as fast as building a
dynamic SQL query across nine joined tables, and it means every field
(including ones assembled from multiple tables, like authors or tags)
is searched the same way.
"""

import re
from difflib import SequenceMatcher

FUZZY_THRESHOLD = 0.6


# ---------------------------------------------------------------------------
# Field extraction: every field is exposed as a list of raw values, so
# multi-valued fields (authors, tags, languages, formats) and
# single-valued fields (title, isbn, ...) can be matched the same way.
# ---------------------------------------------------------------------------


def _series_values(book):

    return [book.series.name] if book.series is not None else []


FIELD_EXTRACTORS = {
    "title": lambda book: [book.title],
    "author": lambda book: [author.name for author in book.authors],
    "isbn": lambda book: [book.isbn],
    "uuid": lambda book: [book.uuid],
    "series": _series_values,
    "publisher": lambda book: [book.publisher],
    "language": lambda book: list(book.languages),
    "tag": lambda book: list(book.tags),
    "format": lambda book: list(book.formats),
    "comments": lambda book: [book.comments],
    "path": lambda book: [book.path],
    "date_added": lambda book: [book.timestamp],
    "last_modified": lambda book: [book.last_modified],
    "rating": lambda book: [book.rating],
    "has_cover": lambda book: [book.has_cover],
}


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------


def _is_empty(value):

    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, bool):
        return value is False
    if isinstance(value, (int, float)):
        return value == 0

    return False


TEXT_OPERATORS = {
    "exact": lambda text, needle: text == needle,
    "contains": lambda text, needle: needle in text,
    "starts_with": lambda text, needle: text.startswith(needle),
    "ends_with": lambda text, needle: text.endswith(needle),
}

NUMERIC_OPERATORS = {
    "eq": lambda a, b: a == b,
    "gte": lambda a, b: a >= b,
    "lte": lambda a, b: a <= b,
    "gt": lambda a, b: a > b,
    "lt": lambda a, b: a < b,
}


def _text_match(raw_value, search_value, comparator):

    text = str(raw_value or "").lower()
    needle = str(search_value or "").lower()

    return comparator(text, needle)


def _regex_match(raw_value, pattern):

    try:
        return re.search(pattern, str(raw_value or ""), re.IGNORECASE) is not None
    except re.error as error:
        raise ValueError(f"Invalid regular expression {pattern!r}: {error}") from error


def _fuzzy_match(raw_value, search_value, threshold=FUZZY_THRESHOLD):

    text = str(raw_value or "").lower()
    needle = str(search_value or "").lower()

    if not needle:
        return False

    return SequenceMatcher(None, text, needle).ratio() >= threshold


def _numeric_match(raw_value, search_value, comparator):

    try:
        return comparator(float(raw_value or 0), float(search_value))
    except (TypeError, ValueError):
        return False


def _matches_value(raw_value, criteria):

    operator = criteria.operator

    if operator == "missing":
        return _is_empty(raw_value)
    if operator == "present":
        return not _is_empty(raw_value)
    if operator == "regex":
        return _regex_match(raw_value, criteria.value)
    if operator == "fuzzy":
        return _fuzzy_match(raw_value, criteria.value)
    if operator in NUMERIC_OPERATORS:
        return _numeric_match(raw_value, criteria.value, NUMERIC_OPERATORS[operator])
    if operator in TEXT_OPERATORS:
        return _text_match(raw_value, criteria.value, TEXT_OPERATORS[operator])

    raise ValueError(f"Unknown search operator: {operator!r}")


def matches(book, criteria):

    extractor = FIELD_EXTRACTORS.get(criteria.field)

    if extractor is None:
        raise ValueError(f"Unknown search field: {criteria.field!r}")

    values = extractor(book)

    if not values and criteria.operator in ("missing", "present"):
        return criteria.operator == "missing"

    return any(_matches_value(value, criteria) for value in values)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------


def _author_sort_key(book):

    if not book.authors:
        return ""

    first_author = book.authors[0]

    return (first_author.sort or first_author.name or "").lower()


def _series_sort_key(book):

    if book.series is None:
        return ("", 0.0)

    return (book.series.name.lower(), book.series_index)


SORT_KEYS = {
    "title": lambda book: (book.title_sort or book.title or "").lower(),
    "author": _author_sort_key,
    "series": _series_sort_key,
    "rating": lambda book: book.rating,
    "date_added": lambda book: book.timestamp or "",
    "last_modified": lambda book: book.last_modified or "",
    "size": lambda book: book.size,
}


class SearchService:

    def __init__(self, book_repository):

        self.book_repository = book_repository

    # ---------------------------------------------------------

    def search(self, criteria_list=None, sort_by=None, descending=False, limit=None, books=None):

        if books is None:
            books = self.book_repository.get_books(limit=None)

        criteria_list = criteria_list or []

        results = [
            book for book in books if all(matches(book, criteria) for criteria in criteria_list)
        ]

        if sort_by:

            sort_key = SORT_KEYS.get(sort_by)

            if sort_key is None:
                raise ValueError(f"Unknown sort field: {sort_by!r}")

            results.sort(key=sort_key, reverse=descending)

        if limit is not None:
            results = results[:limit]

        return results
