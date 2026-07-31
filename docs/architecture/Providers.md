# Provider System

External metadata sources are plugins, all implementing the same
interface (`src/providers/base/provider.py`):

```python
class MetadataProvider(ABC):
    name = "base"

    @abstractmethod
    def find_candidates(self, book) -> list[MetadataCandidate]:
        """Return [] when nothing found. Raise ProviderUnavailableError
        when the provider itself couldn't be reached or its response
        was unusable - distinct from a confirmed empty result."""
```

`MetadataCandidate` is a plain dataclass: `source`, `title`, `authors`,
`isbn`, `publisher`, `description`, `cover_url`. It's a provider's
*proposed* version of a book's metadata, meant for comparison, not for
direct application - nothing in this project writes a candidate's
values back into `metadata.db` automatically (see `Roadmap.md`).

```
providers/
    base/            MetadataProvider, MetadataCandidate, ProviderUnavailableError
    response_cache.py  file-based JSON cache keyed by URL, shared by any provider
    calibre/          working - wraps a book's own existing metadata
    openlibrary/       working - real HTTP calls, see below
    googlebooks/       stub - raises NotImplementedError (planned v2.1.0)
    isbndb/            stub - raises NotImplementedError (planned v2.1.0)
```

## Why Calibre is a "provider" too

The original spec's domain-model diagram is:

```
Calibre -> Book Object -> Open Library -> Improved Book Object -> Repair Engine
```

`CalibreProvider.find_candidates(book)` returns the book's own current
metadata as a single `MetadataCandidate` with `source="calibre"`. This
means comparing "what we have" against "what Open Library says" is
just comparing two lists of `MetadataCandidate` through the same
interface - no special casing for the local source. `OpenLibraryProvider`
being real now means this comparison is real too - see `python run.py
lookup <book_id>`.

## `OpenLibraryProvider` - how it actually works

Two lookup strategies, in order of preference:

1. **ISBN lookup** (`book.isbn` present) - Open Library's `bibkeys`
   API returns one exact record, or nothing if the ISBN isn't in their
   catalog. Strong signal, one candidate.
2. **Title/author search** (no ISBN) - `search.json`, up to 5 loosely
   matched candidates, `title` required (an author-less search would
   be too broad to be useful).

```python
provider = OpenLibraryProvider()
candidates = provider.find_candidates(book)  # -> list[MetadataCandidate]
```

### A real data-quality surprise, found while testing against the live API

Looking up a deliberately-bogus ISBN like `"0000000000000"` or
`"9999999999999"` did **not** return an empty result - Open Library
had real (if obscure) books registered under those exact literal
strings (an exhibition catalog, a foreign-language novel). There's no
reliable "not found" signal to detect client-side beyond "the bibkey
isn't a key in the response dict at all" - which is what
`_find_by_isbn()` actually checks (`data.get(f"ISBN:{isbn}")`, not any
kind of validity check on the result). This is Open Library's own data
quality, not something this project can fix - it's exactly the kind of
mismatch a human reviewing `lookup`'s side-by-side output would catch,
which is the whole reason this is a comparison tool and not an
auto-apply one.

### Network behavior

