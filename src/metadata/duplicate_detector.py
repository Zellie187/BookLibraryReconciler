"""
Duplicate Detector

Finds books that are likely the same book catalogued more than once,
grouped two ways:

- Exact ISBN match - a strong signal, same real-world edition recorded
  under two book ids.
- Fuzzy title match, blocked by primary author - catches re-imports
  with slightly different title formatting (extra whitespace, a
  subtitle, punctuation) without an ISBN to key off of.

Only ever returns groups for a human to review - nothing is merged or
deleted.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from metadata.text_normalize import name_signature

FUZZY_DUPLICATE_THRESHOLD = 0.95


def _strip_digits(text):

    return re.sub(r"\d+", "", text)


def _differs_only_by_a_number(title_a, title_b):
    """
    True for pairs like "Elminster 1 - Greenwood, Ed" / "Elminster 2 -
    Greenwood, Ed" or "042 - Maxwell Grant" / "043 - Maxwell Grant" -
    a shared template with only a volume/issue number changed. These
    are different books, not duplicates, even though a short shared
    template can push their similarity ratio very high.
    """

    return title_a != title_b and _strip_digits(title_a) == _strip_digits(title_b)


@dataclass
class DuplicateGroup:

    reason: str = ""
    book_ids: list[int] = field(default_factory=list)


class DuplicateDetector:

    def find_isbn_duplicates(self, books):

        books_by_isbn = defaultdict(list)

        for book in books:
            if book.isbn:
                books_by_isbn[book.isbn].append(book.id)

        return [
            DuplicateGroup(reason=f"isbn={isbn}", book_ids=book_ids)
            for isbn, book_ids in books_by_isbn.items()
            if len(book_ids) > 1
        ]

    # ---------------------------------------------------------

    def find_title_duplicates(self, books, threshold=FUZZY_DUPLICATE_THRESHOLD):
        """
        Fuzzy title matching, blocked by primary author so this stays
        fast on large libraries: two books are only ever compared if
        they share the same first author (or both have none).

        Books whose title is just their own author's name, in any
        punctuation/word order ("Berry, Steve", "Steve Berry", "Berry
        Steve") are excluded - that's a placeholder from a failed
        import, not a real title (see MetadataValidator's
        title_matches_author check), and grouping many different
        books that all lack a real title as "duplicates of each
        other" would be noise, not a finding.
        """

        books_by_author = defaultdict(list)

        for book in books:

            author = book.authors[0] if book.authors else None
            author_key = author.name.lower() if author else ""

            if author is not None:
                title_signature = name_signature(book.title)
                if title_signature in (name_signature(author.name), name_signature(author.sort)):
                    continue

            books_by_author[author_key].append(book)

        groups = []

        for same_author_books in books_by_author.values():
            groups.extend(self._find_similar_titles(same_author_books, threshold))

        return groups

    # ---------------------------------------------------------

    def _find_similar_titles(self, books, threshold):

        groups = []
        already_grouped = [False] * len(books)

        for i in range(len(books)):

            if already_grouped[i]:
                continue

            title_i = books[i].title.strip().lower()
            group_ids = [books[i].id]

            for j in range(i + 1, len(books)):

                if already_grouped[j]:
                    continue

                title_j = books[j].title.strip().lower()

                if _differs_only_by_a_number(title_i, title_j):
                    continue

                if SequenceMatcher(None, title_i, title_j).ratio() >= threshold:
                    group_ids.append(books[j].id)
                    already_grouped[j] = True

            if len(group_ids) > 1:
                already_grouped[i] = True
                groups.append(DuplicateGroup(reason="similar title, same author", book_ids=group_ids))

        return groups
