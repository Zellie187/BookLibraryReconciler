import sqlite3
from unittest.mock import MagicMock

from metadata.author_duplicate_finder import AuthorDuplicateGroup
from repair.author_merger import AuthorMerger


def test_applies_merge_successfully():

    library_service = MagicMock()
    merger = AuthorMerger(library_service)

    group = AuthorDuplicateGroup(canonical_author_id=1, duplicate_author_ids=[2, 3], names=["A", "B", "C"])

    results = merger.apply([group])

    assert results[0].merged is True
    assert results[0].error == ""
    library_service.merge_authors.assert_called_once_with(1, [2, 3])


def test_one_failure_does_not_stop_the_rest():

    library_service = MagicMock()
    library_service.merge_authors.side_effect = [sqlite3.Error("locked"), None]

    merger = AuthorMerger(library_service)

    groups = [
        AuthorDuplicateGroup(canonical_author_id=1, duplicate_author_ids=[2]),
        AuthorDuplicateGroup(canonical_author_id=5, duplicate_author_ids=[6]),
    ]

    results = merger.apply(groups)

    assert results[0].merged is False
    assert "locked" in results[0].error
    assert results[1].merged is True
