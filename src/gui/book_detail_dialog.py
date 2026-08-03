"""
Book Detail Dialog

Read-only detail view for a single book, opened by double-clicking a
row in the library view. Mirrors main.py's print_book() field set for
the CLI - same information, just in a dialog instead of stdout.
"""

from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout


class BookDetailDialog(QDialog):

    def __init__(self, book, parent=None):

        super().__init__(parent)

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
        form.addRow("Cover:", QLabel("Yes" if book.has_cover else "No"))
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
