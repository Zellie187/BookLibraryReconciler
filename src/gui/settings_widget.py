"""
Settings Widget

Reads and writes Settings/config.json (library_path/metadata_db) from
the GUI instead of requiring the user to hand-edit the file, per
README.md's setup instructions. Doesn't touch anything else - no new
settings, no new file format.

Restart required: `config.settings.LIBRARY_ROOT`/`METADATA_DB` are
computed once at import time and threaded through `Application` at
`python run.py gui` startup, so a change saved here only takes effect
on the next launch - this widget says so rather than pretending to
apply it live.
"""

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.settings import SETTINGS_FILE, load_settings


def save_settings(library_path, metadata_db):
    """
    Pure write step, kept separate from the widget so it's testable
    without constructing any Qt widgets. Writes exactly the two keys
    config.settings.load_settings() already reads.
    """

    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    payload = {"library_path": library_path, "metadata_db": metadata_db}

    SETTINGS_FILE.write_text(json.dumps(payload, indent=4), encoding="utf-8")


class SettingsWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        settings = load_settings()

        self.library_path_field = QLineEdit(settings.get("library_path", ""))
        self.metadata_db_field = QLineEdit(settings.get("metadata_db", ""))

        library_browse_button = QPushButton("Browse...")
        library_browse_button.clicked.connect(self.browse_library_path)

        metadata_browse_button = QPushButton("Browse...")
        metadata_browse_button.clicked.connect(self.browse_metadata_db)

        library_row = QHBoxLayout()
        library_row.addWidget(self.library_path_field)
        library_row.addWidget(library_browse_button)

        metadata_row = QHBoxLayout()
        metadata_row.addWidget(self.metadata_db_field)
        metadata_row.addWidget(metadata_browse_button)

        form = QFormLayout()
        form.addRow("Calibre library folder:", library_row)
        form.addRow("metadata.db (optional):", metadata_row)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save)

        note = QLabel(
            "Leave 'metadata.db' blank to use <library folder>/metadata.db "
            "(Calibre's normal location).\nChanges take effect the next time "
            f"you launch the app.\nSaved to: {SETTINGS_FILE}"
        )
        note.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(save_button)
        layout.addWidget(note)
        layout.addStretch()

    # ---------------------------------------------------------

    def browse_library_path(self):

        path = QFileDialog.getExistingDirectory(self, "Select Calibre library folder")

        if path:
            self.library_path_field.setText(path)

    # ---------------------------------------------------------

    def browse_metadata_db(self):

        path, _ = QFileDialog.getOpenFileName(
            self, "Select metadata.db", filter="Calibre database (*.db)"
        )

        if path:
            self.metadata_db_field.setText(path)

    # ---------------------------------------------------------

    def save(self):

        library_path = self.library_path_field.text().strip()

        if library_path and not self._folder_exists(library_path):
            QMessageBox.warning(self, "Settings", f"That folder doesn't exist:\n{library_path}")
            return

        save_settings(library_path, self.metadata_db_field.text().strip())

        QMessageBox.information(self, "Settings", "Saved. Restart the app for this to take effect.")

    # ---------------------------------------------------------

    @staticmethod
    def _folder_exists(path):

        return Path(path).is_dir()
