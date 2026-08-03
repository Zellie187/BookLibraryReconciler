# Developer Guide

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.14+. `requirements.txt` has the dev tools (`pytest`,
`ruff`, `black`, `mypy`) plus optional-but-included dependencies needed
only by specific commands: `openpyxl`/`fpdf2` for `report --format
excel`/`pdf` (see `Reports.md`), `Pillow` for `covers` (image
validation/resize, see `Providers.md`), and `PySide6` for `gui` (see
`GUI.md`) - everything else in the app is stdlib-only.

## Running the CLI

```bash
python run.py preview --limit 10
python run.py health --limit 10 --csv
python run.py analyze --limit 10 --csv
python run.py repair --limit 10 --csv
python run.py repair --apply
python run.py organize --limit 10 --csv
python run.py organize --apply
python run.py search "author=King" "isbn:missing" --sort title --csv
python run.py report --type statistics --format excel
python run.py lookup 1 --offline
```

By default this reads the bundled sample library in `data/` (7,029
real-world-messy entries, useful for exercising every code path without
touching a real library). Point `Settings/config.json`'s `library_path`
at a real Calibre library to work with your own books - see the root
`README.md` for the exact steps and the "close Calibre first" warning.

## Running the test suite

```bash
pytest
```

`tests/conftest.py` builds a small in-memory-equivalent SQLite database
matching Calibre's schema (only the tables/columns this project
touches) via `tmp_path` fixtures - no test depends on a real Calibre
library or the bundled sample data. `tests/test_organize_applier.py`
and `tests/test_backup.py` exercise real filesystem operations against
`tmp_path`, never the actual `data/` folder. `tests/test_openlibrary_provider.py`
injects a fake HTTP fetcher - **the test suite never makes a real
network call**; the live API was only exercised manually (see
`Providers.md`).

## Linting, formatting, type checking

```bash
ruff check src tests
black --check src tests
mypy src
```

All three are configured in `pyproject.toml` and run in CI
(`.github/workflows/python.yml`) on every push/PR to `main`.

> **Known issue:** at the time of writing, `black` on very new
> CPython/Python builds has been observed to mis-handle a parenthesized
> multi-exception `except (A, B):` clause, rewriting it into invalid
> `except A, B:` syntax. If `black` ever reports success but the file
> no longer compiles, check for that specific pattern and verify with
> `python -m py_compile <file>` before trusting the formatter's output.
> This has not been observed with any other construct in this codebase.

## Project layout

```
src/
    app/            Application bootstrap (dependency injection root)
    controllers/    SearchController - parses CLI query syntax into service calls
    config/         paths, settings (Settings/config.json), constants
    core/           DatabaseManager (+ calibre_functions.py - title_sort trigger
                    compatibility, see Database.md), schema/database explorers, Timer
    models/         Book, Author, Series, FormatFile, SearchCriteria (dataclasses)
    builders/       BookBuilder
    repositories/   one class per Calibre table/relationship (see Gateways.md)
    services/       LibraryService, SearchService
    analyzers/      LibraryAnalyzer, LibraryStatistics (read-only stats)
    metadata/       MetadataScorer, MetadataValidator, MetadataRepair, MetadataEngine,
                    isbn_validator, DuplicateDetector, series_order, LibraryInspector,
                    text_normalize, AuthorDuplicateFinder
    repair/         FileOrganizer, OrganizeApplier, MetadataRepairApplier, AuthorMerger,
                    CoverFinder, CoverApplier, backup
    reports/        ReportWriter + CsvReport/JsonReport/HtmlReport/ExcelReport/PdfReport
                    (see Reports.md)
    providers/      MetadataProvider, ProviderUnavailableError, ResponseCache,
                    registry.py (PROVIDERS mapping, shared by main.py and gui/)
                    (see Providers.md); calibre/, openlibrary/,
                    googlebooks/, and internetarchive/ are real,
                    isbndb/ is a stub (needs a paid API key)
    readers/        CSVReader (legacy), epub_reader.py (stub, not used by the Calibre workflow)
    utils/          logger.py (not yet wired into the CLI)
    gui/            MainWindow, BookTableModel, BookDetailDialog,
                    DashboardWidget, MetadataComparisonDialog,
                    ReportViewerWidget, SettingsWidget,
                    CoverFinderDialog (see GUI.md) -
                    v2.0.0-alpha MVP; PySide6, imported lazily
tests/              pytest suite + tests/conftest.py fixtures
tools/              dev-only scripts (schema dump, table inspector)
docs/architecture/  this documentation
resources/          future GUI assets (icons/images/themes/fonts)
```

## Adding a feature - where does it go?

| You want to... | Start here |
|---|---|
| Read a new Calibre table/field | `repositories/`, `builders/book_builder.py` - see `Gateways.md` |
| Add a searchable/sortable field | `services/search_service.py`'s `FIELD_EXTRACTORS`/`SORT_KEYS` - see `Search.md` |
| Add a completeness/validity check | `metadata/metadata_score.py` or `metadata_validator.py` - see `Metadata-Engine.md` |
| Add a library-wide check (duplicates, series order, ...) | `metadata/` (own module) + wire into `LibraryInspector` and `run_analyze()` |
| Add an external metadata source | `providers/` - see `Providers.md`; inject the HTTP transport as a constructor arg (like `OpenLibraryProvider`'s `fetcher`) so tests never hit the real network |
| Add an output format | `reports/` - subclass `ReportWriter`, implement `write_table()` - see `Reports.md` |
| Add a report preset | `reports/base_report.py` - add a `write_*(...)` method producing `(headers, rows)`, then wire it into `run_report()`'s `--type` choices |
| Add a filesystem operation | `repair/` - must be preview-first with an explicit apply step and a backup, like `organize_applier.py` |
| Add a CLI command | `src/main.py` - add a subparser + `run_*` function that receives `(args, app)` |

## Before opening a PR

See `CONTRIBUTING.md` for branch/commit conventions and the PR
checklist in `.github/PULL_REQUEST_TEMPLATE.md`.
