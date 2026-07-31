import io
from unittest.mock import MagicMock

from PIL import Image

from models.book import Book
from repair.cover_applier import CoverApplier
from repair.cover_finder import CoverCandidate


def make_image_bytes(width, height):

    image = Image.new("RGB", (width, height), color="blue")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    return buffer.getvalue()


def test_saves_cover_and_updates_has_cover(tmp_path):

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)

    book = Book(id=1, title="Title", path="Author/Title", has_cover=False)
    candidate = CoverCandidate(source="openlibrary", image_bytes=make_image_bytes(1000, 1500))

    library_service = MagicMock()
    applier = CoverApplier(tmp_path, library_service)

    result = applier.apply(book, candidate)

    assert result.saved is True
    assert result.error == ""
    assert (book_dir / "cover.jpg").exists()
    library_service.update_has_cover.assert_called_once_with(1, True)


def test_resizes_oversized_images_down_to_max_dimension(tmp_path):

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)

    book = Book(id=1, title="Title", path="Author/Title")
    candidate = CoverCandidate(source="openlibrary", image_bytes=make_image_bytes(3000, 4500))

    applier = CoverApplier(tmp_path, MagicMock())
    applier.apply(book, candidate)

    with Image.open(book_dir / "cover.jpg") as saved:
        assert max(saved.size) <= 800


def test_missing_book_folder_is_reported_not_raised(tmp_path):

    book = Book(id=1, title="Title", path="Nonexistent/Folder")
    candidate = CoverCandidate(source="openlibrary", image_bytes=make_image_bytes(1000, 1500))

    library_service = MagicMock()
    applier = CoverApplier(tmp_path, library_service)

    result = applier.apply(book, candidate)

    assert result.saved is False
    assert "not found" in result.error
    library_service.update_has_cover.assert_not_called()


def test_candidate_with_no_image_data_is_reported_not_raised(tmp_path):

    book = Book(id=1, title="Title", path="Author/Title")
    candidate = CoverCandidate(source="openlibrary", image_bytes=b"")

    result = CoverApplier(tmp_path, MagicMock()).apply(book, candidate)

    assert result.saved is False
    assert "no image data" in result.error.lower()


def test_corrupt_image_data_is_reported_not_raised(tmp_path):

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)

    book = Book(id=1, title="Title", path="Author/Title")
    candidate = CoverCandidate(
        source="openlibrary", image_bytes=b"not a real image but long enough to try" * 5
    )

    result = CoverApplier(tmp_path, MagicMock()).apply(book, candidate)

    assert result.saved is False
    assert "Could not process image" in result.error
