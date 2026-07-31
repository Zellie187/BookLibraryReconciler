"""
Series Order Checker

Groups books by series and flags two kinds of problems: two books
sharing the same series position, and a gap in an otherwise-sequential
run of whole-number positions.

series_index == 0 is Calibre's "not really set" sentinel (also flagged
per-book by MetadataValidator's series_index_zero check) and is
excluded here entirely - treating two unset books as "duplicate
position 0" would be noise, not a finding. Fractional positions (1.5,
for a between-volumes novella) are a normal Calibre convention, so they
count toward duplicate-position checks but are excluded from the gap
check, which only looks at whole numbers.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class SeriesOrderIssue:

    series_name: str = ""
    issue_type: str = ""  # "duplicate_position" or "gap"
    detail: str = ""


def _group_by_series(books):

    books_by_series = defaultdict(list)

    for book in books:
        if book.series is not None:
            books_by_series[book.series.name].append(book)

    return books_by_series


def _find_duplicate_positions(series_name, series_books):

    counts = defaultdict(list)

    for book in series_books:
        if book.series_index > 0:
            counts[book.series_index].append(book.id)

    issues = []

    for position, book_ids in sorted(counts.items()):

        if len(book_ids) > 1:
            issues.append(
                SeriesOrderIssue(
                    series_name=series_name,
                    issue_type="duplicate_position",
                    detail=f"position {position:g} used by books {book_ids}",
                )
            )

    return issues


def _find_gaps(series_name, series_books):

    whole_numbers = sorted(
        {
            int(book.series_index)
            for book in series_books
            if book.series_index > 0 and float(book.series_index).is_integer()
        }
    )

    if len(whole_numbers) < 2:
        return []

    expected = set(range(whole_numbers[0], whole_numbers[-1] + 1))
    missing = sorted(expected - set(whole_numbers))

    if not missing:
        return []

    return [
        SeriesOrderIssue(
            series_name=series_name,
            issue_type="gap",
            detail=f"missing position(s) {missing} between {whole_numbers[0]} and {whole_numbers[-1]}",
        )
    ]


def find_series_order_issues(books):

    issues = []

    for series_name, series_books in _group_by_series(books).items():
        issues.extend(_find_duplicate_positions(series_name, series_books))
        issues.extend(_find_gaps(series_name, series_books))

    return issues
