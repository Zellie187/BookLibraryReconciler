"""
Metadata Validator

Flags books whose metadata looks *wrong*, as opposed to merely missing
(that's metadata_score's job). These are heuristics based on patterns
seen in real Calibre libraries imported from mixed sources - always
show them to a human before changing anything.
"""

import re
from dataclasses import dataclass, field

from metadata.isbn_validator import is_valid_isbn

# Requires at least two capitalized tokens after "by" ("by Rick Riordan"),
# not just one ("by Morning", "by Design") - real titles routinely end in
# "by <a single capitalized word>" as ordinary English, and a single-word
# match produced false positives against real titles like "Married by
# Morning" and "Dexter by Design". Two-plus capitalized words in a row is
# a much stronger signal of an actual "Title by Firstname Lastname" echo.
BY_CLAUSE_PATTERN = re.compile(r"\s+by\s+[A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*)+$")


@dataclass
class ValidationIssue:

    code: str = ""
    message: str = ""


@dataclass
class ValidationReport:

    book_id: int = 0
    title: str = ""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_clean(self):

        return not self.issues


class MetadataValidator:

    def validate_book(self, book):

        report = ValidationReport(book_id=book.id, title=book.title)

        title = book.title.strip()

        if not title:
            report.issues.append(ValidationIssue("empty_title", "Title is empty"))
            return report

        for author in book.authors:

            if author.name and title.lower() == author.name.lower():
                report.issues.append(
                    ValidationIssue(
                        "title_matches_author",
                        f"Title matches the author name ({author.name!r})",
                    )
                )

            if author.sort and title.lower() == author.sort.lower():
                report.issues.append(
                    ValidationIssue(
                        "title_matches_author",
                        f"Title matches the author's sort name ({author.sort!r})",
                    )
                )

        if BY_CLAUSE_PATTERN.search(title):
            report.issues.append(
                ValidationIssue(
                    "title_contains_by_clause",
                    "Title appears to end with a 'by <author>' clause",
                )
            )

        if book.series is not None and book.series_index == 0:
            report.issues.append(
                ValidationIssue(
                    "series_index_zero",
                    f"In series {book.series.name!r} but series_index is 0",
                )
            )

        if book.isbn and not is_valid_isbn(book.isbn):
            report.issues.append(
                ValidationIssue(
                    "invalid_isbn",
                    f"ISBN {book.isbn!r} fails checksum validation",
                )
            )

        return report

    # ---------------------------------------------------------

    def validate_library(self, books):

        return [self.validate_book(book) for book in books]

    # ---------------------------------------------------------

    def books_with_issues(self, books):

        return [report for report in self.validate_library(books) if not report.is_clean]
