from dataclasses import dataclass, field

from gui.repair_wizard_widget import (
    format_author_group_line,
    format_needs_review_line,
    format_suggestion_line,
    summarize_repair_results,
)
from metadata.author_duplicate_finder import AuthorDuplicateGroup
from metadata.metadata_repair import RepairSuggestion


@dataclass
class FakeRepairResult:

    book_id: int = 0
    error: str = ""


@dataclass
class FakeMergeResult:

    canonical_author_id: int = 0
    merged_author_ids: list = field(default_factory=list)
    error: str = ""


def test_format_suggestion_line_shows_before_after_and_reason():

    suggestion = RepairSuggestion(
        book_id=1,
        field="title",
        current_value="The Maze of Bones by Rick Riordan",
        suggested_value="The Maze of Bones",
        reason="Title appears to end with a 'by <author>' clause",
    )

    line = format_suggestion_line(suggestion)

    assert line.startswith("#1:")
    assert "'The Maze of Bones by Rick Riordan' -> 'The Maze of Bones'" in line
    assert "Title appears to end with a 'by <author>' clause" in line


def test_format_needs_review_line_shows_book_and_reason_only():

    suggestion = RepairSuggestion(
        book_id=5,
        field="title",
        current_value="Steve Berry",
        suggested_value="",
        reason="Title matches the author name ('Steve Berry')",
    )

    line = format_needs_review_line(suggestion)

    assert line.startswith("#5:")
    assert "Title matches the author name" in line
    assert "->" not in line


def test_format_author_group_line_shows_names_and_canonical_id():

    group = AuthorDuplicateGroup(
        canonical_author_id=12, duplicate_author_ids=[45], names=["Berry, Steve", "Steve Berry"]
    )

    line = format_author_group_line(group)

    assert "Berry, Steve" in line
    assert "Steve Berry" in line
    assert "merge into author #12" in line


def test_summarize_repair_results_counts_successes():

    title_results = [FakeRepairResult(book_id=1), FakeRepairResult(book_id=2)]
    author_results = [FakeMergeResult(canonical_author_id=10)]

    summary = summarize_repair_results(title_results, author_results, "/backups/metadata.bak")

    assert "Title repairs applied: 2/2" in summary
    assert "Author merges applied: 1/1" in summary
    assert "/backups/metadata.bak" in summary
    assert "Failures" not in summary


def test_summarize_repair_results_lists_failures_from_both_kinds():

    title_results = [FakeRepairResult(book_id=1, error="Apply failed")]
    author_results = [FakeMergeResult(canonical_author_id=10, error="Merge failed")]

    summary = summarize_repair_results(title_results, author_results, "/backups/metadata.bak")

    assert "Title repairs applied: 0/1" in summary
    assert "Author merges applied: 0/1" in summary
    assert "Failures:" in summary
    assert "#1: Apply failed" in summary
    assert "#10: Merge failed" in summary


def test_summarize_repair_results_truncates_long_failure_lists():

    title_results = [FakeRepairResult(book_id=index, error="failed") for index in range(15)]

    summary = summarize_repair_results(title_results, [], "/backups/metadata.bak")

    assert "and 5 more" in summary


def test_summarize_repair_results_handles_no_selections():

    summary = summarize_repair_results([], [], "/backups/metadata.bak")

    assert "Title repairs applied: 0/0" in summary
    assert "Author merges applied: 0/0" in summary
