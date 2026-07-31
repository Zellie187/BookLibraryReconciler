from unittest.mock import MagicMock

from repair.file_organizer import FormatRename, OrganizePlan
from repair.organize_applier import OrganizeApplier


def test_apply_moves_folder_and_renames_formats(tmp_path):

    book_dir = tmp_path / "Stephen King" / "Doctor Sleep (1)"
    book_dir.mkdir(parents=True)
    (book_dir / "Doctor Sleep - Stephen King.epub").write_text("fake epub")

    plan = OrganizePlan(
        book_id=1,
        title="Doctor Sleep",
        author="Stephen King",
        current_path="Stephen King/Doctor Sleep (1)",
        proposed_path="Stephen King/Doctor Sleep",
        format_renames=[
            FormatRename(format="EPUB", old_name="Doctor Sleep - Stephen King", new_name="Doctor Sleep")
        ],
    )

    library_service = MagicMock()
    applier = OrganizeApplier(tmp_path, library_service)

    results = applier.apply([plan])

    assert results[0].moved is True
    assert results[0].error == ""
    assert (tmp_path / "Stephen King" / "Doctor Sleep" / "Doctor Sleep.epub").exists()
    assert not (tmp_path / "Stephen King" / "Doctor Sleep (1)").exists()

    library_service.update_book_path.assert_called_once_with(1, "Stephen King/Doctor Sleep")
    library_service.rename_format.assert_called_once_with(1, "EPUB", "Doctor Sleep")


def test_apply_reports_missing_source_folder(tmp_path):

    plan = OrganizePlan(
        book_id=1,
        title="Ghost Book",
        author="Nobody",
        current_path="Nobody/Ghost Book (1)",
        proposed_path="Nobody/Ghost Book",
    )

    library_service = MagicMock()
    applier = OrganizeApplier(tmp_path, library_service)

    results = applier.apply([plan])

    assert results[0].moved is False
    assert "not found" in results[0].error
    library_service.update_book_path.assert_not_called()


def test_apply_skips_folder_move_when_only_formats_change(tmp_path):

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)
    (book_dir / "old name.pdf").write_text("fake pdf")

    plan = OrganizePlan(
        book_id=1,
        title="Title",
        author="Author",
        current_path="Author/Title",
        proposed_path="Author/Title",
        format_renames=[FormatRename(format="PDF", old_name="old name", new_name="Title")],
    )

    library_service = MagicMock()
    applier = OrganizeApplier(tmp_path, library_service)

    results = applier.apply([plan])

    assert results[0].moved is False
    assert (book_dir / "Title.pdf").exists()
    library_service.update_book_path.assert_not_called()
    library_service.rename_format.assert_called_once_with(1, "PDF", "Title")


def test_apply_does_not_stop_on_one_failure(tmp_path):

    good_dir = tmp_path / "Author" / "Good Book (1)"
    good_dir.mkdir(parents=True)

    good_plan = OrganizePlan(
        book_id=1,
        title="Good Book",
        author="Author",
        current_path="Author/Good Book (1)",
        proposed_path="Author/Good Book",
    )
    bad_plan = OrganizePlan(
        book_id=2,
        title="Missing Book",
        author="Author",
        current_path="Author/Missing Book (2)",
        proposed_path="Author/Missing Book",
    )

    library_service = MagicMock()
    applier = OrganizeApplier(tmp_path, library_service)

    results = applier.apply([bad_plan, good_plan])

    assert results[0].error != ""
    assert results[1].moved is True
