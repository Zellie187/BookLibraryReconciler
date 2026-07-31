"""
Cover Applier

Saves an approved CoverCandidate as a book's cover: resizes it to a
standard maximum dimension (Calibre itself keeps covers modest-sized,
not full source resolution), converts to JPEG (the format Calibre
expects at "cover.jpg" regardless of the source format), and updates
`books.has_cover`. Backup-first, like every other applier in this
project - see main.py's run_covers().
"""

import io
from dataclasses import dataclass
from pathlib import Path

MAX_DIMENSION = 800


@dataclass
class CoverApplyResult:

    book_id: int = 0
    saved: bool = False
    error: str = ""


class CoverApplier:

    def __init__(self, library_root, library_service):

        self.library_root = Path(library_root)
        self.library_service = library_service

    # ---------------------------------------------------------

    def apply(self, book, candidate):

        result = CoverApplyResult(book_id=book.id)

        if not candidate.image_bytes:
            result.error = "Candidate has no image data"
            return result

        try:
            from PIL import Image
        except ImportError:
            result.error = "Cover saving needs the optional 'Pillow' dependency - install it with: pip install Pillow"
            return result

        try:
            image = Image.open(io.BytesIO(candidate.image_bytes))
            image = image.convert("RGB")
            image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
        except Exception as error:  # noqa: BLE001 - already validated upstream, but stay defensive
            result.error = f"Could not process image: {error}"
            return result

        cover_dir = self.library_root / book.path

        if not cover_dir.exists():
            result.error = f"Book folder not found: {cover_dir}"
            return result

        cover_path = cover_dir / "cover.jpg"

        try:
            image.save(cover_path, "JPEG", quality=90)
        except OSError as error:
            result.error = f"Could not save cover: {error}"
            return result

        self.library_service.update_has_cover(book.id, True)

        result.saved = True

        return result
