"""
Internet Archive Provider

Real implementation, mirroring OpenLibraryProvider/GoogleBooksProvider:
looks a book up by ISBN first (`q=isbn:...`, restricted to
`mediatype:texts` so audio/video/software items don't leak in), falling
back to a title/author search when there's no ISBN.

Archive.org's `advancedsearch.php` is a general-purpose search API over
every item in the archive, not a books-specific endpoint like Open
Library's `bibkeys` API - `mediatype:texts` is what keeps results to
scanned books/documents. Cover images come from the well-known
`/services/img/<identifier>` endpoint, which redirects to whatever
thumbnail the item actually has (not guaranteed to exist for every
item, same as any other provider's cover_url).

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
    INTERNET_ARCHIVE_BASE_URL,
    INTERNET_ARCHIVE_CACHE_TTL_SECONDS,
    INTERNET_ARCHIVE_MIN_REQUEST_INTERVAL_SECONDS,
    INTERNET_ARCHIVE_TIMEOUT_SECONDS,
    INTERNET_ARCHIVE_USER_AGENT,
)
from providers.base.provider import MetadataCandidate, MetadataProvider, ProviderUnavailableError
from providers.response_cache import ResponseCache

SEARCH_FIELDS = ["identifier", "title", "creator", "publisher", "description"]
SEARCH_LIMIT = 5


def default_fetcher(url, timeout, user_agent):

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class InternetArchiveProvider(MetadataProvider):

    name = "internetarchive"

    def __init__(
        self,
        fetcher=None,
        cache=None,
        offline=False,
        base_url=INTERNET_ARCHIVE_BASE_URL,
        user_agent=INTERNET_ARCHIVE_USER_AGENT,
        timeout=INTERNET_ARCHIVE_TIMEOUT_SECONDS,
        min_interval_seconds=INTERNET_ARCHIVE_MIN_REQUEST_INTERVAL_SECONDS,
    ):

        self.fetcher = fetcher or default_fetcher
        self.cache = cache or ResponseCache(
            CACHE_FOLDER / "internetarchive", INTERNET_ARCHIVE_CACHE_TTL_SECONDS
        )
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

        data = self._get(self._build_url(f"isbn:{isbn} AND mediatype:texts"))

        return [self._candidate_from_doc(doc) for doc in self._docs(data)]

    # ---------------------------------------------------------

    def _find_by_title_author(self, title, author_names):

        if not title:
            return []

        query = f'title:("{title}") AND mediatype:texts'

        if author_names and author_names != "Unknown":
            query = f'title:("{title}") AND creator:("{author_names}") AND mediatype:texts'

        data = self._get(self._build_url(query))

        return [self._candidate_from_doc(doc) for doc in self._docs(data)]

    # ---------------------------------------------------------

    @staticmethod
    def _docs(data):

        return (data.get("response") or {}).get("docs") or []

    # ---------------------------------------------------------

    def _build_url(self, query):

        params = [
            ("q", query),
            ("rows", SEARCH_LIMIT),
            ("output", "json"),
        ] + [("fl[]", field) for field in SEARCH_FIELDS]

        return f"{self.base_url}/advancedsearch.php?{urllib.parse.urlencode(params)}"

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
            raise ProviderUnavailableError(f"Could not reach Internet Archive: {error}") from error
        except TimeoutError as error:
            raise ProviderUnavailableError(
                f"Internet Archive request timed out: {error}"
            ) from error
        except json.JSONDecodeError as error:
            raise ProviderUnavailableError(
                f"Internet Archive returned an unreadable response: {error}"
            ) from error

        self.cache.set(url, data)

        return data

    # ---------------------------------------------------------

    def _throttle(self):

        elapsed = time.monotonic() - self._last_request_at

        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)

        self._last_request_at = time.monotonic()

    # ---------------------------------------------------------

    def _candidate_from_doc(self, doc):

        identifier = doc.get("identifier", "")

        return MetadataCandidate(
            source=self.name,
            title=doc.get("title", ""),
            authors=self._as_list(doc.get("creator")),
            isbn=self._first(doc.get("isbn")),
            publisher=self._first(doc.get("publisher")),
            description=self._first(doc.get("description")),
            cover_url=f"{self.base_url}/services/img/{identifier}" if identifier else "",
        )

    # ---------------------------------------------------------

    @staticmethod
    def _as_list(value):

        if not value:
            return []

        if isinstance(value, list):
            return value

        return [value]

    # ---------------------------------------------------------

    @staticmethod
    def _first(value):

        if not value:
            return ""

        if isinstance(value, list):
            return value[0] if value else ""

        return value
