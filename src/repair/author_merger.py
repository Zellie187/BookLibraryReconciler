"""
Author Merger

Applies AuthorDuplicateGroup findings (see metadata/author_duplicate_finder.py):
repoints every book linked to a duplicate author over to the canonical
author id, then removes the now-unused duplicate author rows (see
repositories/author_repository.py's merge_authors for the actual SQL).

One group failing does not stop the rest, and is reported back instead
of raised - mirrors repair/organize_applier.py's pattern.
"""

import sqlite3
from dataclasses import dataclass, field


@dataclass
class AuthorMergeResult:

    canonical_author_id: int = 0
    merged_author_ids: list[int] = field(default_factory=list)
    merged: bool = False
    error: str = ""


class AuthorMerger:

    def __init__(self, library_service):

        self.library_service = library_service

    # ---------------------------------------------------------

    def apply(self, duplicate_groups):

        return [self._apply_one(group) for group in duplicate_groups]

    # ---------------------------------------------------------

    def _apply_one(self, group):

        result = AuthorMergeResult(
            canonical_author_id=group.canonical_author_id,
            merged_author_ids=list(group.duplicate_author_ids),
        )

        try:
            self.library_service.merge_authors(group.canonical_author_id, group.duplicate_author_ids)
        except sqlite3.Error as error:
            result.error = f"Merge failed: {error}"
            return result

        result.merged = True

        return result
