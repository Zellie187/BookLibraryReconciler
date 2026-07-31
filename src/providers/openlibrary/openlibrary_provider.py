"""
Open Library Provider

Real implementation: looks a book up by ISBN first (the bibkeys API,
one exact record), falling back to a title/author search (multiple
loosely-matched candidates) when there's no ISBN to key off of.

The actual HTTP call is a small injectable `fetcher(url, timeout,
user_agent) -> dict` function - the default uses stdlib urllib, but
tests inject a fake one so the suite never makes real network calls.
Responses are cached to disk (see response_cache.py) so repeated
lookups - and "offline" mode - don't need the network at all.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

from config.paths import CACHE_FOLDER
from config.providers import (
    OPEN_LIBRARY_BASE_URL,
    OPEN_LIBRARY_CACHE_TTL_SECONDS,
    OPEN_LIBRARY_MIN_REQUEST_INTERVAL_SECONDS,
    OPEN_LIBRARY_TIMEOUT_SECONDS,
    OPEN_LIBRARY_USER_AGENT,
)
from providers.base.provider import MetadataCandidate, MetadataProvider, ProviderUnavailableError
from providers.response_cache import ResponseCache

SEARCH_FIELDS = "title,author_name,isbn,publisher,cover_i"
SEARCH_LIMIT = 5


def default_fetcher(url, timeout, user_agent):

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class OpenLibraryProvider(MetadataProvider):

    name = "openlibrary"

    def __init__(
        self,
        fetcher=None,
        cache=None,
        offline=False,
        base_url=OPEN_LIBRARY_BASE_URL,
        user_agent=OPEN_LIBRARY_USER_AGENT,
        timeout=OPEN_LIBRARY_TIMEOUT_SECONDS,
        min_interval_seconds=OPEN_LIBRARY_MIN_REQUEST_INTERVAL_SECONDS,
    ):

        self.fetcher = fetcher or default_fetcher
        self.cache = cache or ResponseCache(CACHE_FOLDER / "openlibrary", OPEN_LIBRARY_CACHE_TTL_SECONDS)
        self.offline = offline
        self.base_url = base_url
        self.user_agent = user_agent
        self.timeout = timeout
        self.min_interval_seconds = min_interval_seconds

        self._last_request_at = 0.0

    # ---------------------------------------------------------

    def find_candidates(self, book):

        if book.isbn:
            return self._find_by_isbn(book.isbn)

        return self._find_by_title_author(book.title, book.author_names)

    # ---------------------------------------------------------

    def _find_by_isbn(self, isbn):

        url = f"{self.base_url}/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

        data = self._get(url)

        record = data.get(f"ISBN:{isbn}")

        if not record:
            return []

        return [self._candidate_from_isbn_record(record)]

    # ---------------------------------------------------------

    def _find_by_title_author(self, title, author_names, limit=SEARCH_LIMIT):

        if not title:
            return []

        params = {"title": title, "limit": limit, "fields": SEARCH_FIELDS}

        if author_names and author_names != "Unknown":
            params["author"] = author_names

        url = f"{self.base_url}/search.json?{urllib.parse.urlencode(params)}"

        data = self._get(url)

        return [self._candidate_from_search_doc(doc) for doc in data.get("docs", [])]

    # ---------------------------------------------------------

    def _get(self, url):

        cached = self.cache.get(url)

        if cached is not None:
            return cached

        if self.offline:
            return {}

        self._throttle()

        try:
            data = self.fetcher(url, timeout=self.timeout, user_agent=self.user_agent)
        except urllib.error.URLError as error:
            raise ProviderUnavailableError(f"Could not reach Open Library: {error}") from error
        except TimeoutError as error:
            raise ProviderUnavailableError(f"Open Library request timed out: {error}") from error
        except json.JSONDecodeError as error:
            raise ProviderUnavailableError(f"Open Library returned an unreadable response: {error}") from error

        self.cache.set(url, data)

        return data

    # ---------------------------------------------------------

    def _throttle(self):

        elapsed = time.monotonic() - self._last_request_at

        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)

        self._last_request_at = time.monotonic()

    # ---------------------------------------------------------

    def _candidate_from_isbn_record(self, record):

        identifiers = record.get("identifiers") or {}
        isbn = (identifiers.get("isbn_13") or identifiers.get("isbn_10") or [""])[0]

        publishers = record.get("publishers") or [{}]
        publisher = publishers[0].get("name", "")

        cover = record.get("cover") or {}
        cover_url = cover.get("large") or cover.get("medium") or cover.get("small") or ""

        return MetadataCandidate(
            source=self.name,
            title=record.get("title", ""),
            authors=[author.get("name", "") for author in record.get("authors", [])],
            isbn=isbn,
            publisher=publisher,
            description=self._extract_description(record),
            cover_url=cover_url,
        )

    # ---------------------------------------------------------

    def _candidate_from_search_doc(self, doc):

        isbns = doc.get("isbn") or []
        publishers = doc.get("publisher") or []
        cover_id = doc.get("cover_i")

        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ""

        return MetadataCandidate(
            source=self.name,
            title=doc.get("title", ""),
            authors=list(doc.get("author_name") or []),
            isbn=isbns[0] if isbns else "",
            publisher=publishers[0] if publishers else "",
            description="",
            cover_url=cover_url,
        )

    # ---------------------------------------------------------

    @staticmethod
    def _extract_description(record):

        excerpts = record.get("excerpts") or []

        if excerpts:
            return excerpts[0].get("text", "")

        notes = record.get("notes")

        return notes if isinstance(notes, str) else ""
