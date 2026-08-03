import json

from gui import settings_widget


def test_save_settings_writes_expected_json(tmp_path, monkeypatch):

    settings_file = tmp_path / "Settings" / "config.json"
    monkeypatch.setattr(settings_widget, "SETTINGS_FILE", settings_file)

    settings_widget.save_settings("C:/My Calibre Library", "")

    payload = json.loads(settings_file.read_text(encoding="utf-8"))

    assert payload == {"library_path": "C:/My Calibre Library", "metadata_db": ""}


def test_save_settings_creates_parent_folder_if_missing(tmp_path, monkeypatch):

    settings_file = tmp_path / "does" / "not" / "exist" / "config.json"
    monkeypatch.setattr(settings_widget, "SETTINGS_FILE", settings_file)

    settings_widget.save_settings("/some/library", "/some/library/metadata.db")

    assert settings_file.exists()


def test_save_settings_overwrites_existing_file(tmp_path, monkeypatch):

    settings_file = tmp_path / "config.json"
    settings_file.write_text(json.dumps({"library_path": "old", "metadata_db": "old.db"}))
    monkeypatch.setattr(settings_widget, "SETTINGS_FILE", settings_file)

    settings_widget.save_settings("new", "new.db")

    payload = json.loads(settings_file.read_text(encoding="utf-8"))

    assert payload == {"library_path": "new", "metadata_db": "new.db"}


def test_save_settings_stores_both_fields_blank(tmp_path, monkeypatch):

    settings_file = tmp_path / "config.json"
    monkeypatch.setattr(settings_widget, "SETTINGS_FILE", settings_file)

    settings_widget.save_settings("", "")

    payload = json.loads(settings_file.read_text(encoding="utf-8"))

    assert payload == {"library_path": "", "metadata_db": ""}
