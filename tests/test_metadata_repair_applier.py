import sqlite3
from unittest.mock import MagicMock

from metadata.metadata_repair import RepairSuggestion
from repair.metadata_repair_applier import MetadataRepairApplier


def test_applies_suggestion_with_a_concrete_value():

    library_service = MagicMock()
    applier = MetadataRepairApplier(library_service)

    suggestion = RepairSuggestion(
        book_id=2,
        field="title",
        current_value="The Maze of Bones by Rick Riordan",
        suggested_value="The Maze of Bones",
        reason="Title appears to end with a 'by <author>' clause",
    )

    results = applier.apply([suggestion])

    assert results[0].applied is True
    assert results[0].error == ""
    library_service.update_book_title.assert_called_once_with(2, "The Maze of Bones")


def test_skips_suggestion_with_no_concrete_value():

    library_service = MagicMock()
    applier = MetadataRepairApplier(library_service)

    suggestion = RepairSuggestion(
        book_id=4,
        field="title",
        current_value="Taylor, Roger",
        suggested_value="",
        reason="Title matches the author name",
    )

    results = applier.apply([suggestion])

    assert results[0].applied is False
    assert "manual review" in results[0].error
    library_service.update_book_title.assert_not_called()


def test_unknown_field_is_reported_not_raised():

    library_service = MagicMock()
    applier = MetadataRepairApplier(library_service)

    suggestion = RepairSuggestion(book_id=1, field="publisher", suggested_value="Scribner")

    results = applier.apply([suggestion])

    assert results[0].applied is False
    assert "publisher" in results[0].error


def test_one_failure_does_not_stop_the_rest():

    library_service = MagicMock()
    library_service.update_book_title.side_effect = [sqlite3.Error("locked"), None]

    applier = MetadataRepairApplier(library_service)

    suggestions = [
        RepairSuggestion(book_id=1, field="title", suggested_value="A"),
        RepairSuggestion(book_id=2, field="title", suggested_value="B"),
    ]

    results = applier.apply(suggestions)

    assert results[0].applied is False
    assert "locked" in results[0].error
    assert results[1].applied is True
