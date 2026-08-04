"""
Organize Wizard Widget

GUI equivalent of the CLI's `organize` command: preview an Author/
Title reorganization plan for the whole library, let the user
deselect individual books, then apply only the checked ones. Not
blocked by an unanswered policy question - the CLI's `organize
--apply` semantics (backup-first, one book failing doesn't stop the
rest) were already decided and tested; per-item selection here is
strictly *safer* than the CLI's all-or-nothing apply, not a new
policy.
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

from repair.backup import backup_database
from repair.file_organizer import FileOrganizer
from repair.organize_applier import OrganizeApplier


def format_plan_line(plan):
    """
    Pure formatting step (one plan -> one display line), kept separate
    from the widget so it's testable without Qt.
    """

    line = f"#{plan.book_id} {plan.title!r}: {plan.current_path} -> {plan.proposed_path}"

    if plan.formats_changed:
        renamed = [rename.new_name for rename in plan.format_renames if rename.changed]
        line += f" (formats: {', '.join(renamed)})"

    return line


def summarize_apply_results(results, backup_path):
    """
    Pure formatting step (apply results -> summary message), kept
    separate from the widget for the same testability reason.
    """

    failed = [result for result in results if result.error]
    succeeded = len(results) - len(failed)

    lines = [f"Applied {succeeded}/{len(results)} change(s).", f"Backup: {backup_path}"]

    if failed:
        lines.append("")
        lines.append("Failures:")
        for result in failed[:10]:
            lines.append(f"  #{result.book_id}: {result.error}")
        if len(failed) > 10:
            lines.append(f"  ... and {len(failed) - 10} more")

    return "\n".join(lines)


class OrganizeWizardWidget(QWidget):

    def __init__(self, library_service, library_root, database_path, parent=None):

        super().__init__(parent)

        self.library_service = library_service
        self.library_root = library_root
        self.database_path = database_path
        self.plans = []

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

        self.plan_list = QListWidget()

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addLayout(controls_row)
        layout.addWidget(self.plan_list)
        layout.addWidget(self.status_label)

        self.preview()

    # ---------------------------------------------------------

    def preview(self):

        books = self.library_service.get_all_books()
        self.plans = FileOrganizer().plans_with_changes(books)

        self.plan_list.clear()

        for plan in self.plans:
            item = QListWidgetItem(format_plan_line(plan))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.plan_list.addItem(item)

        if self.plans:
            self.status_label.setText(f"{len(self.plans)} book(s) need reorganizing.")
        else:
            self.status_label.setText("No reorganization needed - every book is already in place.")

    # ---------------------------------------------------------

    def _set_all_checked(self, checked):

        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked

        for row in range(self.plan_list.count()):
            self.plan_list.item(row).setCheckState(state)

    # ---------------------------------------------------------

    def _checked_plans(self):

        return [
            plan
            for row, plan in enumerate(self.plans)
            if self.plan_list.item(row).checkState() == Qt.CheckState.Checked
        ]

    # ---------------------------------------------------------

    def apply_selected(self):

        checked_plans = self._checked_plans()

        if not checked_plans:
            QMessageBox.warning(self, "Reorganize", "No books selected to apply.")
            return

        backup_path = backup_database(self.database_path)
        results = OrganizeApplier(self.library_root, self.library_service).apply(checked_plans)

        QMessageBox.information(self, "Reorganize", summarize_apply_results(results, backup_path))

        self.preview()
