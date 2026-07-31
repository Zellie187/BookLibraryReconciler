# Database Layer

## Connection

`src/core/database.py` - `DatabaseManager` wraps a single sqlite3
connection to a Calibre `metadata.db`, with `row_factory = sqlite3.Row`
so every query result is addressable by column name.

```python
db = DatabaseManager(path_to_metadata_db)
db.connect()
...
db.close()
```

In practice you don't construct this yourself - `Application.start()`
does it (see `Architecture.md`).

## Dev tools

- `src/core/schema_explorer.py` / `src/core/database_explorer.py` -
  list tables, columns, foreign keys, indexes via `PRAGMA` queries.
- `tools/explore_database.py` - dumps every table's schema to
  `reports/database_schema.txt` (this is how the schema below was
  captured).
- `tools/inspect_table.py` - prints columns/foreign keys/indexes for
  one named table.

## Tables this project reads

Table names are centralized in `src/config/database.py`
(`BOOKS_TABLE`, `AUTHORS_TABLE`, etc.) for readability at call sites
that build SQL by hand, though most repositories currently write the
table name directly in their query for clarity.

| Table | Purpose | Repository |
|---|---|---|
| `books` | Core book row: title, sort, path, uuid, has_cover, series_index, pubdate | `book_repository.py` |
| `authors` + `books_authors_link` | Author names/sort/link, many-to-many | `author_repository.py` |
| `series` + `books_series_link` | One series per book (in practice) | `series_repository.py` |
| `publishers` + `books_publishers_link` | One publisher per book (in practice) | `publisher_repository.py` |
| `ratings` + `books_ratings_link` | Stored 0-10, converted to 0-5 stars | `rating_repository.py` |
| `languages` + `books_languages_link` | Ordered list of language codes | `language_repository.py` |
| `tags` + `books_tags_link` | Unordered list of tag names | `tag_repository.py` |
| `identifiers` | `{type: value}` dict (isbn, asin, ...) | `identifier_repository.py` |
| `comments` | Book description/blurb | `comment_repository.py` |
| `data` | On-disk format files: `format`, `name` (no extension), `uncompressed_size` | `format_repository.py` |

Not read yet: `custom_columns` (definitions only, no per-book values -
Calibre stores those in dynamically-named `custom_column_N` tables,
which needs a different approach than the fixed-schema repositories
above), `annotations*`, `conversion_options`, `last_read_positions`,
`feeds`, `books_pages_link`, `books_plugin_data`.

## Writes

| Method | Called by |
|---|---|
| `BookRepository.update_path(book_id, new_path)` | `OrganizeApplier`, after a folder move succeeds on disk |
| `FormatRepository.rename_format(book_id, old_format, new_name)` | `OrganizeApplier`, after a format file rename succeeds on disk |
| `BookRepository.update_title(book_id, new_title)` | `MetadataRepairApplier` |
| `AuthorRepository.merge_authors(canonical_id, duplicate_ids)` | `AuthorMerger` |

Every SQL statement uses parameterized queries (`?` placeholders) -
values are never string-interpolated into SQL, including in the write
paths above.

## Calibre's own triggers, and why `title_sort()` must be registered

`metadata.db` isn't a passive schema - Calibre defines triggers on
`books` that fire on any external write, and those triggers call
custom SQL functions Calibre's own Python process normally registers
via `sqlite3.Connection.create_function()`. An external tool that
opens the database with a plain `sqlite3.connect()` and doesn't
register the same functions will get the write half-done or, more
often, an outright error.

This was found for real, not hypothetically: the first version of
`BookRepository.update_title()` failed on every call with
`sqlite3.OperationalError: no such function: title_sort`, because
`books_update_trg` runs `UPDATE books SET sort=title_sort(NEW.title)
WHERE id=NEW.id AND OLD.title <> NEW.title` after any update where the
title actually changed. (Updates that don't touch `title`, like
`update_path`, never hit this - the trigger's guarded inner `UPDATE`
only gets evaluated for matching rows, and zero rows match when
`OLD.title = NEW.title`, so `title_sort()` is never actually called.)

The fix: `core/calibre_functions.py:calculate_title_sort()` replicates
Calibre's real algorithm (move a leading "The"/"A"/"An" to the end -
"The Hobbit" -> "Hobbit, The" - verified against real `sort` values
already stored in the bundled sample library), and `DatabaseManager.connect()`
registers it as `title_sort` on every connection, unconditionally - it's
free for read-only usage and required for any write that touches
`books.title`.

**If you add a repository write and hit `no such function: X`**, the
cause is the same: some Calibre trigger needs `X` registered. Check
`sqlite_master` for triggers on the table you're writing to
(`SELECT sql FROM sqlite_master WHERE type='trigger' AND tbl_name=...`)
before assuming it's a bug in your own SQL.

**Test fixtures must mirror this.** `tests/conftest.py`'s schema
includes `books_insert_trg`/`books_update_trg` for exactly this reason
- without them, a test suite exercising only the simplified fixture
schema would never have caught the `update_title()` bug above, since
the bug only exists against a database with Calibre's real triggers.
Any fixture that does its own raw `sqlite3.connect()` to seed data
(rather than going through `DatabaseManager`) must also call
`connection.create_function("title_sort", 1, calculate_title_sort)`
before inserting/updating `books.title`, or `INSERT` itself will fail
(`books_insert_trg` fires unconditionally, unlike the update trigger).
