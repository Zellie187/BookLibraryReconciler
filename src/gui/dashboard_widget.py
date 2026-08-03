"""
Dashboard Widget

Library health at a glance, computed from the exact same analyzers the
CLI's `preview`/`analyze` commands already use (`LibraryAnalyzer`,
`LibraryInspector`) - no new business logic, just a GUI view over
existing ones. Read-only; nothing here writes to metadata.db.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from analyzers.library_analyzer import LibraryAnalyzer
from metadata.library_inspector import LibraryInspector

TILE_COLUMNS = 3

VALUE_STYLE = "font-size: 22px; font-weight: bold;"
CAPTION_STYLE = "color: gray;"


def compute_stats(books):
    """
    Pure data step, kept separate from widget-building so the numbers
    themselves are testable without constructing any Qt widgets.
    """

    analyzer = LibraryAnalyzer(books)
    inspection = LibraryInspector().inspect(books)

    return [
        ("Total books", f"{analyzer.total_books():,}"),
        ("Unique authors", f"{analyzer.unique_authors():,}"),
        ("Unique series", f"{analyzer.unique_series():,}"),
        ("Average health score", f"{inspection.average_score}%"),
        ("Books needing attention", f"{len(inspection.books_needing_attention):,}"),
        ("Missing ISBN", f"{analyzer.books_missing_isbn():,}"),
        ("Missing cover", f"{analyzer.books_missing_cover():,}"),
        ("Missing description", f"{analyzer.books_missing_comments():,}"),
        ("ISBN duplicate groups", f"{len(inspection.isbn_duplicate_groups):,}"),
        ("Title duplicate groups", f"{len(inspection.title_duplicate_groups):,}"),
        ("Series order issues", f"{len(inspection.series_order_issues):,}"),
    ]


class DashboardWidget(QWidget):

    def __init__(self, library_service, parent=None):

        super().__init__(parent)

        self.library_service = library_service

        self.stats_grid = QGridLayout()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.addLayout(self.stats_grid)
        layout.addWidget(refresh_button)
        layout.addStretch()

        self.refresh()

    # ---------------------------------------------------------

    def refresh(self):

        books = self.library_service.get_all_books()
        stats = compute_stats(books)

        self._clear_grid()

        for index, (label, value) in enumerate(stats):
            row, column = divmod(index, TILE_COLUMNS)
            self.stats_grid.addWidget(self._make_tile(label, value), row, column)

    # ---------------------------------------------------------

    def _clear_grid(self):

        while self.stats_grid.count():

            item = self.stats_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    # ---------------------------------------------------------

    @staticmethod
    def _make_tile(label, value):

        tile = QWidget()
        tile_layout = QVBoxLayout(tile)

        value_label = QLabel(value)
        value_label.setStyleSheet(VALUE_STYLE)

        caption_label = QLabel(label)
        caption_label.setStyleSheet(CAPTION_STYLE)

        tile_layout.addWidget(value_label)
        tile_layout.addWidget(caption_label)

        return tile
