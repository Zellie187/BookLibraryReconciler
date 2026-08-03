"""
Book Detail Dialog

Read-only detail view for a single book, opened by double-clicking a
row in the library view. Mirrors main.py's print_book() field set for
the CLI - same information, just in a dialog instead of stdout.
"""

from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from gui.cover_finder_dialog import CoverFinderDialog
from gui.metadata_comparison_dialog import MetadataComparisonDialog


class BookDetailDialog(QDialog):

    def __init__(
        self, book, library_root=None, library_service=None, database_path=None, parent=None
    ):

        super().__init__(parent)

        self.book = book
        self.library_root = library_root
        self.library_service = library_service
        self.database_path = database_path

        self.setWindowTitle(f"#{book.id} - {book.title}")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        form.addRow("Title:", QLabel(book.title))
        form.addRow("Author:", QLabel(book.author_names))
        form.addRow("Series:", QLabel(book.series_name or "-"))
        form.addRow("Book number:", QLabel(str(book.series_index) if book.series else "-"))
        form.addRow("Rating:", QLabel(str(book.rating)))
        form.addRow("ISBN:", QLabel(book.isbn or "-"))
        form.addRow("Publisher:", QLabel(book.publisher or "-"))
        form.addRow("UUID:", QLabel(book.uuid or "-"))
        form.addRow("Path:", QLabel(book.path or "-"))
        self.cover_label = QLabel("Yes" if book.has_cover else "No")
        form.addRow("Cover:", self.cover_label)
        form.addRow("Formats:", QLabel(", ".join(book.formats) or "-"))

        layout.addLayout(form)

        if book.comments:
            comments_label = QLabel(book.comments)
            comments_label.setWordWrap(True)
            layout.addWidget(QLabel("Comments:"))
            layout.addWidget(comments_label)

        if book.identifiers:
            layout.addWidget(QLabel("Identifiers:"))
            for key, value in sorted(book.identifiers.items()):
                layout.addWidget(QLabel(f"  {key}: {value}"))

        compare_button = QPushButton("Compare Metadata...")
        compare_button.clicked.connect(self.open_metadata_comparison)

        cover_button = QPushButton("Find Cover...")
        cover_button.clicked.connect(self.open_cover_finder)

        button_row = QHBoxLayout()
        button_row.addWidget(compare_button)
        button_row.addWidget(cover_button)
        layout.addLayout(button_row)

    # ---------------------------------------------------------

    def open_metadata_comparison(self):

        dialog = MetadataComparisonDialog(self.book, parent=self)
        dialog.exec()

    # ---------------------------------------------------------

    def open_cover_finder(self):

        dialog = CoverFinderDialog(
            self.book, self.library_root, self.library_service, self.database_path, parent=self
        )
        dialog.exec()

        self.cover_label.setText("Yes" if self.book.has_cover else "No")
