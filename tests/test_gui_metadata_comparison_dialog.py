from gui.metadata_comparison_dialog import format_comparison
from models.author import Author
from models.book import Book
from providers.base.provider import MetadataCandidate


def make_book(
    book_id=1, title="Doctor Sleep", isbn="", publisher="", comments="", author_name="Stephen King"
):

    book = Book(id=book_id, title=title, isbn=isbn, publisher=publisher, comments=comments)

    if author_name:
        book.add_author(Author(name=author_name))

    return book


def test_shows_calibre_metadata_header():

    text = format_comparison(
        make_book(isbn="9781501144525", publisher="Scribner"), "Open Library", []
    )

    assert "Calibre metadata for #1:" in text
    assert "Doctor Sleep" in text
    assert "Stephen King" in text
    assert "9781501144525" in text
    assert "Scribner" in text


def test_no_candidates_reports_no_matches():

    text = format_comparison(make_book(), "Open Library", [])

    assert "No Open Library matches found." in text


def test_lists_each_candidate_with_isbn_and_publisher():

    candidates = [
        MetadataCandidate(
            source="openlibrary",
            title="Doctor Sleep",
            authors=["Stephen King"],
            isbn="9781501144525",
            publisher="Scribner",
        ),
        MetadataCandidate(
            source="openlibrary", title="Doctor Sleep (large print)", authors=["Stephen King"]
        ),
    ]

    text = format_comparison(make_book(), "Open Library", candidates)

    assert "Open Library candidates (2):" in text
    assert "[1] 'Doctor Sleep' by Stephen King" in text
    assert "ISBN: 9781501144525  Publisher: Scribner" in text
    assert "[2] 'Doctor Sleep (large print)' by Stephen King" in text
    assert "ISBN: -  Publisher: -" in text


def test_candidate_with_no_authors_shows_unknown():

    candidates = [MetadataCandidate(source="openlibrary", title="Mystery Book", authors=[])]

    text = format_comparison(make_book(), "Open Library", candidates)

    assert "by Unknown" in text


def test_candidate_description_and_cover_url_included_when_present():

    candidates = [
        MetadataCandidate(
            source="openlibrary",
            title="Doctor Sleep",
            description="A sequel to The Shining.",
            cover_url="https://covers.openlibrary.org/b/id/1-L.jpg",
        )
    ]

    text = format_comparison(make_book(), "Open Library", candidates)

    assert "Description: A sequel to The Shining." in text
    assert "Cover: https://covers.openlibrary.org/b/id/1-L.jpg" in text


def test_missing_calibre_description_shows_dash():

    text = format_comparison(make_book(comments=""), "Open Library", [])

    assert "Description : -" in text


def test_long_calibre_description_is_truncated():

    long_comment = "x" * 500
    text = format_comparison(make_book(comments=long_comment), "Open Library", [])

    assert "x" * 200 + "..." in text
    assert "x" * 500 not in text
