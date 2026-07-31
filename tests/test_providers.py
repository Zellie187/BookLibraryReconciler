import pytest

from models.author import Author
from models.book import Book
from providers.calibre.calibre_provider import CalibreProvider
from providers.googlebooks.googlebooks_provider import GoogleBooksProvider
from providers.isbndb.isbndb_provider import IsbndbProvider


def test_calibre_provider_returns_existing_metadata_as_a_candidate():

    book = Book(id=1, title="Doctor Sleep", isbn="9781501144525", comments="A book.")
    book.add_author(Author(name="Stephen King"))

    candidates = CalibreProvider().find_candidates(book)

    assert len(candidates) == 1
    assert candidates[0].source == "calibre"
    assert candidates[0].title == "Doctor Sleep"
    assert candidates[0].authors == ["Stephen King"]
    assert candidates[0].isbn == "9781501144525"


@pytest.mark.parametrize(
    "provider_class",
    [GoogleBooksProvider, IsbndbProvider],
)
def test_unimplemented_providers_raise_not_implemented(provider_class):

    book = Book(id=1, title="Doctor Sleep")

    with pytest.raises(NotImplementedError):
        provider_class().find_candidates(book)
