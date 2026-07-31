# Changelog

All notable changes to this project will be documented here.

---

## Version 1.1.0 - Search engine and library navigation

### Added
- `models/search_criteria.py` - `SearchCriteria` (field/operator/value).
- `services/search_service.py` - `SearchService`, filtering an
  in-memory `list[Book]` against AND-combined `SearchCriteria`.
  Searchable fields: title, author, isbn, uuid, series, publisher,
  language, tag, format, comments, path, date_added, last_modified,
  rating, has_cover. Operators: exact, contains, starts_with,
  ends_with, regex, fuzzy (stdlib `difflib`), missing, present, and
  numeric eq/gte/lte/gt/lt. Sortable by title, author, series (name
  then series_index), rating, date_added, last_modified, size.
- `controllers/search_controller.py` - `SearchController`, parsing the
  CLI's `field=value` / `field:mode=value` / `field:missing` /
  `field>=value` query syntax plus convenience aliases
  (`missing-isbn`, `has-cover`, etc.) into `SearchCriteria`.
- `books.last_modified` wired into `Book`/`BookBuilder`/`BookRepository`
  (the column existed in Calibre's schema but was never read before).
- `ReportWriter.write_search_results()` for `--csv` on the new command.
- CLI: `python run.py search <terms...> [--sort FIELD] [--desc]
  [--limit N] [--csv]`.
- `docs/architecture/Search.md`; `Roadmap.md` rewritten to match the
  authoritative v1.x version table (search now precedes metadata
  analysis/reporting in the sequence, reflecting what actually shipped).

---

## Version 1.0.0-alpha

### Added (architecture pass)
- `docs/architecture/` - eleven reference docs (Project-Specification,
  Architecture, Database, Metadata-Engine, Providers, Gateways,
  Builders, Services, GUI, Roadmap, Developer-Guide).
- GitHub community files: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`,
  `.github/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/python.yml`
  (pytest + ruff + black + mypy on every push/PR to `main`).
- `src/config/` package (`paths.py`, `settings.py`, `database.py`,
  `providers.py`, `constants.py`), replacing the single
  `core/config.py` + `core/constants.py`.
- `src/app/application.py` - the single place that wires
  `DatabaseManager` -> `BookRepository` -> `LibraryService` together.
  `LibraryService` now takes an injected `BookRepository` instead of
  constructing one from a `database_manager` itself.
- `src/metadata/metadata_validator.py` (heuristic checks: title matches
  author name, title contains a "by <author>" clause, empty title,
  series_index of 0) and `metadata_repair.py` (non-destructive
  suggested field corrections) and `metadata_engine.py` (facade tying
  scoring + validation + repair suggestions together).
  `health_score.py` renamed to `metadata_score.py`.
- `src/providers/` plugin architecture: `MetadataProvider` /
  `MetadataCandidate` base interface, a working `CalibreProvider`, and
  conforming stubs for Open Library / Google Books / ISBNdb (replacing
  the old empty flat files under `src/services/`).
- `src/reports/base_report.py` common `ReportWriter` interface;
  `csv_report.py` and `json_report.py` are real, `excel_report.py` and
  `html_report.py` are conforming stubs (replacing `report_generator.py`).
- `resources/{icons,images,themes,fonts}/` scaffold for the future GUI.

### Added (first working slice)
- Repositories (gateway layer) for publishers, ratings, languages, tags,
  and on-disk formats, completing the entity list from the dev spec.
- `BookBuilder` now assembles the full `Book` object: publisher, pubdate,
  rating, languages, tags, and format files (with sizes).
- Metadata Engine: per-book completeness scoring
  (title/author/ISBN/cover/description) plus library averages.
- Repair Engine first slice (`src/repair/`): `FileOrganizer` computes an
  `Author/Title` reorganize plan from existing Calibre metadata,
  `OrganizeApplier` executes it (move folders, rename format files,
  update `metadata.db`), `backup.py` snapshots the database before any
  write. Preview-first: nothing moves without an explicit `--apply`.
- CSV report export for both the organize plan and the health report.
- CLI subcommands in `run.py`: `preview`, `health`, `organize` (with
  `--limit`, `--csv`, `--apply`).
- `Settings/config.json` is now read, so the tool can point at a real
  Calibre library instead of only the bundled sample.
- pytest suite (30 tests) covering models, repositories, the analyzer,
  the health scorer, and the organizer/applier against a fixture
  Calibre-schema database.
- `pyproject.toml` with pytest/ruff/black/mypy configuration.

### Fixed
- `src/models/_init_.py` and `src/builders/_init_.py` were misspelled
  (single underscore) and were not real package init files.
- `LibraryAnalyzer` expected dict-style rows but `BookRepository` returns
  `Book` dataclasses — rewritten against the real model.
- Startup crashed on Windows consoles due to an emoji in the banner
  encoding to the console's codepage; stdout is now reconfigured to UTF-8.
- `requirements.txt` and `README.md` were empty.

### Not yet implemented
- Open Library / Google Books / ISBNdb providers (stubs only).
- EPUB-embedded metadata reading.
- Duplicate detection, cover-fetching, Excel/HTML reports, GUI.

---

## Version 0.4

### Added
- Project architecture
- SQLite database connection
- Book model
- Repository pattern

### Changed
- Switched from CSV-first design to metadata.db-first design