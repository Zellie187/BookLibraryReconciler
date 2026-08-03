"""
Main Window

MVP for the v2.0.0 desktop application: a "Library" tab (searchable
table of books, opening a read-only detail dialog on double-click - it
in turn opens a Metadata Comparison dialog), a "Dashboard" tab (library
health at a glance), a "Reports" tab (the 4 CLI report presets,
rendered as text), and a "Settings" tab (edits Settings/config.json).
The search box reuses the exact same SearchController/SearchService
the CLI's `search` command uses - the query syntax typed into the
search box is identical to `python run.py search "..."` (see
Search.md), so there is only one place that understands search terms.

Deliberately minimal: no repair-wizard/notifications yet (see
docs/architecture/GUI.md and Roadmap.md for what's still planned).
Read-only with respect to metadata.db - Settings writes to
Settings/config.json, a separate file the CLI already documents
hand-editing directly (see README.md).
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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from controllers.search_controller import SearchController
from gui.book_detail_dialog import BookDetailDialog
from gui.book_table_model import BookTableModel
from gui.dashboard_widget import DashboardWidget
from gui.report_viewer_widget import ReportViewerWidget
from gui.settings_widget import SettingsWidget


class MainWindow(QMainWindow):

    def __init__(
        self, library_service, search_service, library_root=None, database_path=None, parent=None
    ):

        super().__init__(parent)

        self.library_service = library_service
        self.library_root = library_root
        self.database_path = database_path
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

        library_tab = QWidget()
        library_layout = QVBoxLayout(library_tab)
        library_layout.addLayout(search_row)
        library_layout.addWidget(self.table_view)
        library_layout.addWidget(self.status_label)

        self.dashboard_widget = DashboardWidget(library_service)
        self.report_viewer_widget = ReportViewerWidget(library_service)
        self.settings_widget = SettingsWidget()

        tabs = QTabWidget()
        tabs.addTab(library_tab, "Library")
        tabs.addTab(self.dashboard_widget, "Dashboard")
        tabs.addTab(self.report_viewer_widget, "Reports")
        tabs.addTab(self.settings_widget, "Settings")

        self.setCentralWidget(tabs)

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

        dialog = BookDetailDialog(
            book,
            library_root=self.library_root,
            library_service=self.library_service,
            database_path=self.database_path,
            parent=self,
        )
        dialog.exec()

        # book_at() returns the same Book object CoverFinderDialog may
        # have mutated (has_cover) - repaint rather than reload, so an
        # active search filter isn't reset by closing the detail dialog.
        self.table_model.layoutChanged.emit()
