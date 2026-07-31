"""
Cover Finder

Finds, downloads, and validates candidate cover images for a book -
Book -> Provider -> Download -> Validate, matching the spec's Cover
Download Engine workflow. Never saves anything; see
repair/cover_applier.py for the explicit, backup-first apply step.

Sources:
- Open Library, via the cover_url already present on a
  MetadataCandidate from OpenLibraryProvider.find_candidates() - the
  caller passes those in, so a `lookup`-style call that already fetched
  them doesn't pay for a second round-trip.
- An optional local "user folder" - a directory the user drops cover
  images into, named by Calibre book id (`<book_id>.jpg`/`.png`/`.webp`).

Google Books, Internet Archive, and Amazon (metadata-only) are not
implemented - they need their own provider work first (see Roadmap.md).

Image validation needs the optional Pillow dependency, lazy-imported
so the rest of the app works without it installed.
"""

import hashlib
import io
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

MIN_WIDTH = 300
MIN_HEIGHT = 300
MIN_ASPECT_RATIO = 1.1  # height / width - book covers are portrait, not square
MAX_ASPECT_RATIO = 2.2
MIN_FILE_SIZE_BYTES = 100
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

# A typical trade paperback cover is roughly this many pixels - used
# only to normalize resolution into a 0-100 "quality" number, not as a
# validation cutoff.
TARGET_PIXELS = 1000 * 1500

USER_FOLDER_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def default_fetcher(url, timeout=10):

    request = urllib.request.Request(url, headers={"User-Agent": "BookLibraryReconciler/1.0"})

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


@dataclass
class CoverCandidate:

    source: str = ""
    origin: str = ""  # URL or local file path, for display only
    width: int = 0
    height: int = 0
    format: str = ""
    size_bytes: int = 0
    quality_score: int = 0
    issues: list[str] = field(default_factory=list)
    is_duplicate: bool = False
    image_bytes: bytes = field(default=b"", repr=False)

    @property
    def is_valid(self):

        return not self.issues


class CoverFinder:

    def __init__(self, fetcher=None, library_root=None, user_folder=None):

        self.fetcher = fetcher or default_fetcher
        self.library_root = Path(library_root) if library_root else None
        self.user_folder = Path(user_folder) if user_folder else None

    # ---------------------------------------------------------

    def find_candidates(self, book, provider_candidates=None):

        candidates = []

        for provider_candidate in provider_candidates or []:

            if not provider_candidate.cover_url:
                continue

            candidates.append(
                self._build_candidate(provider_candidate.source, provider_candidate.cover_url)
            )

        if self.user_folder:
            candidates.extend(self._find_in_user_folder(book))

        self._flag_duplicates(book, candidates)

        return candidates

    # ---------------------------------------------------------

    def _build_candidate(self, source, url):

        candidate = CoverCandidate(source=source, origin=url)

        try:
            image_bytes = self.fetcher(url)
        except urllib.error.URLError as error:
            candidate.issues.append(f"Download failed: {error}")
            return candidate
        except TimeoutError as error:
            candidate.issues.append(f"Download timed out: {error}")
            return candidate

        self._validate(candidate, image_bytes)

        return candidate

    # ---------------------------------------------------------

    def _find_in_user_folder(self, book):

        candidates = []

        for extension in USER_FOLDER_EXTENSIONS:

            path = self.user_folder / f"{book.id}{extension}"

            if not path.exists():
                continue

            candidate = CoverCandidate(source="user_folder", origin=str(path))

            try:
                image_bytes = path.read_bytes()
            except OSError as error:
                candidate.issues.append(f"Could not read file: {error}")
                candidates.append(candidate)
                continue

            self._validate(candidate, image_bytes)
            candidates.append(candidate)

        return candidates

    # ---------------------------------------------------------

    def _validate(self, candidate, image_bytes):

        candidate.image_bytes = image_bytes
        candidate.size_bytes = len(image_bytes)

        if candidate.size_bytes < MIN_FILE_SIZE_BYTES:
            candidate.issues.append(f"File too small ({candidate.size_bytes} bytes)")
            return

        if candidate.size_bytes > MAX_FILE_SIZE_BYTES:
            candidate.issues.append(f"File too large ({candidate.size_bytes:,} bytes)")

        try:
            from PIL import Image
        except ImportError as error:
            raise ImportError(
                "Cover validation needs the optional 'Pillow' dependency - "
                "install it with: pip install Pillow"
            ) from error

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
            # verify() invalidates the image object for further use - reopen it.
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            image_format = (image.format or "").upper()
        except Exception as error:  # noqa: BLE001
            # Arbitrary external image bytes can raise many different PIL
            # exception types - any parse failure here just means "corrupt".
            candidate.issues.append(f"Corrupt or unreadable image: {error}")
            return

        candidate.width = width
        candidate.height = height
        candidate.format = image_format

        if image_format not in SUPPORTED_FORMATS:
            candidate.issues.append(f"Unsupported format: {image_format or 'unknown'}")

        if width == 0 or height == 0:
            candidate.issues.append("Zero-dimension image")
        else:

            if width < MIN_WIDTH or height < MIN_HEIGHT:
                candidate.issues.append(
                    f"Resolution too low: {width}x{height} (minimum {MIN_WIDTH}x{MIN_HEIGHT})"
                )

            aspect_ratio = height / width

            if not (MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO):
                candidate.issues.append(
                    f"Unusual aspect ratio for a book cover: {aspect_ratio:.2f}"
                )

            candidate.quality_score = min(
                100, max(0, round((width * height) / TARGET_PIXELS * 100))
            )

    # ---------------------------------------------------------

    def _flag_duplicates(self, book, candidates):

        existing_hash = self._existing_cover_hash(book)

        if not existing_hash:
            return

        for candidate in candidates:

            if (
                candidate.image_bytes
                and hashlib.sha256(candidate.image_bytes).hexdigest() == existing_hash
            ):
                candidate.is_duplicate = True

    # ---------------------------------------------------------

    def _existing_cover_hash(self, book):

        if not self.library_root or not book.has_cover:
            return None

        cover_path = self.library_root / book.path / "cover.jpg"

        if not cover_path.exists():
            return None

        try:
            return hashlib.sha256(cover_path.read_bytes()).hexdigest()
        except OSError:
            return None
