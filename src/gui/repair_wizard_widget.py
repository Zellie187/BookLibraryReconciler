"""
Repair Wizard Widget

GUI equivalent of the CLI's `repair` command: preview title-repair
suggestions and duplicate-author groups for the whole library, let the
user deselect individual items, then apply only the checked ones.
Second half of the "repair wizard" GUI.md always planned (see
organize_wizard_widget.py for the first half). Same reasoning applies:
not blocked by an unanswered policy question - the CLI's `repair
--apply` semantics (backup-first, auto-applicable suggestions only,
one item failing doesn't stop the rest) were already decided and
tested; per-item selection here is strictly *safer* than the CLI's
all-or-nothing apply.

Suggestions without a concrete `suggested_value` (the real value is
genuinely unknown - e.g. a title that's just an echo of the author's
own name) are shown for visibility but never offered as checkable,
matching the CLI's "needs manual review" distinction exactly: there is
nothing to apply.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from metadata.author_duplicate_finder import AuthorDuplicateFinder
from metadata.metadata_repair import MetadataRepair
from repair.author_merger import AuthorMerger
from repair.backup import backup_database
from repair.metadata_repair_applier import MetadataRepairApplier


def format_suggestion_line(suggestion):
    """
    Pure formatting step for an auto-applicable title suggestion, kept
    separate from the widget so it's testable without Qt.
    """

    return f"#{suggestion.book_id}: {suggestion.current_value!r} -> {suggestion.suggested_value!r} ({suggestion.reason})"


def format_needs_review_line(suggestion):

    return f"#{suggestion.book_id}: {suggestion.current_value!r} - {suggestion.reason}"


def format_author_group_line(group):

    return f"{group.names} -> merge into author #{group.canonical_author_id}"


def summarize_repair_results(title_results, author_results, backup_path):
    """
    Pure formatting step (apply results -> summary message), kept
    separate from the widget for the same testability reason.
    """

    title_failed = [result for result in title_results if result.error]
    author_failed = [result for result in author_results if result.error]

    lines = [
        f"Title repairs applied: {len(title_results) - len(title_failed)}/{len(title_results)}",
        f"Author merges applied: {len(author_results) - len(author_failed)}/{len(author_results)}",
        f"Backup: {backup_path}",
    ]

    failures = [f"  #{result.book_id}: {result.error}" for result in title_failed] + [
        f"  #{result.canonical_author_id}: {result.error}" for result in author_failed
    ]

    if failures:
        lines.append("")
        lines.append("Failures:")
        lines.extend(failures[:10])
        if len(failures) > 10:
            lines.append(f"  ... and {len(failures) - 10} more")

    return "\n".join(lines)


class RepairWizardWidget(QWidget):

    def __init__(self, library_service, database_path, parent=None):

        super().__init__(parent)

        self.library_service = library_service
        self.database_path = database_path
        self.applicable_suggestions = []
        self.author_groups = []

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(lambda: self._set_all_checked(True))

        select_none_button = QPushButton("Select None")
        select_none_button.clicked.connect(lambda: self._set_all_checked(False))

        apply_button = QPushButton("Apply Selected")
        apply_button.clicked.connect(self.apply_selected)

        controls_row = QHBoxLayout()
        controls_row.addWidget(preview_button)
        controls_row.addWidget(select_all_button)
        controls_row.addWidget(select_none_button)
        controls_row.addWidget(apply_button)
        controls_row.addStretch()

        self.title_list = QListWidget()
        self.needs_review_list = QListWidget()
        self.author_group_list = QListWidget()

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addLayout(controls_row)
        layout.addWidget(QLabel("Title repairs (auto-applicable):"))
        layout.addWidget(self.title_list)
        layout.addWidget(
            QLabel("Needs manual review (not auto-applicable - fix in Calibre directly):")
        )
        layout.addWidget(self.needs_review_list)
        layout.addWidget(QLabel("Duplicate author groups:"))
        layout.addWidget(self.author_group_list)
        layout.addWidget(self.status_label)

        self.preview()

    # ---------------------------------------------------------

    def preview(self):

        books = self.library_service.get_all_books()
        suggestions = MetadataRepair().suggest_for_library(books)
        self.applicable_suggestions = [s for s in suggestions if s.suggested_value]
        needs_review = [s for s in suggestions if not s.suggested_value]

        author_records = self.library_service.get_all_author_records()
        self.author_groups = AuthorDuplicateFinder().find_duplicates(author_records)

        self._fill_checkable(self.title_list, self.applicable_suggestions, format_suggestion_line)
        self._fill_readonly(self.needs_review_list, needs_review, format_needs_review_line)
        self._fill_checkable(self.author_group_list, self.author_groups, format_author_group_line)

        self.status_label.setText(
            f"{len(self.applicable_suggestions)} auto-applicable title repair(s), "
            f"{len(needs_review)} needing manual review, "
            f"{len(self.author_groups)} duplicate author group(s)."
        )

    # ---------------------------------------------------------

    @staticmethod
    def _fill_checkable(list_widget, items, formatter):

        list_widget.clear()

        for item in items:
            widget_item = QListWidgetItem(formatter(item))
            widget_item.setFlags(widget_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            widget_item.setCheckState(Qt.CheckState.Checked)
            list_widget.addItem(widget_item)

    # ---------------------------------------------------------

    @staticmethod
    def _fill_readonly(list_widget, items, formatter):

        list_widget.clear()

        for item in items:
            list_widget.addItem(formatter(item))

    # ---------------------------------------------------------

    def _set_all_checked(self, checked):

        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked

        for list_widget in (self.title_list, self.author_group_list):
            for row in range(list_widget.count()):
                list_widget.item(row).setCheckState(state)

    # ---------------------------------------------------------

    def _checked_suggestions(self):

        return [
            suggestion
            for row, suggestion in enumerate(self.applicable_suggestions)
            if self.title_list.item(row).checkState() == Qt.CheckState.Checked
        ]

    # ---------------------------------------------------------

    def _checked_author_groups(self):

        return [
            group
            for row, group in enumerate(self.author_groups)
            if self.author_group_list.item(row).checkState() == Qt.CheckState.Checked
        ]

    # ---------------------------------------------------------

    def apply_selected(self):

        checked_suggestions = self._checked_suggestions()
        checked_groups = self._checked_author_groups()

        if not checked_suggestions and not checked_groups:
            QMessageBox.warning(self, "Repair", "Nothing selected to apply.")
            return

        backup_path = backup_database(self.database_path)

        title_results = MetadataRepairApplier(self.library_service).apply(checked_suggestions)
        author_results = AuthorMerger(self.library_service).apply(checked_groups)

        QMessageBox.information(
            self, "Repair", summarize_repair_results(title_results, author_results, backup_path)
        )

        self.preview()
