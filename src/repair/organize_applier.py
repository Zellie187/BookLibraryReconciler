"""
Organize Applier

Carries out an Author/Title reorganization plan (see file_organizer.py):
moves each book's folder on disk, renames its format files, and updates
Calibre's metadata.db so the library stays in sync.

Every plan is applied independently - one book failing to move does not
stop the rest, and is reported back instead of raised.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ApplyResult:

    book_id: int = 0
    proposed_path: str = ""
    moved: bool = False
    renamed_formats: list[str] = field(default_factory=list)
    error: str = ""


class OrganizeApplier:

    def __init__(self, library_root, library_service):

        self.library_root = Path(library_root)
        self.library_service = library_service

    # ---------------------------------------------------------

    def apply(self, plans):

        results = []

        for plan in plans:

            results.append(self._apply_one(plan))

        return results

    # ---------------------------------------------------------

    def _apply_one(self, plan):

        result = ApplyResult(book_id=plan.book_id, proposed_path=plan.proposed_path)

        current_dir = self.library_root / plan.current_path
        proposed_dir = self.library_root / plan.proposed_path

        if plan.folder_changed:

            if not current_dir.exists():
                result.error = f"Source folder not found: {current_dir}"
                return result

            if proposed_dir.exists() and proposed_dir != current_dir:
                result.error = f"Destination already exists: {proposed_dir}"
                return result

            try:
                proposed_dir.parent.mkdir(parents=True, exist_ok=True)
                current_dir.rename(proposed_dir)
            except OSError as error:
                result.error = f"Move failed: {error}"
                return result

            result.moved = True

        for rename in plan.format_renames:

            if not rename.changed:
                continue

            old_file = proposed_dir / f"{rename.old_name}.{rename.format.lower()}"
            new_file = proposed_dir / f"{rename.new_name}.{rename.format.lower()}"

            if not old_file.exists():
                result.error = f"Format file not found: {old_file}"
                continue

            if new_file.exists() and new_file != old_file:
                result.error = f"Format destination already exists: {new_file}"
                continue

            try:
                old_file.rename(new_file)
            except OSError as error:
                result.error = f"Format rename failed: {error}"
                continue

            self.library_service.rename_format(plan.book_id, rename.format, rename.new_name)

            result.renamed_formats.append(rename.new_name)

        if plan.folder_changed and not result.error:
            self.library_service.update_book_path(plan.book_id, plan.proposed_path)

        return result
