"""
Search Controller

Parses the CLI's small search query syntax into SearchCriteria and
delegates to SearchService. This is the only place that understands
query text - SearchService only ever sees structured SearchCriteria.

Term syntax (each term is one AND-combined condition):

    field=value              contains match (default)
    field:mode=value         mode is one of exact/contains/starts_with/
                              ends_with/regex/fuzzy
    field:missing             field is empty/absent
    field:present              field has a value
    field>=value / field<=value / field>value / field<value
                              numeric comparison (e.g. rating>=4)

Plus convenience aliases for the "Missing ISBN" / "Has Cover" style
filters from the spec (see ALIASES below).
"""

from models.search_criteria import SearchCriteria

ALIASES = {
    "missing-isbn": "isbn:missing",
    "missing-cover": "has_cover:missing",
    "has-cover": "has_cover:present",
    "missing-series": "series:missing",
    "missing-description": "comments:missing",
    "missing-publisher": "publisher:missing",
    "missing-language": "language:missing",
    "missing-tags": "tag:missing",
    "missing-rating": "rating:missing",
}

NUMERIC_FIELDS = {"rating"}

NUMERIC_SYMBOLS = (
    (">=", "gte"),
    ("<=", "lte"),
    (">", "gt"),
    ("<", "lt"),
)


class SearchController:

    def __init__(self, search_service):

        self.search_service = search_service

    # ---------------------------------------------------------

    def parse_term(self, term):

        term = ALIASES.get(term, term)

        if ":" in term and "=" not in term:
            field, mode = term.split(":", 1)
            return SearchCriteria(field=field.strip(), operator=mode.strip())

        for symbol, operator in NUMERIC_SYMBOLS:
            if symbol in term:
                field, value = term.split(symbol, 1)
                return SearchCriteria(field=field.strip(), operator=operator, value=value.strip())

        if ":" in term and "=" in term and term.index(":") < term.index("="):
            field_and_mode, value = term.split("=", 1)
            field, mode = field_and_mode.split(":", 1)
            return SearchCriteria(field=field.strip(), operator=mode.strip(), value=value.strip())

        if "=" in term:
            field, value = term.split("=", 1)
            field = field.strip()
            operator = "eq" if field in NUMERIC_FIELDS else "contains"
            return SearchCriteria(field=field, operator=operator, value=value.strip())

        raise ValueError(
            f"Could not parse search term: {term!r} "
            "(expected field=value, field:mode=value, field:missing, or field>=value)"
        )

    # ---------------------------------------------------------

    def parse_terms(self, terms):

        return [self.parse_term(term) for term in terms]

    # ---------------------------------------------------------

    def search(self, terms=None, sort_by=None, descending=False, limit=None, books=None):

        criteria = self.parse_terms(terms or [])

        return self.search_service.search(
            criteria_list=criteria,
            sort_by=sort_by,
            descending=descending,
            limit=limit,
            books=books,
        )
