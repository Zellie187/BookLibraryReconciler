# Service Layer

## `LibraryService`

`src/services/library_service.py` is the only service today. It takes
an already-constructed `BookRepository` (dependency injection - see
`Architecture.md`) and exposes the operations the CLI and Repair Engine
actually need:

| Method | Used by |
|---|---|
| `get_book_count()` | `preview` command |
| `get_books(limit)` | `preview` command (timed, prints load duration) |
| `get_all_books()` | `health`, `organize` commands (`get_books(limit=None)`) |
| `update_book_path(book_id, new_path)` | `OrganizeApplier` after a folder move |
| `rename_format(book_id, old_format, new_name)` | `OrganizeApplier` after a format file rename |

It does not do its own SQL - everything delegates to
`self.book_repository`. Its value is timing/logging around the load
(`get_books`) and giving the Repair Engine a stable interface instead
of a raw repository (see `update_book_path`/`rename_format`).

## Why services exist at all

`MetadataEngine`, `FileOrganizer`, and the report writers all operate
on a plain `list[Book]` - they don't need a service, just data. The
service layer exists specifically for operations that need the
database connection alive (loading, and the two write-back calls the
applier makes). If a future operation needs the same treatment (e.g. a
bulk metadata-repair "apply" step), add it to `LibraryService` rather
than reaching into `BookRepository` directly from `main.py`.

## Adding a service

Construct it inside `Application.start()` (see
`src/app/application.py`), passing in whatever repository or other
service it depends on - never have a service construct its own
dependencies internally.
