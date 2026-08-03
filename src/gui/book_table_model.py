"""
Book Table Model

Read-only Qt table model wrapping a list[Book] for the GUI's library
view. Deliberately read-only - no setData()/flags() write path - the
GUI inherits the CLI's non-negotiable rule that nothing gets written
without an explicit preview + apply step (see docs/architecture/GUI.md).
This model just displays whatever Book objects it's given; it never
mutates them or writes to metadata.db.
"""

from PySide6.QtCore import QAbstractTableModel, Qt

COLUMNS = ("ID", "Title", "Author", "Series", "Rating", "ISBN", "Cover")


class BookTableModel(QAbstractTableModel):

    def __init__(self, books=None, parent=None):

        super().__init__(parent)

        self.books = list(books or [])

    # ---------------------------------------------------------

    def set_books(self, books):

        self.beginResetModel()
        self.books = list(books)
        self.endResetModel()

    # ---------------------------------------------------------

    def book_at(self, row):

        if 0 <= row < len(self.books):
            return self.books[row]

        return None

    # ---------------------------------------------------------

    def rowCount(self, parent=None):

        return len(self.books)

    # ---------------------------------------------------------

    def columnCount(self, parent=None):

        return len(COLUMNS)

    # ---------------------------------------------------------

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):

        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None

        return COLUMNS[section]

    # ---------------------------------------------------------

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        book = self.books[index.row()]
        column = index.column()

        if column == 0:
            return book.id
        if column == 1:
            return book.title
        if column == 2:
            return book.author_names
        if column == 3:
            return book.series_name
        if column == 4:
            return book.rating
        if column == 5:
            return book.isbn or "-"
        if column == 6:
            return "Yes" if book.has_cover else "No"

        return None
