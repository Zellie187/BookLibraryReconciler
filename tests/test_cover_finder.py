import io

from PIL import Image

from models.book import Book
from providers.base.provider import MetadataCandidate
from repair.cover_finder import CoverFinder


def make_image_bytes(width, height, image_format="JPEG"):

    image = Image.new("RGB", (width, height), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)

    return buffer.getvalue()


def make_book(book_id=1, path="Author/Title", has_cover=False):

    return Book(id=book_id, title="Title", path=path, has_cover=has_cover)


def test_finds_a_valid_candidate_from_a_provider():

    good_cover = make_image_bytes(1000, 1500)

    def fetcher(url):
        return good_cover

    finder = CoverFinder(fetcher=fetcher)
    book = make_book()

    provider_candidates = [
        MetadataCandidate(source="openlibrary", cover_url="https://example.com/cover.jpg")
    ]

    candidates = finder.find_candidates(book, provider_candidates=provider_candidates)

    assert len(candidates) == 1
    assert candidates[0].is_valid is True
    assert candidates[0].width == 1000
    assert candidates[0].height == 1500
    assert candidates[0].format == "JPEG"
    assert candidates[0].quality_score == 100


def test_ignores_provider_candidates_without_a_cover_url():

    def fetcher(url):
        raise AssertionError("fetcher should not be called")

    finder = CoverFinder(fetcher=fetcher)
    book = make_book()

    provider_candidates = [MetadataCandidate(source="openlibrary", cover_url="")]

    assert finder.find_candidates(book, provider_candidates=provider_candidates) == []


def test_flags_low_resolution_images():

    small_cover = make_image_bytes(100, 150)

    finder = CoverFinder(fetcher=lambda url: small_cover)
    book = make_book()

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_valid is False
    assert any("Resolution too low" in issue for issue in candidates[0].issues)


def test_flags_unusual_aspect_ratio():

    square_cover = make_image_bytes(1000, 1000)

    finder = CoverFinder(fetcher=lambda url: square_cover)
    book = make_book()

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert any("aspect ratio" in issue for issue in candidates[0].issues)


def test_flags_corrupt_image_data():

    junk_bytes = (
        b"this is not an image, just some junk bytes padded out past the minimum file size check"
        * 2
    )

    finder = CoverFinder(fetcher=lambda url: junk_bytes)
    book = make_book()

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_valid is False
    assert any("Corrupt" in issue for issue in candidates[0].issues)


def test_flags_a_too_small_file_without_attempting_to_parse_it():

    finder = CoverFinder(fetcher=lambda url: b"tiny")
    book = make_book()

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_valid is False
    assert any("too small" in issue for issue in candidates[0].issues)


def test_flags_download_failure():

    import urllib.error

    def fetcher(url):
        raise urllib.error.URLError("connection refused")

    finder = CoverFinder(fetcher=fetcher)
    book = make_book()

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_valid is False
    assert any("Download failed" in issue for issue in candidates[0].issues)


def test_finds_cover_in_user_folder_named_by_book_id(tmp_path):

    good_cover = make_image_bytes(1000, 1500)
    (tmp_path / "1.jpg").write_bytes(good_cover)

    finder = CoverFinder(fetcher=lambda url: b"", user_folder=tmp_path)
    book = make_book(book_id=1)

    candidates = finder.find_candidates(book, provider_candidates=[])

    assert len(candidates) == 1
    assert candidates[0].source == "user_folder"
    assert candidates[0].is_valid is True


def test_user_folder_ignores_files_for_other_book_ids(tmp_path):

    (tmp_path / "999.jpg").write_bytes(make_image_bytes(1000, 1500))

    finder = CoverFinder(fetcher=lambda url: b"", user_folder=tmp_path)
    book = make_book(book_id=1)

    assert finder.find_candidates(book, provider_candidates=[]) == []


def test_flags_duplicate_of_existing_cover(tmp_path):

    existing_cover = make_image_bytes(1000, 1500)

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)
    (book_dir / "cover.jpg").write_bytes(existing_cover)

    def fetcher(url):
        return existing_cover

    finder = CoverFinder(fetcher=fetcher, library_root=tmp_path)
    book = make_book(has_cover=True)

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_duplicate is True


def test_does_not_flag_a_different_cover_as_duplicate(tmp_path):

    existing_cover = make_image_bytes(1000, 1500)
    different_cover = make_image_bytes(1200, 1800)

    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)
    (book_dir / "cover.jpg").write_bytes(existing_cover)

    finder = CoverFinder(fetcher=lambda url: different_cover, library_root=tmp_path)
    book = make_book(has_cover=True)

    candidates = finder.find_candidates(
        book,
        provider_candidates=[MetadataCandidate(source="openlibrary", cover_url="https://x/y.jpg")],
    )

    assert candidates[0].is_duplicate is False
