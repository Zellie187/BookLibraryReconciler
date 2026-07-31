# Builder Layer

## Purpose

Converts a raw `sqlite3.Row` (plus pre-loaded bulk caches from the
repository layer) into a fully-populated `Book` domain object:

```
SQLite Row + bulk caches -> BookBuilder -> Book
```

## `BookBuilder`

`src/builders/book_builder.py` is a fluent builder - each `set_*`/`add_*`
method returns `self` so `BookRepository.get_books()` can chain the
whole assembly in one expression:

```python
book = (
    BookBuilder()
    .set_basic_info(row)
    .add_authors(author_cache.get(row["id"], []))
    .add_identifiers(identifier_cache.get(row["id"], {}))
    .set_series(self.series_repo.get_series_for_book(row["id"]))
    .set_comments(self.comment_repo.get_comment_for_book(row["id"]))
    .set_publisher(publisher_cache.get(row["id"], ""))
    .set_rating(rating_cache.get(row["id"], 0))
    .add_languages(language_cache.get(row["id"], []))
    .add_tags(tag_cache.get(row["id"], []))
    .add_formats(format_cache.get(row["id"], []))
    .build()
)
```

Notable behavior baked into the builder rather than left to callers:

- `add_identifiers()` also extracts `book.isbn` from the identifiers
  dict (`identifiers.get("isbn", "")`).
- `add_formats()` derives three things from the list of `FormatFile`:
  `book.format_files` (the full objects), `book.formats` (just the
  extensions), and `book.size` (sum of all format sizes).
- `set_basic_info()` defaults `series_index` to `0` when Calibre stores
  `NULL`.

## Models

Plain dataclasses, no I/O, defined in `src/models/`:

- `Book` - the aggregate; see `Project-Specification.md` for the full field list.
- `Author`, `Series` - `{id, name, sort, link}` shape shared with Calibre's own schema.
- `FormatFile` - `{format, name, size}` plus a `.filename` property (`f"{name}.{format.lower()}"`).

## Adding a field

If you add a new repository (see `Gateways.md`), add the matching
`BookBuilder` method and `Book` field in the same change - the two are
meant to evolve together, and `tests/test_book_repository.py` asserts
the field actually round-trips from a seeded fixture database.
