"""
Google Books Provider

Real implementation, mirroring OpenLibraryProvider's pattern: looks a
book up by ISBN first (`q=isbn:...`, generally one strong match),
falling back to a title/author search (`q=intitle:...+inauthor:...`,
several loosely-matched candidates) when there's no ISBN.

The actual HTTP call is a small injectable `fetcher(url, timeout,
user_agent) -> dict` function - the default uses stdlib urllib, but
tests inject a fake one so the suite never makes real network calls.
Responses are cached to disk (see response_cache.py) so repeated
lookups - and "offline" mode - don't need the network at all.

An API key is optional (Google Books works unauthenticated at a lower
rate limit); when `GOOGLE_BOOKS_API_KEY` is set it's appended to every
request URL.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

from config.paths import CACHE_FOLDER
from config.providers import (
    GOOGLE_BOOKS_API_KEY,
    GOOGLE_BOOKS_BASE_URL,
    GOOGLE_BOOKS_CACHE_TTL_SECONDS,
    GOOGLE_BOOKS_MIN_REQUEST_INTERVAL_SECONDS,
    GOOGLE_BOOKS_TIMEOUT_SECONDS,
)
from providers.base.provider import MetadataCandidate, MetadataProvider, ProviderUnavailableError
from providers.response_cache import ResponseCache

USER_AGENT = "BookLibraryReconciler/1.0 (+https://github.com/Zellie187/BookLibraryReconciler)"
SEARCH_LIMIT = 5


def default_fetcher(url, timeout, user_agent):

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class GoogleBooksProvider(MetadataProvider):

    name = "googlebooks"

    def __init__(
        self,
        fetcher=None,
        cache=None,
        offline=False,
        base_url=GOOGLE_BOOKS_BASE_URL,
        api_key=GOOGLE_BOOKS_API_KEY,
        user_agent=USER_AGENT,
        timeout=GOOGLE_BOOKS_TIMEOUT_SECONDS,
        min_interval_seconds=GOOGLE_BOOKS_MIN_REQUEST_INTERVAL_SECONDS,
    ):

        self.fetcher = fetcher or default_fetcher
        self.cache = cache or ResponseCache(
            CACHE_FOLDER / "googlebooks", GOOGLE_BOOKS_CACHE_TTL_SECONDS
        )
        self.offline = offline
        self.base_url = base_url
        self.api_key = api_key
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

        data = self._get(self._build_url(f"isbn:{isbn}"))

        return [self._candidate_from_item(item) for item in data.get("items") or []]

    # ---------------------------------------------------------

    def _find_by_title_author(self, title, author_names):

        if not title:
            return []

        query = f"intitle:{title}"

        if author_names and author_names != "Unknown":
            query += f"+inauthor:{author_names}"

        data = self._get(self._build_url(query))

        return [self._candidate_from_item(item) for item in data.get("items") or []]

    # ---------------------------------------------------------

    def _build_url(self, query):

        params = {"q": query, "maxResults": SEARCH_LIMIT}

        if self.api_key:
            params["key"] = self.api_key

        return f"{self.base_url}/volumes?{urllib.parse.urlencode(params)}"

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
            raise ProviderUnavailableError(f"Could not reach Google Books: {error}") from error
        except TimeoutError as error:
            raise ProviderUnavailableError(f"Google Books request timed out: {error}") from error
        except json.JSONDecodeError as error:
            raise ProviderUnavailableError(
                f"Google Books returned an unreadable response: {error}"
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

    def _candidate_from_item(self, item):

        info = item.get("volumeInfo") or {}
        identifiers = info.get("industryIdentifiers") or []

        isbn = self._preferred_isbn(identifiers)

        image_links = info.get("imageLinks") or {}
        cover_url = (
            image_links.get("extraLarge")
            or image_links.get("large")
            or image_links.get("medium")
            or image_links.get("thumbnail")
            or image_links.get("smallThumbnail")
            or ""
        )
        # Google Books serves cover images over http:// even when the
        # rest of the API is https - upgrade so a downstream fetch
        # (e.g. the Cover Download Engine) doesn't get blocked/mixed-content.
        if cover_url.startswith("http://"):
            cover_url = "https://" + cover_url[len("http://") :]

        return MetadataCandidate(
            source=self.name,
            title=info.get("title", ""),
            authors=list(info.get("authors") or []),
            isbn=isbn,
            publisher=info.get("publisher", ""),
            description=info.get("description", ""),
            cover_url=cover_url,
        )

    # ---------------------------------------------------------

    @staticmethod
    def _preferred_isbn(identifiers):

        by_type = {entry.get("type"): entry.get("identifier", "") for entry in identifiers}

        return by_type.get("ISBN_13") or by_type.get("ISBN_10") or ""
