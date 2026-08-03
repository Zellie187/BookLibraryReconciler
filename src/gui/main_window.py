"""
Main Window

MVP library view for the v2.0.0 desktop application: a searchable
table of books, opening a read-only detail dialog on double-click.
Reuses the exact same SearchController/SearchService the CLI's
`search` command uses - the query syntax typed into the search box is
identical to `python run.py search "..."` (see Search.md), so there is
only one place that understands search terms.

Deliberately minimal: no dashboard/metadata-comparison/report-viewer/
settings yet (see docs/architecture/GUI.md and Roadmap.md for what's
still planned). Read-only - nothing here writes to metadata.db.
"""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from controllers.search_controller import SearchController
from gui.book_detail_dialog import BookDetailDialog
from gui.book_table_model import BookTableModel


class MainWindow(QMainWindow):

    def __init__(self, library_service, search_service, parent=None):

        super().__init__(parent)

        self.library_service = library_service
        self.search_controller = SearchController(search_service)

        self.setWindowTitle("Book Library Reconciler")
        self.resize(900, 600)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search (e.g. author=King, isbn:missing, has-cover) - leave blank for all books"
        )
        self.search_box.returnPressed.connect(self.run_search)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.run_search)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_box)
        search_row.addWidget(search_button)

        self.table_model = BookTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_view.doubleClicked.connect(self.show_book_details)

        self.status_label = QLabel("Loading library...")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(search_row)
        layout.addWidget(self.table_view)
        layout.addWidget(self.status_label)

        self.setCentralWidget(central)

        self.load_all_books()

    # ---------------------------------------------------------

    def load_all_books(self):

        books = self.library_service.get_all_books()
        self.table_model.set_books(books)
        self.status_label.setText(f"{len(books):,} books")

    # ---------------------------------------------------------

    def run_search(self):

        query = self.search_box.text().strip()
        terms = query.split() if query else []

        try:
            results = self.search_controller.search(terms)
        except ValueError as error:
            QMessageBox.warning(self, "Search error", str(error))
            return

        self.table_model.set_books(results)
        self.status_label.setText(f"{len(results):,} matches")

    # ---------------------------------------------------------

    def show_book_details(self, index):

        book = self.table_model.book_at(index.row())

        if book is None:
            return

        dialog = BookDetailDialog(book, parent=self)
        dialog.exec()
