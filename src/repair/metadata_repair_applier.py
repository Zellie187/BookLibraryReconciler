"""
Metadata Repair Applier

Applies MetadataRepair suggestions that have a concrete suggested_value
- e.g. stripping a "by <author>" clause from a title. Suggestions with
no suggested_value (e.g. title_matches_author, where the real title is
genuinely unknown) are always skipped; there is nothing to apply.

One suggestion failing does not stop the rest, and is reported back
instead of raised - mirrors repair/organize_applier.py's pattern.
"""

import sqlite3
from dataclasses import dataclass

FIELD_WRITERS = {
    "title": lambda library_service, book_id, value: library_service.update_book_title(book_id, value),
}


@dataclass
class RepairApplyResult:

    book_id: int = 0
    field: str = ""
    applied_value: str = ""
    applied: bool = False
    error: str = ""


class MetadataRepairApplier:

    def __init__(self, library_service):

        self.library_service = library_service

    # ---------------------------------------------------------

    def apply(self, suggestions):

        return [self._apply_one(suggestion) for suggestion in suggestions]

    # ---------------------------------------------------------

    def _apply_one(self, suggestion):

        result = RepairApplyResult(book_id=suggestion.book_id, field=suggestion.field)

        if not suggestion.suggested_value:
            result.error = "No suggested value - needs manual review"
            return result

        writer = FIELD_WRITERS.get(suggestion.field)

        if writer is None:
            result.error = f"Don't know how to apply repairs to field {suggestion.field!r}"
            return result

        try:
            writer(self.library_service, suggestion.book_id, suggestion.suggested_value)
        except sqlite3.Error as error:
            result.error = f"Apply failed: {error}"
            return result

        result.applied = True
        result.applied_value = suggestion.suggested_value

        return result