- **HTTP**: stdlib `urllib.request` only - no new dependency for the
  HTTP layer itself (unlike the Report Engine's Excel/PDF writers).
- **Caching**: every response is cached to `cache/openlibrary/<sha256(url)>.json`
  with a 1-week TTL (`response_cache.py`, `ResponseCache`) - repeat
  lookups for the same book don't hit the network at all.
- **Offline mode** (`OpenLibraryProvider(offline=True)`, `--offline` on
  the CLI): only ever consults the cache; a cache miss returns `[]`
  immediately rather than attempting a network call.
- **Rate limiting**: a courtesy 1-second minimum interval between
  actual network requests (`_throttle()`), so a batch of lookups
  doesn't hammer a free public API. Cache hits bypass the throttle
  entirely.
- **Error handling**: `URLError`/`TimeoutError` (network down, DNS
  failure, timeout) and `JSONDecodeError` (malformed response) all
  raise `ProviderUnavailableError` - callers can distinguish "Open
  Library has nothing for this book" (`[]`) from "couldn't reach Open
  Library right now" (exception), which matters a lot for `lookup`'s
  error message.

### Why the HTTP call is injectable, not just importable

`OpenLibraryProvider(fetcher=...)` takes the actual
`fetcher(url, timeout, user_agent) -> dict` callable as a constructor
argument, defaulting to a small `urllib`-based implementation. Every
test in `tests/test_openlibrary_provider.py` injects a fake fetcher
returning canned JSON - **the automated test suite never makes a real
network call**. The real API was hit manually (via `python -c ...` and
`python run.py lookup`) to validate the response shapes this module's
mapping logic is built against, but that verification isn't part of
`pytest`.

## Configuration

`src/config/providers.py` holds base URLs, timeouts, cache TTL, and
rate-limit interval for Open Library, plus (for API-key providers) the
key read from an environment variable so wiring a provider up later
doesn't need another config pass:

```python
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")
```

## CLI: `python run.py lookup <book_id>`

Read-only metadata comparison - Calibre's current values next to every
Open Library candidate found. Nothing is written; there's no `--apply`
because deciding *which* fields to trust and overwrite is a real policy
question the project hasn't answered yet (see `Roadmap.md`). Add
`--offline` to only consult the cache.

## Cover Download Engine (`src/repair/cover_finder.py`, `cover_applier.py`)

Deliberately shipped as its own release (v1.5.1) after the Open
Library provider, since it needed a new dependency (Pillow) and its
own image-handling logic rather than being rushed as part of v1.5.0.

`CoverFinder` gathers candidate cover images from two sources and
never writes anything - it only downloads, validates, and scores:

- **Open Library** - reuses the `cover_url` a provider candidate
  already carries (from `OpenLibraryProvider.find_candidates()`), so a
  `covers` call that already ran a `lookup`-style provider query
  doesn't pay for a second HTTP round-trip.
- **User folder** (optional, `--user-folder PATH`) - local files named
  `<book_id>.jpg`/`.png`/`.webp`, for covers found by hand outside the
  tool. Google Books, Internet Archive, and Amazon (metadata-only)
  remain unimplemented, blocked on their own provider work (v2.1.0).

Each candidate is downloaded via the same dependency-injected
`fetcher` pattern as `OpenLibraryProvider`, then validated with
`Pillow` (lazy-imported, so the app runs without it until a `covers`
call actually needs it):

- Corruption check: `Image.verify()`, then reopen (verify invalidates
  the image object for further use).
- Format must be JPEG, PNG, or WEBP.
- Minimum resolution 300x300; aspect ratio (height/width) between 1.1
  and 2.2 - rejects square or extreme images, since book covers are
  reliably portrait.
- File size between 100 bytes and 20 MB (catches both truncated
  downloads and mistaken non-image responses).
- A 0-100 quality score, normalized against a ~1000x1500-pixel target
  resolution - not a validation cutoff, just a ranking signal for
  `--best`.
- Duplicate flag: SHA-256 byte-hash of the candidate compared against
  the book's existing `cover.jpg`, if any - exact-match only, not
  perceptual/fuzzy hashing (a simpler first pass; see `Roadmap.md`).

`CoverApplier` is the only thing that writes: resizes the chosen
candidate down to an 800px max dimension, converts to JPEG, saves it
as `cover.jpg` in the book's folder, and updates `has_cover` in
`metadata.db`. Same backup-first apply pattern as `repair --apply` and
`organize --apply` (`repair/backup.py`, called before any write).

```
python run.py covers <book_id>                    # preview only
python run.py covers <book_id> --apply --best      # save the top-scoring valid, non-duplicate candidate
python run.py covers <book_id> --apply --candidate 2   # save a specific candidate from the preview list
```

## Adding a real provider

1. Create `providers/<name>/<name>_provider.py` subclassing `MetadataProvider`.
2. Implement `find_candidates()` - map the external API's response
   onto `MetadataCandidate` fields; raise `ProviderUnavailableError`
   for connectivity/parsing failures, return `[]` for confirmed "not found".
3. Add base URL/API key/timeouts to `config/providers.py`.
4. Reuse `response_cache.py`'s `ResponseCache` rather than writing a
   new cache - it's provider-agnostic (just a URL-keyed JSON store).
5. Inject the HTTP transport as a constructor argument (see
   `OpenLibraryProvider.__init__`'s `fetcher` parameter) so tests can
   fake it - do not hit the real API in the test suite.
6. Update this doc's stub/working table and `Roadmap.md`.
