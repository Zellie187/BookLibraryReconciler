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

Only two repository methods write to `metadata.db`, and only when the
Repair Engine's `OrganizeApplier` calls them after a file move/rename
has already succeeded on disk:

- `BookRepository.update_path(book_id, new_path)` - the book's folder moved.
- `FormatRepository.rename_format(book_id, old_format, new_name)` - one format file was renamed.

Every SQL statement uses parameterized queries (`?` placeholders) -
values are never string-interpolated into SQL, including in the write
paths above.
