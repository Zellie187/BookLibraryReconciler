import pytest

from repair.backup import backup_database


def test_backup_creates_a_timestamped_copy(tmp_path):

    db_path = tmp_path / "metadata.db"
    db_path.write_text("fake sqlite content")

    backup_path = backup_database(db_path)

    assert backup_path.exists()
    assert backup_path.read_text() == "fake sqlite content"
    assert backup_path != db_path
    assert backup_path.suffix == ".bak"


def test_backup_missing_database_raises(tmp_path):

    with pytest.raises(FileNotFoundError):
        backup_database(tmp_path / "does_not_exist.db")
