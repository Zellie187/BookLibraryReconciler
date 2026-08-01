import json
import urllib.error
from unittest.mock import patch

import pytest

from models.author import Author
from models.book import Book
from providers.base.provider import ProviderUnavailableError
from providers.googlebooks.googlebooks_provider import GoogleBooksProvider
from providers.response_cache import ResponseCache

ISBN_RESPONSE = {
    "items": [
        {
            "volumeInfo": {
                "title": "The Shining",
                "authors": ["Stephen King"],
                "publisher": "Anchor Books",
                "description": "Jack Torrance thought: Officious little prick.",
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "0307743658"},
                    {"type": "ISBN_13", "identifier": "9780307743657"},
                ],
                "imageLinks": {"thumbnail": "http://books.google.com/thumb.jpg"},
            }
        }
    ]
}

SEARCH_RESPONSE = {
    "items": [
        {
            "volumeInfo": {
                "title": "Doctor Sleep",
                "authors": ["Stephen King"],
                "publisher": "Scribner",
                "industryIdentifiers": [{"type": "ISBN_13", "identifier": "9781501144525"}],
                "imageLinks": {"smallThumbnail": "http://books.google.com/small.jpg"},
            }
        }
    ]
}


def make_book(isbn="", title="Doctor Sleep", author_name="Stephen King"):

    book = Book(id=1, title=title, isbn=isbn)

    if author_name:
        book.add_author(Author(name=author_name))

    return book


def make_provider(tmp_path, fetcher, offline=False):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=3600)

    return GoogleBooksProvider(
        fetcher=fetcher, cache=cache, offline=offline, min_interval_seconds=0
    )


def test_finds_by_isbn_when_present(tmp_path):

    def fetcher(url, timeout, user_agent):
        assert "isbn%3A9780307743657" in url
        return ISBN_RESPONSE

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="9780307743657")

    candidates = provider.find_candidates(book)

    assert len(candidates) == 1
    assert candidates[0].source == "googlebooks"
    assert candidates[0].title == "The Shining"
    assert candidates[0].authors == ["Stephen King"]
    assert candidates[0].isbn == "9780307743657"
    assert candidates[0].publisher == "Anchor Books"
    assert candidates[0].cover_url == "https://books.google.com/thumb.jpg"
    assert "Officious little prick" in candidates[0].description


def test_isbn_not_found_returns_empty_list(tmp_path):

    def fetcher(url, timeout, user_agent):
        return {}

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="0000000000000")

    assert provider.find_candidates(book) == []


def test_falls_back_to_title_author_search_without_isbn(tmp_path):

    def fetcher(url, timeout, user_agent):
        assert "intitle" in url and "inauthor" in url
        return SEARCH_RESPONSE

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="", title="Doctor Sleep", author_name="Stephen King")

    candidates = provider.find_candidates(book)

    assert len(candidates) == 1
    assert candidates[0].title == "Doctor Sleep"
    assert candidates[0].isbn == "9781501144525"
    assert candidates[0].cover_url == "https://books.google.com/small.jpg"


def test_no_title_and_no_isbn_returns_empty_without_calling_fetcher(tmp_path):

    def fetcher(url, timeout, user_agent):
        raise AssertionError("fetcher should not be called")

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="", title="")

    assert provider.find_candidates(book) == []


def test_cache_hit_avoids_calling_the_fetcher(tmp_path):

    calls = []

    def fetcher(url, timeout, user_agent):
        calls.append(url)
        return ISBN_RESPONSE

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="9780307743657")

    provider.find_candidates(book)
    provider.find_candidates(book)

    assert len(calls) == 1


def test_offline_mode_returns_empty_without_cache_or_network(tmp_path):

    def fetcher(url, timeout, user_agent):
        raise AssertionError("fetcher should not be called in offline mode")

    provider = make_provider(tmp_path, fetcher, offline=True)
    book = make_book(isbn="9780307743657")

    assert provider.find_candidates(book) == []


def test_offline_mode_still_uses_the_cache(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=3600)
    provider = GoogleBooksProvider(
        fetcher=lambda *a, **k: {}, cache=cache, offline=False, min_interval_seconds=0
    )
    url = provider._build_url("isbn:9780307743657")
    cache.set(url, ISBN_RESPONSE)

    def fetcher(url, timeout, user_agent):
        raise AssertionError("fetcher should not be called")

    offline_provider = GoogleBooksProvider(
        fetcher=fetcher, cache=cache, offline=True, min_interval_seconds=0
    )
    book = make_book(isbn="9780307743657")

    candidates = offline_provider.find_candidates(book)

    assert len(candidates) == 1
    assert candidates[0].title == "The Shining"


def test_network_failure_raises_provider_unavailable(tmp_path):

    def fetcher(url, timeout, user_agent):
        raise urllib.error.URLError("connection refused")

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="9780307743657")

    with pytest.raises(ProviderUnavailableError):
        provider.find_candidates(book)


def test_malformed_response_raises_provider_unavailable(tmp_path):

    def fetcher(url, timeout, user_agent):
        raise json.JSONDecodeError("bad json", "doc", 0)

    provider = make_provider(tmp_path, fetcher)
    book = make_book(isbn="9780307743657")

    with pytest.raises(ProviderUnavailableError):
        provider.find_candidates(book)


def test_api_key_is_appended_when_configured(tmp_path):

    def fetcher(url, timeout, user_agent):
        assert "key=test-key-123" in url
        return {}

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=3600)
    provider = GoogleBooksProvider(
        fetcher=fetcher, cache=cache, api_key="test-key-123", min_interval_seconds=0
    )
    book = make_book(isbn="9780307743657")

    provider.find_candidates(book)


def test_prefers_isbn_13_over_isbn_10():

    identifiers = [
        {"type": "ISBN_10", "identifier": "0307743658"},
        {"type": "ISBN_13", "identifier": "9780307743657"},
    ]

    assert GoogleBooksProvider._preferred_isbn(identifiers) == "9780307743657"


def test_throttle_sleeps_when_called_too_soon(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=3600)
    provider = GoogleBooksProvider(fetcher=lambda *a, **k: {}, cache=cache, min_interval_seconds=5)
    provider._last_request_at = 10.0

    with (
        patch("providers.googlebooks.googlebooks_provider.time.monotonic", return_value=12.0),
        patch("providers.googlebooks.googlebooks_provider.time.sleep") as mock_sleep,
    ):
        provider._throttle()

    mock_sleep.assert_called_once_with(pytest.approx(3.0))


def test_throttle_does_not_sleep_once_enough_time_has_passed(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=3600)
    provider = GoogleBooksProvider(fetcher=lambda *a, **k: {}, cache=cache, min_interval_seconds=5)
    provider._last_request_at = 0.0

    with (
        patch("providers.googlebooks.googlebooks_provider.time.monotonic", return_value=10.0),
        patch("providers.googlebooks.googlebooks_provider.time.sleep") as mock_sleep,
    ):
        provider._throttle()

    mock_sleep.assert_not_called()
