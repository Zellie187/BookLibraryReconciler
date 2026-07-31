# Architecture

## Layers

```
Application Layer     src/app/application.py
        |
Service Layer         src/services/
        |
Repository Layer      src/repositories/   (this project's "Gateway Layer" - see Gateways.md)
        |
Database Layer        src/core/database.py + Calibre's metadata.db
```

Alongside that vertical stack, three independent packages plug into
the Service layer's data instead of sitting inside it:

```
Metadata Engine   src/metadata/    - completeness scoring, validation, repair suggestions
Repair Engine     src/repair/      - file reorganize plan + apply + backup
Reports           src/reports/     - CSV/JSON/(Excel/HTML) report writers
Providers         src/providers/   - pluggable external metadata sources
```

Configuration is its own package, read by whichever layer needs it -
nothing above it constructs paths or reads `Settings/config.json`
directly:

```
src/config/
    paths.py       project-relative folders (data/, output/, reports/, logs/, covers/)
    settings.py     Settings/config.json -> LIBRARY_ROOT, METADATA_DB
    database.py     Calibre table name constants
    providers.py    external provider base URLs / API keys
    constants.py    APP_NAME, VERSION, display constants
```

## Dependency injection

`Application` (see `src/app/application.py`) is the **only** place that
constructs `DatabaseManager`, `BookRepository`, and `LibraryService`.
Nothing else is allowed to build its own repository or service - they
receive one through their constructor instead:

```python
class LibraryService:
    def __init__(self, book_repository):   # injected, not constructed here
        self.book_repository = book_repository
```

```python
with Application() as app:
    app.library_service.get_books(limit=10)
```

Why this matters: a test can pass in a fake/mock `BookRepository`
without touching a real database, and swapping the database layer
later (e.g. a folder-based library instead of Calibre) only means
changing what `Application.start()` wires up - `LibraryService` and
everything above it are unaffected.

## Request flow example: `python run.py organize`

```
main.py
  -> Application().start()
       -> DatabaseManager(METADATA_DB).connect()
       -> BookRepository(database)          # queries books + all linked tables
       -> LibraryService(book_repository)
  -> LibraryService.get_all_books()          -> list[Book]
  -> FileOrganizer().plans_with_changes(books) -> list[OrganizePlan]
  -> (if --apply) backup_database(METADATA_DB)
  -> (if --apply) OrganizeApplier(library_root, library_service).apply(plans)
```

## Package boundaries

- `models/` - plain dataclasses (`Book`, `Author`, `Series`, `FormatFile`). No I/O.
- `builders/` - turn a raw `sqlite3.Row` (plus pre-loaded bulk caches) into a `Book`.
- `repositories/` - one class per Calibre table/relationship, all SQL lives here.
- `services/` - business logic that composes repositories; this is what `Application` hands out.
- `analyzers/` - read-only statistics over an already-loaded `list[Book]`.
- `metadata/` - scoring, validation, and repair-suggestion logic over `list[Book]`.
- `repair/` - the only code allowed to touch the filesystem or write to `metadata.db` outside of `repositories/`.
- `reports/` - turns any headers+rows into a file; never queries the database itself.
- `providers/` - external (or local) sources of `MetadataCandidate` objects, all implementing the same interface.

A rule of thumb used throughout: **a lower layer never imports from a
higher one** (e.g. `repositories/` never imports `services/`).
