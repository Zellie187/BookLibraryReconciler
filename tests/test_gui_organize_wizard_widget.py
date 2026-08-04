from dataclasses import dataclass, field

from gui.organize_wizard_widget import format_plan_line, summarize_apply_results
from repair.file_organizer import FormatRename, OrganizePlan


@dataclass
class FakeApplyResult:

    book_id: int = 0
    proposed_path: str = ""
    moved: bool = False
    renamed_formats: list = field(default_factory=list)
    error: str = ""


def test_format_plan_line_shows_book_id_title_and_path_change():

    plan = OrganizePlan(
        book_id=1,
        title="Doctor Sleep",
        current_path="messy/path",
        proposed_path="Stephen King/Doctor Sleep",
    )

    line = format_plan_line(plan)

    assert line.startswith("#1 'Doctor Sleep'")
    assert "messy/path -> Stephen King/Doctor Sleep" in line


def test_format_plan_line_mentions_renamed_formats_when_present():

    plan = OrganizePlan(
        book_id=1,
        title="Doctor Sleep",
        current_path="a",
        proposed_path="b",
        format_renames=[FormatRename(format="EPUB", old_name="old", new_name="Doctor Sleep")],
    )

    line = format_plan_line(plan)

    assert "formats: Doctor Sleep" in line


def test_format_plan_line_omits_format_note_when_nothing_renamed():

    plan = OrganizePlan(
        book_id=1,
        title="Doctor Sleep",
        current_path="a",
        proposed_path="b",
        format_renames=[FormatRename(format="EPUB", old_name="same", new_name="same")],
    )

    line = format_plan_line(plan)

    assert "formats:" not in line


def test_summarize_apply_results_counts_successes():

    results = [
        FakeApplyResult(book_id=1, moved=True),
        FakeApplyResult(book_id=2, moved=True),
    ]

    summary = summarize_apply_results(results, "/backups/metadata.bak")

    assert "Applied 2/2 change(s)." in summary
    assert "/backups/metadata.bak" in summary
    assert "Failures" not in summary


def test_summarize_apply_results_lists_failures():

    results = [
        FakeApplyResult(book_id=1, moved=True),
        FakeApplyResult(book_id=2, error="Destination already exists"),
    ]

    summary = summarize_apply_results(results, "/backups/metadata.bak")

    assert "Applied 1/2 change(s)." in summary
    assert "Failures:" in summary
    assert "#2: Destination already exists" in summary


def test_summarize_apply_results_truncates_long_failure_lists():

    results = [FakeApplyResult(book_id=index, error="failed") for index in range(15)]

    summary = summarize_apply_results(results, "/backups/metadata.bak")

    assert "and 5 more" in summary
