# Changelog

All notable changes to this project will be documented here.

---

## Version 2.0.0-alpha.6 - Cover Finder dialog

Sixth slice of the GUI MVP - the GUI equivalent of the CLI's `covers`
command, and the first GUI slice that actually writes anything.

### Added
- `src/gui/cover_finder_dialog.py` - `CoverFinderDialog`: provider
  dropdown (Open Library/Google Books/Internet Archive) + offline
  checkbox + "Find Candidates" button, a list of candidates (source/
  dimensions/format/score/valid/duplicate), and "Apply Best"/"Apply
  Selected" buttons - reachable via a new "Find Cover..." button on
  `BookDetailDialog`.
- Reuses the CLI's already-decided `covers --apply --best|--candidate
  N` semantics as-is (backup-first, resize, convert to JPEG, update
  `has_cover`) - not blocked by an unanswered policy question the way
  applying provider *metadata* is.
- `format_candidate_line()`/`pick_best_candidate()`: plain functions
  kept separate from the dialog for testability - `tests/
  test_gui_cover_finder_dialog.py` (8 tests).
- `MainWindow`/`BookDetailDialog` now thread `library_root`/
  `database_path` through, needed by `CoverFinder`/`CoverApplier`/
  `backup_database`.
- After the detail dialog closes, `MainWindow` repaints the library
  table instead of reloading it, since `book_at()` returns the same
  `Book` object the cover dialog may have mutated - avoids resetting
  an active search filter or a redundant database round-trip.
- Verified live end-to-end against the real Open Library API and a
  throwaway copy of the sample database: found 3 real candidates for
  book #1, applied the best one through the dialog's actual code path
  (`QMessageBox` patched to no-ops so the unattended smoke test
  doesn't hang on a modal popup), confirmed `cover.jpg` was written
  and `has_cover` persisted via a fresh database read, and confirmed
  the real committed sample library was untouched throughout.

---

## Version 2.0.0-alpha.5 - Settings tab

Fifth slice of the GUI MVP - reads and writes `Settings/config.json`
from the GUI instead of requiring the hand-editing README.md currently
documents.

### Added
- `src/gui/settings_widget.py` - `SettingsWidget`: a new "Settings" tab
  with a folder picker for the Calibre library, an optional file
  picker for `metadata.db`, a "Save" button, and a note that changes
  take effect on the next launch (not live).
- Validates the library folder exists before saving.
- `save_settings()`: a plain function writing exactly the two keys
  `config.settings.load_settings()` already reads.
- `tests/test_gui_settings_widget.py` (4 tests), each monkeypatching
  `SETTINGS_FILE` to a `tmp_path` so the real project's
  `Settings/config.json` is never touched by the test suite.
- Verified live: loaded the real (blank) values from the project's
  actual settings file at startup, confirmed the validation guard
  directly, and screenshotted all four tabs together - the real
  settings file was confirmed untouched throughout.

---

## Version 2.0.0-alpha.4 - Reports tab

Fourth slice of the GUI MVP - the GUI equivalent of the CLI's `report`
command (minus writing a file to disk), another item from
v2.0.0-alpha's "not done" list.

### Added
- `src/gui/report_viewer_widget.py` - `ReportViewerWidget`: a new
  "Reports" tab in `MainWindow` with a dropdown for the same four
  presets as `python run.py report --type` (health/duplicates/series/
  statistics) and a "Generate" button, rendering the report as text.
- `generate_report_text()`: a plain function (no Qt dependency)
  reusing `MetadataScorer`, `DuplicateDetector`,
  `AuthorDuplicateFinder`, `find_series_order_issues`, and
  `LibraryStatistics` - the exact same analyzers `preview`/`health`/
  `analyze`/`report` already use. No new business logic.
- `tests/test_gui_report_viewer_widget.py` (7 tests) against
  `generate_report_text()` directly, using a small fake
  `library_service` stub - no Qt or network dependency.
- Verified live against the real 7,029-book sample library: all four
  presets generated without error, and the numbers match figures
  already verified elsewhere in this project (40% average health
  score, 46 title duplicate groups, 52 duplicate author groups, 290
  series order issues), plus a rendered screenshot of the Statistics
  preset with all three tabs visible.

---

## Version 2.0.0-alpha.3 - Metadata Comparison dialog

Third slice of the GUI MVP - the GUI equivalent of the CLI's `lookup`
command, another item from v2.0.0-alpha's "not done" list.

### Added
- `src/gui/metadata_comparison_dialog.py` - `MetadataComparisonDialog`:
  Calibre's current metadata next to candidates from a chosen provider
  (Open Library/Google Books/Internet Archive dropdown, "Offline
  (cache only)" checkbox - same options as `lookup --provider
  --offline`). No write path, same scope as `lookup` itself.
- A new "Compare Metadata..." button on `BookDetailDialog` opens it.
- `src/providers/registry.py` - the `PROVIDERS` mapping extracted out
  of `main.py`, so both the CLI and this new GUI dialog can import it
  without a circular dependency. `main.py`'s `lookup`/`covers`
  commands now import it from there instead - no behavior change.
- `format_comparison()`: a plain function (no Qt, no network) doing
  the display-text formatting, kept separate from the dialog for the
  same testability reason as `compute_stats()`.
- `tests/test_gui_metadata_comparison_dialog.py` (7 tests) against
  `format_comparison()` directly.
- Verified live against the real Open Library API: found 3 real
  candidates for book #1 with correct ISBNs/publishers/cover URLs,
  including one with a non-ASCII author name that rendered correctly
  in the actual `QTextEdit` widget (confirmed via screenshot - a
  console `print()` of the same text showed mojibake, which turned
  out to be a terminal-encoding artifact, not a widget bug). Switching
  to Google Books mid-session hit the same real rate limit documented
  in v1.6.0's entry, handled cleanly with no crash.

---

## Version 2.0.0-alpha.2 - Dashboard tab

Second slice of the GUI MVP - library health at a glance, the first
item from v2.0.0-alpha's "not done" list.

### Added
- `src/gui/dashboard_widget.py` - `DashboardWidget`: a new "Dashboard"
  tab alongside "Library" in `MainWindow` (now a `QTabWidget`). Shows
  total books, unique authors/series, average health score, books
  needing attention, missing ISBN/cover/description, and ISBN/title
  duplicate group + series-order-issue counts, as a 3-column grid of
  stat tiles with a manual "Refresh" button.
- `compute_stats()`: a plain function (no Qt dependency, directly
  unit-testable) computing the numbers above via `LibraryAnalyzer`/
  `LibraryInspector` - the exact same analyzers `preview`/`analyze`
  already use, no new business logic.
- `tests/test_gui_dashboard_widget.py` (6 tests) - since
  `compute_stats()` has no Qt dependency, these don't need the
  `qt_app` fixture the table-model tests use.
- Verified live: a headless smoke test confirming the Dashboard tab
  populates (11 stat tiles) against the real 7,029-book sample
  library, plus actual rendered screenshots of both tabs - the
  Dashboard's numbers (1,468 authors, 2,365 series, 46 title
  duplicate groups) match figures already verified elsewhere in this
  project against the same sample library.

---

## Version 2.0.0-alpha - GUI MVP

First slice of the desktop application, chosen deliberately as a
minimal MVP over building the full spec'd v2.0.0 feature set in one
pass - proves the PySide6 wiring against the existing service layer.

### Added
- `src/gui/main_window.py` - `MainWindow`: search bar, `QTableView`
  library listing, status bar. Double-clicking a row opens a book
  detail dialog.
- `src/gui/book_table_model.py` - `BookTableModel`: read-only
  `QAbstractTableModel` (ID/Title/Author/Series/Rating/ISBN/Cover
  columns). No write path - the GUI inherits the CLI's preview-first
  rule (see `GUI.md`).
- `src/gui/book_detail_dialog.py` - `BookDetailDialog`: full book
  detail view, mirroring `main.py`'s CLI `print_book()` field set.
- The search box reuses `SearchController`/`SearchService` directly -
  identical query syntax to `python run.py search "..."`, one place
  that understands search terms.
- CLI: `python run.py gui` - lazily imports PySide6 (same pattern as
  Pillow/openpyxl/fpdf2), so the rest of the CLI works without it
  installed; prints a friendly install message instead of crashing if
  it's missing.
- `requirements.txt`: added `PySide6>=6.5`.
- `tests/test_gui_book_table_model.py` (8 tests) plus a session-scoped
  `qt_app` fixture in `conftest.py` (one shared `QApplication` - a
  second one raises) and `QT_QPA_PLATFORM=offscreen` set before any
  `QApplication` is constructed, so the suite runs without a display.
- `.github/workflows/python.yml`: installs `libegl1`/`libgl1`/
  `libxkbcommon0`/`fontconfig`/`fonts-dejavu-core` via `apt` before
  the Python dependencies, since PySide6's wheels need a few Linux
  system libraries even for the offscreen Qt platform - not verified
  against a real GitHub Actions run.
- Verified live: a headless smoke test (load all 7,029 books, run a
  real search, open the detail dialog, confirm a bad search field
  raises the same `ValueError` the CLI does) plus actual rendered
  screenshots of the running window and detail dialog.

### Known limitation
- Under `QT_QPA_PLATFORM=offscreen` on this project's Windows dev
  machine, rendered text came out as blank glyph boxes (no font found)
  even though the window's structure (columns, layout, row/field
  counts) was correct - confirmed as a font-availability quirk of the
  offscreen platform specifically, not a bug, by re-rendering on the
  native `windows` Qt platform, where every label rendered correctly.

---

## Version 1.7.0 - Internet Archive provider

The last piece of the spec's v2.1.0 "additional providers" scope,
built ahead of the v2.0.0 GUI for the same reason as v1.6.0 - only
needed the real-provider pattern v1.5.0 already established.

### Added
- `providers/internetarchive/internetarchive_provider.py` - real
  `InternetArchiveProvider.find_candidates()`: ISBN lookup
  (`q=isbn:...`) with a title/author search fallback
  (`q=title:(...)+AND+creator:(...)`), both restricted to
  `mediatype:texts` against archive.org's `advancedsearch.php` - a
  general-purpose search API over the whole archive, not a
  books-specific endpoint, so the media-type filter keeps results to
  scanned books/documents.
- Cover images via archive.org's `/services/img/<identifier>`
  endpoint.
- Reuses `ResponseCache` (own `cache/internetarchive/` folder,
  1-week TTL), offline mode, and the same rate-limit throttle pattern
  as Open Library/Google Books - no API key needed, archive.org's
  search API is free and public.
- Handles real-world field-shape variance confirmed against live API
  responses: archive.org's `creator`/`isbn`/`publisher`/`description`
  fields come back as either a plain string or a list depending on
  the item; `_as_list`/`_first` helpers normalize both.
- `--provider internetarchive` now selectable on `lookup`/`covers` -
  no argparse changes needed, both commands already read `choices`
  dynamically from the `PROVIDERS` registry.
- `tests/test_internetarchive_provider.py` (13 tests, fake fetcher
  only - no real network calls in the suite).
- Verified live against the real archive.org API: found *The
  Shining* by ISBN and 147 real matches for "Pride and Prejudice" by
  title/author (also exercising the string-vs-list field handling);
  the bundled sample library's intentionally messy titles don't match
  anything real, confirmed handled as a clean "no matches" across
  several book ids rather than an error.

---

## Version 1.6.0 - Google Books provider

Part of the spec's v2.1.0 "additional providers" scope, built ahead of
the v2.0.0 GUI since it only needed the real-provider pattern v1.5.0
already established - numbered v1.6.0 rather than v2.1.0 to keep
version numbers strictly increasing in actual ship order (see the
reordering note at the top of `docs/architecture/Roadmap.md`).

### Added
- `providers/googlebooks/googlebooks_provider.py` - real
  `GoogleBooksProvider.find_candidates()`: ISBN lookup
  (`q=isbn:...`) with a title/author search fallback
  (`q=intitle:...+inauthor:...`, up to 5 candidates) - the same
  two-strategy shape as `OpenLibraryProvider`.
- Reuses `ResponseCache` (own `cache/googlebooks/` folder, 1-week
  TTL), offline mode, and a 1-second rate-limit throttle - identical
  pattern to Open Library, new constants in `config/providers.py`.
- Optional `GOOGLE_BOOKS_API_KEY` environment variable, appended to
  requests when set (Google Books works unauthenticated too, at a
  stricter rate limit).
- `--provider {openlibrary,googlebooks}` added to both
  `python run.py lookup` and `python run.py covers` (default
  `openlibrary`).
- `tests/test_googlebooks_provider.py` (13 tests, fake fetcher only -
  no real network calls in the suite).

### Fixed
- `tests/test_providers.py` previously asserted `GoogleBooksProvider`
  raises `NotImplementedError` as a stub; now that it's real, that
  assertion would have made a live network call from inside the
  automated test suite. Removed `GoogleBooksProvider` from that
  parametrized stub test (caught by running the full suite after
  implementing the provider).

### Known limitation
- Google Books' unauthenticated rate limit is stricter than Open
  Library's, and this project's dev environment was already
  rate-limited (`HTTP 429`) during testing. Verified live: a direct
  `urllib` call confirmed the 429 is Google's own IP-level limit (not
  a bug), and the full `ProviderUnavailableError` -> CLI error-message
  path was exercised end to end against the real API. The
  response-parsing logic itself is covered by unit tests built from
  Google's documented response shape, not a live success call.

---

## Version 1.5.1 - Cover Download Engine

Completes the scope explicitly deferred out of v1.5.0.

### Added
- `repair/cover_finder.py` - `CoverFinder`: candidates from Open
  Library (`cover_url` already present on a `MetadataCandidate` from
  `OpenLibraryProvider.find_candidates()`, so no second round-trip)
  and an optional local "user folder" (covers named
  `<book_id>.jpg`/`.png`/`.webp`).
- Image validation (`Pillow`, lazy-imported so the rest of the app
  runs without it): corruption check (`Image.verify()` + reopen),
  supported format (JPEG/PNG/WEBP), minimum resolution (300x300),
  aspect ratio (height/width between 1.1 and 2.2 - book covers are
  portrait, not square), file size bounds (100 bytes - 20 MB).
- Quality scoring (0-100, normalized against a ~1000x1500-pixel
  target) and duplicate detection (SHA-256 byte-hash of the candidate
  against the book's existing `cover.jpg` - exact-match only, not
  perceptual/fuzzy hashing).
- `repair/cover_applier.py` - `CoverApplier`: resizes down to an
  800px max dimension, converts to JPEG, saves as `cover.jpg`, and
  updates `has_cover` in `metadata.db`. Follows the project's
  backup-first apply pattern (`repair/backup.py`), same as
  `organize --apply` and `repair --apply`.
- `BookRepository.update_has_cover()` / `LibraryService.update_has_cover()`.
- CLI: `python run.py covers <book_id> [--offline] [--user-folder PATH]
  [--apply --best | --apply --candidate N]` - preview by default;
  `--apply` needs an explicit candidate choice (highest-scoring valid
  non-duplicate via `--best`, or a specific 1-indexed `--candidate N`).
- `requirements.txt`: added `Pillow>=10.0`.
- Verified end-to-end against the live Open Library API and a
  throwaway copy of the sample database: real cover downloaded,
  validated, database backed up, `cover.jpg` written, and `has_cover`
  persisted correctly on a fresh read.

### Not included
- Google Books, Internet Archive, and Amazon (metadata-only) as cover
  sources - blocked on their own provider work (v2.1.0).
- Perceptual/fuzzy duplicate detection - exact byte-hash only for now.

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