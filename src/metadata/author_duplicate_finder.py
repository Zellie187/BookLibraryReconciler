"""
Author Duplicate Finder

Groups author records (from Calibre's authors table) that are likely
the same real person recorded under different name formatting -
"Berry, Steve" vs "Steve Berry" vs "Berry Steve" all collapse to the
same signature (see text_normalize.name_signature).

Detection only - see repair/author_merger.py for merging duplicates,
which always requires an explicit --apply and a backup first.
"""

from collections import defaultdict
from dataclasses import dataclass, field

from metadata.text_normalize import name_signature


@dataclass
class AuthorDuplicateGroup:

    canonical_author_id: int = 0
    duplicate_author_ids: list[int] = field(default_factory=list)
    names: list[str] = field(default_factory=list)

    @property
    def all_author_ids(self):

        return [self.canonical_author_id, *self.duplicate_author_ids]


class AuthorDuplicateFinder:

    def find_duplicates(self, author_records):
        """
        author_records: Author objects (id, name, sort), e.g. from
        LibraryService.get_all_author_records(). The canonical id in
        each group is deterministically the lowest author id - there's
        no signal in the data for which spelling is "correct", so this
        is just a stable default a human can override when reviewing.
        """

        authors_by_signature = defaultdict(list)

        for author in author_records:

            signature = name_signature(author.name)

            if signature:
                authors_by_signature[signature].append(author)

        groups = []

        for authors in authors_by_signature.values():

            if len(authors) < 2:
                continue

            authors_sorted = sorted(authors, key=lambda author: author.id)
            canonical, *duplicates = authors_sorted

            groups.append(
                AuthorDuplicateGroup(
                    canonical_author_id=canonical.id,
                    duplicate_author_ids=[author.id for author in duplicates],
                    names=[author.name for author in authors_sorted],
                )
            )

        return groups
