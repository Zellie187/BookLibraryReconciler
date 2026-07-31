# Gateways (Repository Layer)

## Naming: why `repositories/`, not `gateways/`

The project spec originally called this layer the "Gateway Layer." In
practice the folder is named `repositories/`, and that's deliberate:

- The repository pattern is a well-known, widely recognised design
  pattern - most developers immediately understand what a
  `BookRepository` does.
- "Gateway" is overloaded (database gateway, API gateway, network
  gateway) and would read as ambiguous next to `providers/`, which is
  where this project's actual external-system access lives.

So the convention here is:

```
repositories/   domain persistence (reads/writes Calibre's metadata.db)
providers/      external systems (Open Library, Google Books, ...) and,
                as a special case, Calibre's own metadata treated as
                one provider among others (see Providers.md)
```

This document keeps the "Gateways" name only because that's where the
project's docs index points - read it as "the gateway layer, i.e. the
repositories."

## What lives here

One class per Calibre table/relationship, each taking a
`DatabaseManager` in its constructor:

- `book_repository.py` - the aggregate root; assembles a full `Book`
  by querying `books` and pulling bulk caches from every other
  repository below, then handing rows to `BookBuilder`.
- `author_repository.py`, `series_repository.py`,
  `publisher_repository.py`, `rating_repository.py`,
  `language_repository.py`, `tag_repository.py`,
  `identifier_repository.py`, `comment_repository.py`,
  `format_repository.py` - one per entity.

## The bulk-cache pattern

Loading 7,000+ books one query-per-book-per-relationship would be
slow. Every repository except `series_repository` and
`comment_repository` (which are simple enough to query per-book)
exposes a `get_all_*()` method that loads *every* row for *every* book
in one query and returns a `book_id -> value` dict. `BookRepository`
calls each `get_all_*()` once, then does in-memory dict lookups per
row:

```python
author_cache = self.author_repo.get_all_authors()     # one query
...
for row in cursor.fetchall():                          # N books
    ...add_authors(author_cache.get(row["id"], []))    # dict lookup, no query
```

This is why `get_books()` on the 7,029-book bundled sample loads in
well under a second.

## Adding a new repository

1. Add the table to `docs/architecture/Database.md`.
2. Create `repositories/<name>_repository.py` with `get_<name>_for_book(book_id)`
   and `get_all_<name>s()` following the pattern above.
3. Wire it into `BookRepository.__init__` and `get_books()`.
4. Add the corresponding `BookBuilder` setter and `Book` model field.
5. Add it to the fixture schema in `tests/conftest.py` and cover it in
   `tests/test_book_repository.py`.
