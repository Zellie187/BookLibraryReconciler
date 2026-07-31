"""
File Organizer

Computes a clean "Author/Title" folder and filename layout for each
book from its Calibre metadata, without touching the title or author
text itself - it only reorganises where the existing files live.

No automatic destructive changes: this module only ever *plans* moves.
Actually touching disk happens in OrganizeApplier (organize_applier.py),
and only for plans the caller has explicitly chosen to apply.
"""

import re
from dataclasses import dataclass, field

_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_TRAILING_JUNK = re.compile(r"[.\s]+$")

MAX_COMPONENT_LENGTH = 150


def sanitize_component(text, fallback="Unknown"):
    """
    Make a string safe to use as a single Windows/POSIX path component.
    """

    text = (text or "").strip()
    text = _ILLEGAL_CHARS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = _TRAILING_JUNK.sub("", text)

    if not text:
        text = fallback

    return text[:MAX_COMPONENT_LENGTH]


@dataclass
class FormatRename:

    format: str = ""
    old_name: str = ""
    new_name: str = ""

    @property
    def changed(self):
        return self.old_name != self.new_name


@dataclass
class OrganizePlan:

    book_id: int = 0
    title: str = ""
    author: str = ""

    current_path: str = ""
    proposed_path: str = ""

    format_renames: list[FormatRename] = field(default_factory=list)

    @property
    def folder_changed(self):
        return self.current_path != self.proposed_path

    @property
    def formats_changed(self):
        return any(rename.changed for rename in self.format_renames)

    @property
    def has_changes(self):
        return self.folder_changed or self.formats_changed


class FileOrganizer:
    """
    Builds an Author/Title reorganization plan for a set of Book objects.
    """

    def build_plan(self, books):

        plans = []
        used_folders = {}

        for book in sorted(books, key=lambda b: b.id):

            author = sanitize_component(
                book.authors[0].name if book.authors else "Unknown"
            )
            title = sanitize_component(
                book.title, fallback=f"Untitled ({book.id})"
            )

            proposed_path = f"{author}/{title}"
            folder_key = proposed_path.lower()

            if folder_key in used_folders:
                proposed_path = f"{author}/{title} ({book.id})"

            used_folders.setdefault(folder_key, []).append(book.id)

            format_renames = [
                FormatRename(
                    format=format_file.format,
                    old_name=format_file.name,
                    new_name=title,
                )
                for format_file in book.format_files
            ]

            plans.append(
                OrganizePlan(
                    book_id=book.id,
                    title=book.title,
                    author=author,
                    current_path=book.path,
                    proposed_path=proposed_path,
                    format_renames=format_renames,
                )
            )

        return plans

    # ---------------------------------------------------------

    def plans_with_changes(self, books):

        return [plan for plan in self.build_plan(books) if plan.has_changes]
