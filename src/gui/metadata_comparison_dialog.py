"""
Metadata Comparison Dialog

Read-only GUI equivalent of the CLI's `lookup` command: Calibre's
current metadata for a book next to whatever candidates the chosen
provider (Open Library / Google Books / Internet Archive) finds for
it. No write path - deciding whether/how to apply a provider's data
back into metadata.db is still an unanswered policy question (see
docs/architecture/Roadmap.md), same reason `lookup` itself has no
`--apply`.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from providers.base.provider import ProviderUnavailableError
from providers.registry import PROVIDERS


def format_comparison(book, provider_label, candidates):
    """
    Pure formatting step (book + candidates -> display text), kept
    separate from the dialog so it's testable without constructing any
    Qt widgets or making a network call.
    """

    lines = [
        f"Calibre metadata for #{book.id}:",
        "",
        f"  Title       : {book.title}",
        f"  Author      : {book.author_names}",
        f"  ISBN        : {book.isbn or '-'}",
        f"  Publisher   : {book.publisher or '-'}",
        f"  Description : {(book.comments[:200] + '...') if book.comments else '-'}",
        "",
    ]

    if not candidates:
        lines.append(f"No {provider_label} matches found.")
        return "\n".join(lines)

    lines.append(f"{provider_label} candidates ({len(candidates)}):")

    for index, candidate in enumerate(candidates, start=1):
        lines.append("")
        lines.append(
            f"  [{index}] {candidate.title!r} by {', '.join(candidate.authors) or 'Unknown'}"
        )
        lines.append(
            f"      ISBN: {candidate.isbn or '-'}  Publisher: {candidate.publisher or '-'}"
        )
        if candidate.description:
            lines.append(f"      Description: {candidate.description[:200]}")
        if candidate.cover_url:
            lines.append(f"      Cover: {candidate.cover_url}")

    return "\n".join(lines)


class MetadataComparisonDialog(QDialog):

    def __init__(self, book, parent=None):

        super().__init__(parent)

        self.book = book

        self.setWindowTitle(f"Compare metadata - #{book.id} {book.title}")
        self.setMinimumSize(560, 420)

        self.provider_box = QComboBox()
        for key, (label, _) in PROVIDERS.items():
            self.provider_box.addItem(label, userData=key)

        self.offline_checkbox = QCheckBox("Offline (cache only)")

        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self.run_comparison)

        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Provider:"))
        controls_row.addWidget(self.provider_box)
        controls_row.addWidget(self.offline_checkbox)
        controls_row.addWidget(compare_button)
        controls_row.addStretch()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFontFamily("Consolas")

        layout = QVBoxLayout(self)
        layout.addLayout(controls_row)
        layout.addWidget(self.output)

        self.run_comparison()

    # ---------------------------------------------------------

    def run_comparison(self):

        provider_key = self.provider_box.currentData()
        provider_label, provider_class = PROVIDERS[provider_key]

        provider = provider_class(offline=self.offline_checkbox.isChecked())

        try:
            candidates = provider.find_candidates(self.book)
        except ProviderUnavailableError as error:
            self.output.setPlainText(f"{provider_label} unavailable: {error}")
            return

        self.output.setPlainText(format_comparison(self.book, provider_label, candidates))
