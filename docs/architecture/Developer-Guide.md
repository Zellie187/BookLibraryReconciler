# Developer Guide

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.14+. No runtime dependencies outside the standard
library - `requirements.txt` is dev-only (`pytest`, `ruff`, `black`, `mypy`).

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
`tmp_path`, never the actual `data/` folder.

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
    analyzers/      LibraryAnalyzer (read-only stats)
    metadata/       MetadataScorer, MetadataValidator, MetadataRepair, MetadataEngine,
                    isbn_validator, DuplicateDetector, series_order, LibraryInspector,
                    text_normalize, AuthorDuplicateFinder
    repair/         FileOrganizer, OrganizeApplier, MetadataRepairApplier, AuthorMerger, backup
    reports/        ReportWriter + CsvReport/JsonReport/(ExcelReport/HtmlReport stubs)
    providers/      MetadataProvider + calibre/openlibrary/googlebooks/isbndb
    readers/        CSVReader (legacy), epub_reader.py (stub, not used by the Calibre workflow)
    utils/          logger.py (not yet wired into the CLI)
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
| Add an external metadata source | `providers/` - see `Providers.md` |
| Add an output format | `reports/` - subclass `ReportWriter`, implement `write_table()` |
| Add a filesystem operation | `repair/` - must be preview-first with an explicit apply step and a backup, like `organize_applier.py` |
| Add a CLI command | `src/main.py` - add a subparser + `run_*` function that receives `(args, app)` |

## Before opening a PR

See `CONTRIBUTING.md` for branch/commit conventions and the PR
checklist in `.github/PULL_REQUEST_TEMPLATE.md`.
