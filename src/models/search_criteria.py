"""
Search Criteria

One condition in a search query. A search is a list of these,
AND-combined - see SearchService.search().
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SearchCriteria:

    field: str
    operator: str = "contains"
    value: Any = None

    def __str__(self):

        if self.operator in ("missing", "present"):
            return f"{self.field}:{self.operator}"

        return f"{self.field}:{self.operator}={self.value!r}"
