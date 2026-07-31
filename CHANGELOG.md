# Changelog

All notable changes to this project will be documented here.

---

## Version 1.5.0 - Open Library provider

The spec's Open Library provider scope, built after the Report Engine
(v1.4.0) by explicit choice - see the note at the top of `Roadmap.md`.
**Cover Download Engine is explicitly not part of this release** - a
separate, sizable feature (new Pillow dependency, image validation/
dedup/resize) deliberately left for its own pass.

### Added
- `providers/response_cache.py` - `ResponseCache`, a file-based JSON
  cache keyed by URL (`sha256` hash), with a TTL. Provider-agnostic,
  ready for reuse by Google Books/ISBNdb when those stop being stubs.
- Real `OpenLibraryProvider.find_candidates()`: ISBN lookup (Open
  Library's `bibkeys` API, one exact record) with a title/author
  search fallback (`search.json`, up to 5 candidates) when there's no
  ISBN. stdlib `urllib` only - no new HTTP dependency.
- `offline` mode (cache-only, never touches the network), a 1-second
  minimum interval between real requests (bypassed on cache hits), and
  a new `ProviderUnavailableError` distinguishing "couldn't reach the
  provider" (network/timeout/malformed response) from a confirmed
  empty result.
- The HTTP transport is dependency-injected (`fetcher` constructor
  argument) specifically so the automated test suite never makes a
  real network call - `tests/test_openlibrary_provider.py` uses a fake
  fetcher throughout.
- CLI: `python run.py lookup <book_id> [--offline]` - read-only,
  side-by-side comparison of Calibre's current metadata against every
  Open Library candidate found. No write path yet (deciding which
  fields to trust and overwrite is a real policy question, not
  answered by this release).
- `config/paths.py:CACHE_FOLDER`; new provider config constants
  (timeout, cache TTL, rate-limit interval, user agent) in
  `config/providers.py`.
- `docs/architecture/Providers.md` rewritten with the real
  implementation details, including a genuine data-quality surprise
  found while testing against the live API: bogus ISBNs like
  `"0000000000000"` returned real, unrelated books rather than a clean
  "not found" - Open Library's own data, not a bug in this project,
  and exactly the kind of mismatch `lookup`'s comparison view is meant
  to surface to a human.

---

## Version 1.4.0 - Report engine

Note: the spec's "Version 1.x Roadmap" document assigns this content
to v1.5.0 and the Open Library provider to v1.4.0. This project built
the Report Engine first (explicit choice), so version *numbers* here
track actual ship order - see `docs/architecture/Roadmap.md`.

### Added
- `analyzers/library_statistics.py` - `LibraryStatistics`: books per
  author/series/language/year, largest/smallest books by format size.
  Long-format output (`category, label, value`) rather than one
  section per breakdown, so no report-format interface changes were
  needed. Excludes Calibre's `"0101-01-01"` unknown-pubdate sentinel
  from the per-year breakdown (7,028 of 7,029 sample books have it)
  and zero-size books from "smallest," the same way earlier work
  excluded the `series_index == 0` sentinel.
- Real `ExcelReport` (`openpyxl`, bold header row, autosized columns)
  and `HtmlReport` (stdlib-only, `html.escape()`d self-contained page),
  replacing their `NotImplementedError` stubs.
- New `PdfReport` (`fpdf2`) - a plain tabular dump (fixed column
  widths, truncated long values), not a polished layout.
- Four report presets on `ReportWriter`: `write_library_health_summary`
  (library-wide counts, not per-book), `write_duplicate_report`
  (isbn/title/author groups), `write_series_report`,
  `write_statistics_report`.
- CLI: `python run.py report --type health|duplicates|series|statistics
  --format csv|json|excel|html|pdf [--output PATH]`.
- `openpyxl`/`fpdf2` added to `requirements.txt` (both lazy-imported by
  their respective writers, so everything else still runs without them).
- Verified against the bundled 7,000-book sample across all 20
  type/format combinations: 1,468 authors + 2,365 series produce a
  ~3,855-row statistics table at sane file sizes in every format
  (142KB CSV up to 377KB JSON).
- `docs/architecture/Reports.md`.

---

## Version 1.3.0 - Metadata repair engine

### Added
- `repair/metadata_repair_applier.py` - `MetadataRepairApplier` writes
  `MetadataRepair` suggestions back to `metadata.db` via
  `LibraryService.update_book_title()`, skipping (and reporting)
  suggestions with no concrete `suggested_value`.
- `metadata/text_normalize.py` - `name_signature()` extracted from
  `duplicate_detector.py` so `author_duplicate_finder.py` can share it.
- `metadata/author_duplicate_finder.py` - `AuthorDuplicateFinder` groups
  Calibre `authors` rows that are the same person spelled differently
  ("Stephen King" / "King, Stephen" / "King| Stephen"). Found 52 groups
  in the bundled 7,000-book sample's 1,468 distinct authors, all
  genuine on inspection - no fuzzy tuning needed (exact signature match).
- `repair/author_merger.py` - `AuthorMerger` applies those groups:
  repoints `books_authors_link` to the canonical (lowest-id) author and
  deletes the duplicate rows (`repositories/author_repository.py:merge_authors`).
- `repositories/book_repository.py:update_title()`,
  `repositories/author_repository.py:get_all_author_records()` /
  `merge_authors()`, and matching `LibraryService` wrappers.
- CLI: `python run.py repair [--limit N] [--csv] [--apply]`.

### Fixed
- **`title_contains_by_clause` false positive**: the heuristic matched
  a single capitalized word after "by", which misidentified real
  titles ending in ordinary English - "Married by Morning" (Lisa
  Kleypas) and "Dexter by Design" (Jeff Lindsay) - as author-echoed
  titles. Found by running `repair --apply` against a throwaway copy
  of the bundled sample and checking the result, *before* this reached
  a real library. Now requires 2+ capitalized words ("by Rick
  Riordan"), which still catches every genuine case in the sample.
- **`no such function: title_sort`**: Calibre's own `books_update_trg`
  trigger recomputes the `sort` column via a `title_sort()` SQL
  function whenever `books.title` changes - a function only Calibre's
  own process normally registers. `update_title()` failed on every
  call until `core/calibre_functions.py:calculate_title_sort()`
  (Calibre's real "move a leading article to the end" algorithm,
  verified against real `sort` values in the sample) was added and
  registered by `DatabaseManager.connect()`. `tests/conftest.py`'s
  fixture schema now includes the real trigger so this class of bug is
  caught by the test suite, not just manual smoke testing.

---

## Version 1.2.0 - Metadata analysis and health scoring

### Added
- `metadata/isbn_validator.py` - ISBN-10/ISBN-13 checksum validation
  (stdlib only). Wired into `MetadataValidator` as a new `invalid_isbn`
  check.
- `metadata/duplicate_detector.py` - `DuplicateDetector` finds likely
  duplicate books two ways: exact ISBN match, and fuzzy title matching
  (blocked by primary author, for speed on large libraries). Excludes
  author-name-echo titles and numbered-volume titles, both tuned by
  running against the bundled 7,000-book sample and checking the
  output by hand (265 -> 46 groups after the numbered-volume fix, with
  the remainder being genuine same-title duplicates on inspection).
- `metadata/series_order.py` - `find_series_order_issues()` flags
  duplicate series positions and gaps in whole-number sequences,
  correctly excluding the `series_index == 0` "unset" sentinel and
  treating fractional positions (between-volumes novellas) as valid.
- `metadata/library_inspector.py` - `LibraryInspector` ties
  `MetadataEngine` + `DuplicateDetector` + `series_order` together into
  one `LibraryInspection` per library.
- `ReportWriter.write_library_analysis()` for `--csv` on the new command.
- CLI: `python run.py analyze [--limit N] [--csv]`.
- `docs/architecture/Metadata-Engine.md` updated with all of the above,
  including the exact false-positive patterns found and how they were
  fixed; `Roadmap.md` marks v1.2.0 done.

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