"""
Metadata Engine

Ties completeness scoring, validity checks, and repair suggestions
together into a single per-book and library-wide analysis. This is the
"intelligence layer" from the project spec: Import -> Analyse -> Identify
Problems, before anything reaches the Repair Engine's file operations.
"""

from dataclasses import dataclass, field

from metadata.metadata_repair import MetadataRepair
from metadata.metadata_score import MetadataScorer
from metadata.metadata_validator import MetadataValidator


@dataclass
class BookAnalysis:

    book_id: int = 0
    title: str = ""
    score: int = 0
    failed_checks: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    repair_suggestions: list = field(default_factory=list)

    @property
    def needs_attention(self):

        return self.score < 100 or bool(self.issues)


class MetadataEngine:

    def __init__(self, scorer=None, validator=None, repair=None):

        self.scorer = scorer or MetadataScorer()
        self.validator = validator or MetadataValidator()
        self.repair = repair or MetadataRepair()

    # ---------------------------------------------------------

    def analyze_book(self, book):

        score_report = self.scorer.score_book(book)
        validation_report = self.validator.validate_book(book)
        repair_suggestions = self.repair.suggest_for_book(book)

        return BookAnalysis(
            book_id=book.id,
            title=book.title,
            score=score_report.score,
            failed_checks=score_report.failed,
            issues=[issue.message for issue in validation_report.issues],
            repair_suggestions=repair_suggestions,
        )

    # ---------------------------------------------------------

    def analyze_library(self, books):

        return [self.analyze_book(book) for book in books]

    # ---------------------------------------------------------

    def books_needing_attention(self, books):

        return [analysis for analysis in self.analyze_library(books) if analysis.needs_attention]
