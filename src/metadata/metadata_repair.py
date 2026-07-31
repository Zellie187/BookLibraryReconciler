"""
Metadata Repair Suggestions

Suggests corrected field values for books the validator flagged.
Suggestions are never applied automatically - matching the project's
rule that every metadata change needs a human to approve it.
"""

from dataclasses import dataclass

from metadata.metadata_validator import BY_CLAUSE_PATTERN


@dataclass
class RepairSuggestion:

    book_id: int = 0
    field: str = ""
    current_value: str = ""
    suggested_value: str = ""
    reason: str = ""


class MetadataRepair:

    def suggest_for_book(self, book):

        suggestions = []
        title = book.title.strip()

        match = BY_CLAUSE_PATTERN.search(title)

        if match:

            cleaned = title[: match.start()].strip()

            if cleaned:
                suggestions.append(
                    RepairSuggestion(
                        book_id=book.id,
                        field="title",
                        current_value=book.title,
                        suggested_value=cleaned,
                        reason="Title appears to end with a 'by <author>' clause",
                    )
                )

        for author in book.authors:

            if author.name and title.lower() == author.name.lower():
                suggestions.append(
                    RepairSuggestion(
                        book_id=book.id,
                        field="title",
                        current_value=book.title,
                        suggested_value="",
                        reason=(
                            f"Title matches the author name ({author.name!r}); "
                            "the real title is unknown and cannot be suggested automatically"
                        ),
                    )
                )

        return suggestions

    # ---------------------------------------------------------

    def suggest_for_library(self, books):

        suggestions = []

        for book in books:
            suggestions.extend(self.suggest_for_book(book))

        return suggestions
