"""
Cover Finder Dialog

GUI equivalent of the CLI's `covers` command: find candidate cover
images for a book from a chosen provider, preview them, and - unlike
Metadata Comparison - actually save one. This isn't blocked by an
unanswered policy question the way applying provider *metadata* back
into metadata.db is: the CLI's `covers --apply --best|--candidate N`
semantics (backup-first, resize, convert to JPEG, update has_cover)
are already decided and tested (see repair/cover_finder.py,
repair/cover_applier.py, Roadmap.md's v1.5.1 entry) - this dialog just
reuses them.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from providers.base.provider import ProviderUnavailableError
from providers.registry import PROVIDERS
from repair.backup import backup_database
from repair.cover_applier import CoverApplier
from repair.cover_finder import CoverFinder


def format_candidate_line(index, candidate):
    """
    Pure formatting step (one candidate -> one display line), kept
    separate from the dialog so it's testable without Qt or a network
    call. Mirrors main.py's run_covers() preview output.
    """

    status = "ok" if candidate.is_valid else "invalid"
    duplicate_note = " (duplicate of existing cover)" if candidate.is_duplicate else ""

    line = (
        f"[{index}] {candidate.source:<12} {candidate.width}x{candidate.height} "
        f"{candidate.format or '-':<6} score={candidate.quality_score:>3} {status}{duplicate_note}"
    )

    if candidate.issues:
        line += " - " + "; ".join(candidate.issues)

    return line


def pick_best_candidate(candidates):
    """
    Highest-scoring valid, non-duplicate candidate - same selection
    rule as the CLI's `--apply --best`. Returns None when there's
    nothing eligible.
    """

    eligible = [
        candidate for candidate in candidates if candidate.is_valid and not candidate.is_duplicate
    ]

    if not eligible:
        return None

    return max(eligible, key=lambda candidate: candidate.quality_score)


class CoverFinderDialog(QDialog):

    def __init__(self, book, library_root, library_service, database_path, parent=None):

        super().__init__(parent)

        self.book = book
        self.library_root = library_root
        self.library_service = library_service
        self.database_path = database_path
        self.candidates = []

        self.setWindowTitle(f"Find cover - #{book.id} {book.title}")
        self.setMinimumSize(520, 400)

        self.provider_box = QComboBox()
        for key, (label, _) in PROVIDERS.items():
            self.provider_box.addItem(label, userData=key)

        self.offline_checkbox = QCheckBox("Offline (cache only)")

        find_button = QPushButton("Find Candidates")
        find_button.clicked.connect(self.find_candidates)

        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Provider:"))
        controls_row.addWidget(self.provider_box)
        controls_row.addWidget(self.offline_checkbox)
        controls_row.addWidget(find_button)
        controls_row.addStretch()

        self.candidate_list = QListWidget()

        apply_best_button = QPushButton("Apply Best")
        apply_best_button.clicked.connect(self.apply_best)

        apply_selected_button = QPushButton("Apply Selected")
        apply_selected_button.clicked.connect(self.apply_selected)

        apply_row = QHBoxLayout()
        apply_row.addWidget(apply_best_button)
        apply_row.addWidget(apply_selected_button)
        apply_row.addStretch()

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addLayout(controls_row)
        layout.addWidget(self.candidate_list)
        layout.addLayout(apply_row)
        layout.addWidget(self.status_label)

        self.find_candidates()

    # ---------------------------------------------------------

    def find_candidates(self):

        provider_key = self.provider_box.currentData()
        provider_label, provider_class = PROVIDERS[provider_key]
        provider = provider_class(offline=self.offline_checkbox.isChecked())

        try:
            provider_candidates = provider.find_candidates(self.book)
        except ProviderUnavailableError as error:
            provider_candidates = []
            self.status_label.setText(f"{provider_label} unavailable: {error}")

        finder = CoverFinder(library_root=self.library_root)
        self.candidates = finder.find_candidates(self.book, provider_candidates=provider_candidates)

        self.candidate_list.clear()

        for index, candidate in enumerate(self.candidates, start=1):
            self.candidate_list.addItem(format_candidate_line(index, candidate))

        if not self.candidates:
            self.status_label.setText(
                f"No cover candidates found for #{self.book.id} {self.book.title!r}."
            )
        else:
            self.status_label.setText(f"{len(self.candidates)} candidate(s) found.")

    # ---------------------------------------------------------

    def apply_best(self):

        chosen = pick_best_candidate(self.candidates)

        if chosen is None:
            QMessageBox.warning(self, "Cover", "No valid, non-duplicate candidate to apply.")
            return

        self._apply(chosen)

    # ---------------------------------------------------------

    def apply_selected(self):

        row = self.candidate_list.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Cover", "Select a candidate from the list first.")
            return

        self._apply(self.candidates[row])

    # ---------------------------------------------------------

    def _apply(self, chosen):

        if not chosen.is_valid:
            QMessageBox.warning(
                self,
                "Cover",
                "Chosen candidate failed validation, not saving:\n" + "\n".join(chosen.issues),
            )
            return

        backup_path = backup_database(self.database_path)
        result = CoverApplier(self.library_root, self.library_service).apply(self.book, chosen)

        if result.saved:
            QMessageBox.information(
                self, "Cover", f"Cover saved.\nBackup written to:\n{backup_path}"
            )
            self.book.has_cover = True
        else:
            QMessageBox.warning(self, "Cover", f"Could not save cover: {result.error}")
