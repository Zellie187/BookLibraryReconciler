# Provider System

External metadata sources are plugins, all implementing the same
interface (`src/providers/base/provider.py`):

```python
class MetadataProvider(ABC):
    name = "base"

    @abstractmethod
    def find_candidates(self, book) -> list[MetadataCandidate]:
        ...
```

`MetadataCandidate` is a plain dataclass: `source`, `title`, `authors`,
`isbn`, `publisher`, `description`, `cover_url`. It's a provider's
*proposed* version of a book's metadata, meant for comparison, not for
direct application.

```
providers/
    base/            MetadataProvider, MetadataCandidate
    calibre/          working - wraps a book's own existing metadata
    openlibrary/       stub - raises NotImplementedError (planned v1.2.0)
    googlebooks/       stub - raises NotImplementedError (planned v1.2.0)
    isbndb/            stub - raises NotImplementedError (planned v1.2.0)
```

## Why Calibre is a "provider" too

The original spec's domain-model diagram is:

```
Calibre -> Book Object -> Open Library -> Improved Book Object -> Repair Engine
```

`CalibreProvider.find_candidates(book)` returns the book's own current
metadata as a single `MetadataCandidate` with `source="calibre"`. This
means once external providers are implemented, comparing "what we have"
against "what Open Library/Google Books say" is just comparing two
lists of `MetadataCandidate` through the same interface - no special
casing for the local source.

## Configuration

`src/config/providers.py` holds base URLs and (for API-key providers)
reads the key from an environment variable, so wiring a provider up
later doesn't need another config pass:

```python
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")
```

## Adding a real provider

1. Create `providers/<name>/<name>_provider.py` subclassing `MetadataProvider`.
2. Implement `find_candidates()` to call the external API and map its
   response onto `MetadataCandidate` fields.
3. Add any needed base URL/API key to `config/providers.py`.
4. Add tests using a mocked HTTP client (do not hit the real API in
   the test suite).
5. Update this doc's stub/working table and `Roadmap.md`.
