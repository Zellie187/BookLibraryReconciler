# Version Roadmap

See `CHANGELOG.md` for the detailed, dated history. This is the
forward-looking summary. Version *numbers* here track actual ship
order (so they're always increasing); version *content* mostly follows
the "Feature Specifications - Version 1.x Roadmap" document, except
where explicit build-order choices swapped two entries:

- Search (spec's v1.1.0) shipped first, matching the spec already.
- The Report Engine (spec's v1.5.0) was explicitly built before the
  Open Library provider (spec's v1.4.0), so **this project's v1.4.0 is
  the Report Engine and v1.5.0 is Open Library/covers** - the reverse
  of the spec document's own numbering. Content-wise nothing was
  dropped, just reordered.
- The Google Books and Internet Archive providers (spec's v2.1.0,
  planned after the v2.0.0 GUI) were built next instead, since they
  only needed the provider pattern v1.5.0 already established - no
  GUI dependency. Since the GUI (v2.0.0) hasn't shipped yet, both keep
  the **1.x** line - **v1.6.0** and **v1.7.0** - rather than v2.1.0,
  preserving "version numbers always increase in actual ship order."
  v2.0.0/v2.1.0 stay reserved for the GUI and whatever's left of
  v2.1.0's original scope (ISBNdb) whenever those ship.
- The GUI's first slice is deliberately an MVP - a working PySide6
  window (searchable library table + read-only book detail dialog)
  proving the wiring against the existing service layer - rather than
  the full spec'd feature set (dashboard, grid/list views, metadata
  comparison, repair wizard, report viewer, instant/advanced/smart-
  collection search, settings, notifications) in one pass. Following
  the same convention as **v1.0.0-alpha** for the CLI foundation,
  this ships as **v2.0.0-alpha** - the full feature set stays "v2.0.0"
  until it's actually all there.

| Version | Features |
|---|---|
| v1.0.0-alpha | Core architecture, models, repositories, builders, database layer |
| v1.1.0 | Search engine and library navigation |
| v1.2.0 | Metadata analysis and health scoring |
| v1.3.0 | Metadata repair engine |
| v1.4.0 | Report engine (CSV, Excel, HTML, JSON, PDF) - spec's v1.5.0, built first |
| v1.5.0 | Open Library provider - spec's v1.4.0, built after |
| v1.5.1 | Cover Download Engine, completing v1.5.0's originally-deferred scope |
| v1.6.0 | Google Books provider - part of spec's v2.1.0, built ahead of the GUI |
| v1.7.0 | Internet Archive provider - part of spec's v2.1.0, built ahead of the GUI |
| v2.0.0-alpha | GUI MVP: searchable library table + book detail dialog (PySide6) |
| v2.0.0-alpha.2 | GUI MVP: Dashboard tab (library health at a glance) |
| v2.0.0-alpha.3 | GUI MVP: read-only Metadata Comparison dialog |
| v2.0.0-alpha.4 | GUI MVP: Reports tab (the 4 CLI report presets, as text) |
| v2.0.0-alpha.5 | GUI MVP: Settings tab (edits Settings/config.json) |
| v2.0.0-alpha.6 | GUI MVP: Cover Finder dialog (find + apply a cover) |
| v2.0.0 | Full PySide6 desktop application (dashboard, all views, wizards) |
| v2.1.0 | Remaining additional providers (ISBNdb) |
| v3.0.0 | Plugin SDK and provider marketplace |

## v1.0.0-alpha (done)

- [x] Models (`Book`, `Author`, `Series`, `FormatFile`)
- [x] Database layer (`DatabaseManager`, schema/database explorers)
- [x] Repository ("gateway") layer for every fixed-schema Calibre
      entity: books, authors, series, publishers, ratings, languages,
      tags, identifiers, comments, formats
- [x] Builder layer (`BookBuilder`)
- [x] Service layer + `Application` bootstrap with dependency injection
- [x] Testing framework (pytest, fixture Calibre-schema database)

Not done in this phase:

- [ ] Wire `utils/logger.py` into the CLI (currently `print()`-only)
- [ ] Custom column support (needs dynamic `custom_column_N` table handling)

## v1.1.0 - Search engine and library navigation (done)

See `Search.md` for the full write-up.

- [x] Search by title, author, ISBN, UUID, series, publisher, language,
      tag, format, comments, path, date added, last modified, rating,
      has-cover
- [x] Advanced filters (AND-combined `SearchCriteria` list)
- [x] Match modes: exact, contains, starts with, ends with, regex, fuzzy
- [x] Sorting: title, author, rating, series, date added, last
      modified, size - ascending/descending
- [x] Result fields: cover, title, author, series, rating, metadata
      score, ISBN, formats
- [x] `SearchController -> SearchService -> BookRepository -> SQLite`
      architecture (see `Search.md` for why "SQLite" here means "load
      once, filter in memory" rather than dynamic per-query SQL)

Not done (deferred to the GUI, v2.0.0 - no CLI "session" to attach to):

- [ ] Instant search
- [ ] Saved searches
- [ ] Search history
- [ ] Smart collections

## v1.2.0 - Metadata analysis and health scoring (done)

See `Metadata-Engine.md` for the full write-up.

- [x] Completeness scoring (`MetadataScorer`/`metadata_score.py`)
- [x] Validation heuristics (`MetadataValidator`): title matches
      author name, title contains a "by \<author\>" clause, empty
      title, series_index of 0, invalid ISBN checksum
- [x] Facade tying scoring + validation + repair suggestions together
      (`MetadataEngine`)
- [x] Invalid ISBN checksum validation (`isbn_validator.py` - ISBN-10/13)
- [x] Duplicate detection (`duplicate_detector.py`): exact ISBN match,
      plus fuzzy title matching blocked by author, with exclusions for
      author-name-echo titles and numbered-volume titles (both found
      by running against the bundled sample and checking by hand)
- [x] Broken series order detection (`series_order.py`): duplicate
      positions and gaps in whole-number sequences
- [x] `LibraryInspector` ties all of the above into one whole-library
      report, wired into `python run.py analyze`

Not done:

- [ ] Duplicate *file* detection (duplicate *books*, by ISBN or title,
      and duplicate *authors* are both covered - see v1.3.0)

## v1.3.0 - Metadata repair engine (done)

See `Metadata-Engine.md` for the full write-up, including a real bug
this work turned up (Calibre's `title_sort` trigger dependency,
documented in `Database.md`) and a real false-positive fix (the
`title_contains_by_clause` heuristic was misfiring on real titles like
"Married by Morning" until tightened).

- [x] Non-destructive repair suggestions (`metadata_repair.py`) - two
      patterns so far (`title_contains_by_clause`, `title_matches_author`)
- [x] Preview -> approve -> apply -> backup workflow for metadata
      writes (`repair/metadata_repair_applier.py` - the *file*
      reorganize side already existed in `organize_applier.py`; this is
      its metadata-field equivalent). Wired into `python run.py repair`.
- [x] Duplicate author detection + merging (`author_duplicate_finder.py`,
      `repair/author_merger.py`) - 52 groups found and correctly merged
      against the bundled 7,000-book sample, verified end-to-end
      (including that unrelated authors sharing a surname were *not*
      over-merged)
- [x] Repair modes, simplified for a non-interactive CLI: suggestions
      with a concrete `suggested_value` are "auto-applicable" under
      `--apply`; suggestions without one (the real value is genuinely
      unknown from local data) always require manual review - there is
      no fully-automatic mode that skips this distinction

Not done:

- [ ] Repair sources comparison (Calibre vs Open Library vs Google
      Books vs ISBNdb) - the *comparison* is real as of v1.5.0
      (`python run.py lookup`, Calibre vs Open Library specifically),
      but there's still no write path from a chosen candidate back
      into `metadata.db`, and Google Books/ISBNdb remain stubs
- [ ] Broken series order *repair* - `series_order.py` (v1.2.0) already
      *detects* duplicate/gap positions, but deciding which book should
      move to which position is exactly the kind of judgment call this
      project's rules say a human should make in Calibre itself, not
      something to guess at automatically

## v1.4.0 - Report engine (done)

See `Reports.md` for the full write-up. Built before the Open Library
provider (spec's original v1.4.0) - see the note at the top of this doc.

- [x] Common `ReportWriter` interface; `CsvReport`/`JsonReport`/`HtmlReport`
      real, `ExcelReport` (`openpyxl`) and `PdfReport` (`fpdf2`) real
      with lazy imports and a friendly error if the optional dependency
      is missing
- [x] Report presets: Library Health (library-wide counts, not
      per-book), Duplicate Report (isbn/title/author), Series Report,
      Statistics (books per author/series/language/year, largest/
      smallest books) - verified against the bundled 7,000-book sample
      (1,468 authors, 2,365 series -> ~3,855-row statistics table,
      sane file sizes across all five formats)
- [x] CLI: `python run.py report --type <...> --format <...> [--output PATH]`

Not done:

- [ ] Scheduling (manual/automatic/on-demand) - needs a place to run on
      a timer, which implies either the GUI or a separate scheduler
      process

## v1.5.0 - Open Library provider (done)

See `Providers.md` for the full write-up, including a real data-quality
surprise found while testing against the live API (bogus ISBNs like
`"0000000000000"` returned real, unrelated books rather than "not found").

- [x] Implement `OpenLibraryProvider.find_candidates()` for real: ISBN
      lookup (bibkeys API, exact record) with title/author search
      fallback (`search.json`, several loosely-matched candidates)
- [x] Response caching (`response_cache.py`, 1-week TTL, file-based)
- [x] Offline mode (`--offline` on the CLI - cache-only, no network)
- [x] Rate limiting (1s minimum interval between real requests; cache
      hits bypass it)
- [x] Error handling: `ProviderUnavailableError` for network
      failure/timeout/malformed response, distinct from a confirmed
      empty `[]` result; the "not found" case for a bogus ISBN can't be
      detected any more precisely than "the bibkey isn't in the
      response" - see `Providers.md` for why
- [x] CLI: `python run.py lookup <book_id> [--offline]` - read-only
      side-by-side comparison (Calibre's current metadata vs. Open
      Library candidates), matching the spec's "Metadata Comparison"
      concept. No `--apply` - deciding which fields to trust and
      overwrite is a real policy question, deliberately not answered
      yet (see "Not done" below)

Not done - Cover Download Engine was explicitly scoped out of this
pass and shipped separately as v1.5.1 (below):

- [ ] Repair sources comparison *applying* a chosen candidate's fields
      back to `metadata.db` - `lookup` now makes the comparison real,
      but there's still no write path; this needs a real UI/UX
      decision (per-field approve? whole-candidate approve?) that's
      more naturally a GUI (v2.0.0) concern than a CLI flag

## v1.5.1 - Cover Download Engine (done)

See `Providers.md` for the full write-up. Deliberately scoped out of
v1.5.0 since it needed its own pass: a new Pillow dependency, plus
image validation/quality-scoring/duplicate-detection/resize logic.

- [x] `CoverFinder`: candidates from Open Library (`cover_url` already
      present on a `MetadataCandidate`, so no second round-trip) and an
      optional local "user folder" (covers named `<book_id>.jpg/.png/.webp`)
- [x] Image validation (`Pillow`, lazy-imported): corruption check
      (`verify()` + reopen), format (JPEG/PNG/WEBP), minimum resolution
      (300x300), aspect ratio (height/width between 1.1 and 2.2 - book
      covers are portrait, not square), file size bounds
- [x] Quality scoring (0-100, normalized against a ~1000x1500 target)
      and duplicate detection (SHA-256 byte-hash against the existing
      `cover.jpg`, not perceptual/fuzzy hashing - a simpler first pass)
- [x] `CoverApplier`: resize down to 800px max dimension, convert to
      JPEG, save as `cover.jpg`, update `has_cover` - always behind the
      project's backup-first apply pattern
- [x] CLI: `python run.py covers <book_id> [--offline] [--user-folder PATH]
      [--apply --best | --apply --candidate N]` - preview by default,
      apply only with an explicit candidate choice
- [x] Verified end-to-end against the live Open Library API and a
      throwaway copy of the sample database (real download, validation,
      backup, save, and `has_cover` persistence all confirmed)

Not done:

- [ ] Internet Archive and Amazon (metadata-only) as cover sources -
      Google Books shipped as v1.6.0 (below); the rest is still
      blocked on their own provider work
- [ ] Perceptual/fuzzy duplicate detection - exact byte-hash only for now

## v1.6.0 - Google Books provider (done)

See `Providers.md` for the full write-up. Part of the spec's v2.1.0
scope, built ahead of the v2.0.0 GUI since it only needed the real-
provider pattern v1.5.0 already established - see the reordering note
at the top of this doc for why it's numbered v1.6.0, not v2.1.0.

- [x] Implement `GoogleBooksProvider.find_candidates()` for real:
      ISBN lookup (`q=isbn:...`, one exact record) with title/author
      search fallback (`q=intitle:...+inauthor:...`, several loosely-
      matched candidates) - same two-strategy shape as
      `OpenLibraryProvider`
- [x] Response caching, offline mode, and rate limiting reusing the
      exact same `ResponseCache`/throttle pattern as Open Library
      (`config/providers.py` holds Google's own TTL/interval/timeout)
- [x] Optional API key (`GOOGLE_BOOKS_API_KEY` env var) - Google Books
      works unauthenticated at a lower, stricter rate limit; appended
      to the request URL when set
- [x] Error handling: `ProviderUnavailableError` for network failure/
      timeout/malformed response, same as Open Library
- [x] CLI: `--provider {openlibrary,googlebooks}` added to both
      `lookup` and `covers` (default `openlibrary`), so either command
      can pull from Google Books instead
- [x] `tests/test_providers.py`'s old "GoogleBooksProvider raises
      NotImplementedError" stub test removed now that it's real (it
      would otherwise have made a live network call from the test
      suite by accident - caught by running the full suite)

Not done / known limitation:

- [ ] A real live success-path smoke test against Google's API -
      Google Books' unauthenticated quota is much stricter than Open
      Library's and this project's dev environment was already rate-
      limited (`HTTP 429`) at test time. Verified instead via a direct
      `urllib` call outside the app (confirming the 429 is Google's own
      IP-level limit, not a bug) plus the full error-handling path
      (`ProviderUnavailableError` -> CLI message) working live end to
      end. Response-parsing logic is covered by unit tests built
      directly from Google's documented response shape. Set
      `GOOGLE_BOOKS_API_KEY` for a higher quota if this matters for
      real use.

## v1.7.0 - Internet Archive provider (done)

See `Providers.md` for the full write-up. The last piece of the
spec's v2.1.0 scope built ahead of the GUI - same reasoning as
v1.6.0's Google Books provider.

- [x] Implement `InternetArchiveProvider.find_candidates()` for real:
      ISBN lookup (`q=isbn:...`) with title/author search fallback
      (`q=title:(...)+AND+creator:(...)`), both restricted to
      `mediatype:texts` against archive.org's `advancedsearch.php` -
      a general-purpose search API over the whole archive, not a
      books-specific endpoint, so the media-type filter is what keeps
      results to scanned books/documents
- [x] Cover images via the well-known `/services/img/<identifier>`
      endpoint
- [x] Response caching, offline mode, rate limiting, and
      `ProviderUnavailableError` handling - identical pattern to Open
      Library and Google Books (own `cache/internetarchive/` folder,
      no API key needed - archive.org's search API is free/public)
- [x] Handles real-world field-shape variance found while building
      this: archive.org's `creator`/`isbn`/`publisher`/`description`
      fields come back as either a plain string or a list depending
      on the item, confirmed against live API responses (`_as_list`/
      `_first` helpers normalize both)
- [x] CLI: `--provider internetarchive` added to `PROVIDERS` (no
      argparse changes needed - both `lookup` and `covers` already
      read `choices` dynamically from the registry)
- [x] Verified live against the real API: raw `urllib` calls
      confirmed the ISBN query finds *The Shining* by its real ISBN,
      and 147 real matches for "Pride and Prejudice" by title/author
      (also exercising the string-vs-list field-shape handling); the
      bundled sample library's intentionally messy titles (the whole
      premise of this tool) don't match anything real, which the app
      handles as a clean "no matches" rather than an error - tested
      across several book ids

Not done: ISBNdb provider remains a stub (needs a paid API key this
project doesn't have to verify against - see `Roadmap.md`'s v2.1.0
entry).

## v2.0.0-alpha - GUI MVP (done)

See `GUI.md` for the full write-up. Proves the PySide6 wiring against
the existing service layer with a deliberately small first slice -
the "Minimal MVP first" option chosen over building the full v2.0.0
feature set in one pass.

- [x] `src/gui/` package: `MainWindow` (search bar + table view +
      status bar), `BookTableModel` (read-only `QAbstractTableModel`),
      `BookDetailDialog` (double-click a row to see full book details)
- [x] Search box reuses the exact same `SearchController`/
      `SearchService` the CLI's `search` command already uses - same
      query syntax (`author=King`, `isbn:missing`, etc.), one place
      that understands search terms, not two
- [x] CLI: `python run.py gui` - lazily imports PySide6 (mirrors the
      Pillow/openpyxl/fpdf2 pattern), so the rest of the CLI still
      runs without it installed
- [x] Read-only, matching `GUI.md`'s carried-over design constraint -
      nothing in this MVP writes to `metadata.db`
- [x] `tests/test_gui_book_table_model.py` (8 tests) exercising the
      table model's data/header/reset logic directly; a session-scoped
      `qt_app` fixture in `conftest.py` shares one `QApplication`
      instance across GUI tests (constructing more than one raises).
      CI's `QT_QPA_PLATFORM=offscreen` is set in `conftest.py` itself
      (before any `QApplication` is constructed) so tests don't need a
      real display
- [x] Verified live: a headless smoke test (loading all 7,029 books,
      running a real search, opening the detail dialog, and confirming
      an invalid search field still raises `ValueError` the same way
      the CLI does) plus actual rendered screenshots of the running
      window and detail dialog on this machine's native Qt platform
      (not just the offscreen one) - both render correctly

Not done at this point - picked up incrementally in later
v2.0.0-alpha.N slices (below) and the rest of the spec's v2.0.0 scope.

## v2.0.0-alpha.2 - Dashboard tab (done)

See `GUI.md` for the full write-up. Second slice of the GUI MVP -
library health at a glance, the first item from v2.0.0-alpha's "not
done" list.

- [x] `src/gui/dashboard_widget.py` - `DashboardWidget`: a "Dashboard"
      tab alongside "Library" in `MainWindow` (now a `QTabWidget`).
      Shows total books, unique authors/series, average health score,
      books needing attention, missing ISBN/cover/description, and
      ISBN/title duplicate group + series-order-issue counts as a
      3-column grid of stat tiles, with a manual "Refresh" button (no
      auto-refresh - recomputing duplicate detection over the whole
      library isn't instant)
- [x] No new business logic - `compute_stats()` is a plain function
      (no Qt dependency) that calls `LibraryAnalyzer`/
      `LibraryInspector`, the exact same analyzers `preview`/`analyze`
      already use
- [x] `tests/test_gui_dashboard_widget.py` (6 tests) against
      `compute_stats()` directly - being a plain function, these don't
      even need the `qt_app` fixture the table-model tests use
- [x] Verified live: a headless smoke test confirming the Dashboard
      tab populates (11 stat tiles) against the real 7,029-book sample
      library, plus actual rendered screenshots of both tabs - the
      Dashboard's numbers (1,468 authors, 2,365 series, 46 title
      duplicate groups) match figures already verified elsewhere in
      this project against the same sample library

Not done: everything else on v2.0.0-alpha's original list except
Dashboard - grid/list views, metadata comparison UI, repair wizard,
report viewer, instant/saved/smart search, settings, notifications,
GUI provider picker.

## v2.0.0-alpha.3 - Metadata Comparison dialog (done)

See `GUI.md` for the full write-up. Third slice of the GUI MVP - the
GUI equivalent of the CLI's `lookup` command, another item from
v2.0.0-alpha's "not done" list.

- [x] `src/gui/metadata_comparison_dialog.py` - `MetadataComparisonDialog`:
      Calibre's current metadata next to candidates from a chosen
      provider (dropdown: Open Library/Google Books/Internet Archive),
      with an "Offline (cache only)" checkbox - same options as the
      CLI's `lookup --provider --offline`. No write path, matching
      `lookup`'s own scope exactly (deciding which fields to trust and
      overwrite is still an unanswered policy question).
- [x] Reachable via a new "Compare Metadata..." button on
      `BookDetailDialog`.
- [x] `src/providers/registry.py` - the `{key: (label, class)}`
      `PROVIDERS` mapping, extracted out of `main.py` so both the CLI
      and this new GUI dialog can import it without a circular
      dependency (`main.py` imports `gui.main_window`, so GUI code
      can't import back from `main.py`). `main.py`'s own `lookup`/
      `covers` commands now import it from there too - no behavior
      change, just removes the duplication before it could happen.
- [x] `format_comparison()`: a plain function (book + candidates ->
      display text) kept separate from the dialog so it's testable
      without Qt or a network call - `tests/test_gui_metadata_comparison_dialog.py`
      (7 tests).
- [x] Verified live against the real Open Library API: found 3 real
      candidates for book #1 with correct ISBNs/publishers/cover URLs,
      including one with a non-ASCII author name (confirmed rendering
      correctly in the actual `QTextEdit` widget, screenshotted -
      console `print()` output showed mojibake, which turned out to
      be a terminal-encoding artifact, not a bug in the widget).
      Switching to Google Books mid-session hit the same real rate
      limit documented in v1.6.0's entry, handled cleanly (no crash).

Not done at this point: everything else on v2.0.0-alpha's original
list except Dashboard and Metadata Comparison - grid/list views,
repair wizard, report viewer, instant/saved/smart search, settings,
notifications, GUI provider picker for `covers`.

## v2.0.0-alpha.4 - Reports tab (done)

See `GUI.md` for the full write-up. Fourth slice of the GUI MVP - the
GUI equivalent of the CLI's `report` command (minus writing a file to
disk), another item from v2.0.0-alpha's "not done" list.

- [x] `src/gui/report_viewer_widget.py` - `ReportViewerWidget`: a new
      "Reports" tab in `MainWindow` with a dropdown for the same four
      presets as `python run.py report --type` (health/duplicates/
      series/statistics) and a "Generate" button, rendering the
      report as text.
- [x] No new business logic - `generate_report_text()` reuses
      `MetadataScorer`, `DuplicateDetector`, `AuthorDuplicateFinder`,
      `find_series_order_issues`, and `LibraryStatistics` - the exact
      same analyzers `preview`/`health`/`analyze`/`report` already
      use, formatted as text instead of written to a CSV/JSON/Excel/
      HTML/PDF file.
- [x] `tests/test_gui_report_viewer_widget.py` (7 tests) against
      `generate_report_text()` directly, using a small fake
      `library_service` stub rather than the real database - no Qt or
      network dependency.
- [x] Verified live against the real 7,029-book sample library: all
      four presets generated without error, and the numbers match
      figures already verified elsewhere in this project (40% average
      health score, 46 title duplicate groups, 52 duplicate author
      groups, 290 series order issues) - plus a rendered screenshot of
      the Statistics preset showing all three tabs together.

Not done: everything else on v2.0.0-alpha's original list except
Dashboard, Metadata Comparison, and Reports - grid/list views, repair
wizard, instant/saved/smart search, settings, notifications, GUI
provider picker for `covers`.

## v2.0.0-alpha.5 - Settings tab (done)

See `GUI.md` for the full write-up. Fifth slice of the GUI MVP - reads
and writes `Settings/config.json` (`library_path`/`metadata_db`) from
the GUI, instead of requiring the hand-editing README.md currently
documents.

- [x] `src/gui/settings_widget.py` - `SettingsWidget`: a new
      "Settings" tab with a folder picker for the Calibre library and
      an optional file picker for `metadata.db`, a "Save" button, and
      a note explaining the change takes effect on next launch (not
      live - `config.settings.LIBRARY_ROOT`/`METADATA_DB` are computed
      once at import time and threaded through `Application` at
      startup, so there's no live-reload path to build here).
- [x] Validates the library folder exists before saving; warns instead
      of silently writing a broken path.
- [x] `save_settings()`: a plain function (no Qt dependency) writing
      exactly the two keys `config.settings.load_settings()` already
      reads - `tests/test_gui_settings_widget.py` (4 tests), each
      monkeypatching `SETTINGS_FILE` to a `tmp_path` so the real
      project's `Settings/config.json` is never touched by the test
      suite (confirmed via `git status` after running).
- [x] Verified live: the widget correctly loaded the real (blank)
      values from the project's actual `Settings/config.json` at
      startup, the nonexistent-folder validation guard was confirmed
      directly, and a screenshot shows all four tabs together. The
      real settings file was confirmed untouched throughout (this
      smoke test only reads and validates - it never calls
      `save_settings()` against the real file, to avoid any risk of
      leaving the repo's tracked default `config.json` modified).

Not done: everything else on v2.0.0-alpha's original list except
Dashboard, Metadata Comparison, Reports, and Settings - grid/list
views, repair wizard, instant/saved/smart search, notifications, GUI
provider picker for `covers`.

## v2.0.0-alpha.6 - Cover Finder dialog (done)

See `GUI.md` for the full write-up. Sixth slice of the GUI MVP - the
GUI equivalent of the CLI's `covers` command, and the first GUI slice
that actually writes anything (a `cover.jpg` + `has_cover`), unlike
every prior slice. Not blocked by an unanswered policy question the
way applying provider *metadata* is: the CLI's `covers --apply --best|
--candidate N` semantics (backup-first, resize, convert to JPEG,
update `has_cover`) were already decided and tested back in v1.5.1 -
this dialog just reuses them as-is.

- [x] `src/gui/cover_finder_dialog.py` - `CoverFinderDialog`: provider
      dropdown (Open Library/Google Books/Internet Archive) + offline
      checkbox + "Find Candidates" button, a list of candidates
      (source/dimensions/format/score/valid/duplicate), and "Apply
      Best"/"Apply Selected" buttons. Reachable via a new "Find
      Cover..." button on `BookDetailDialog`.
- [x] `format_candidate_line()` and `pick_best_candidate()`: plain
      functions (no Qt, no network) kept separate from the dialog for
      the same testability reason as every other GUI slice's helper
      functions - `tests/test_gui_cover_finder_dialog.py` (8 tests).
- [x] `MainWindow`/`BookDetailDialog` now thread `library_root` and
      `database_path` through (previously only `library_service`/
      `search_service` were passed) - needed for `CoverFinder`,
      `CoverApplier`, and `backup_database`, which all need real
      filesystem paths, not just the service layer.
- [x] After closing the detail dialog, `MainWindow` repaints the
      table (`table_model.layoutChanged.emit()`) rather than reloading
      it from the database - `book_at()` returns the same `Book`
      object `CoverFinderDialog` may have mutated (`has_cover`), so a
      repaint reflects the change without resetting an active search
      filter or paying for a redundant database round-trip.
- [x] Verified live end-to-end against the real Open Library API and
      a throwaway copy of the sample database (same pattern as
      v1.5.1's original verification): found 3 real candidates for
      book #1, applied the best one through the dialog's actual
      `apply_best()`/`_apply()` code path (with `QMessageBox.
      information()`/`.warning()` patched to no-ops so the unattended
      smoke test doesn't hang on a modal popup - the same lesson
      learned earlier with `QMessageBox.warning()` in the Metadata
      Comparison dialog's own smoke test), confirmed `cover.jpg` was
      written and `has_cover` was persisted via a fresh read from the
      database copy, and confirmed the real committed sample library
      was untouched throughout (`git status` clean).

Not done: everything else on v2.0.0-alpha's original list except
Dashboard, Metadata Comparison, Reports, Settings, and Cover Finder -
grid/list views, repair wizard, instant/saved/smart search,
notifications.

## v2.0.0 - Full PySide6 desktop application

See `GUI.md`. Dashboard, library view (grid/list/table), book details,
metadata comparison, report viewer, search (instant/advanced/smart
collections), settings, notifications. v2.0.0-alpha through
v2.0.0-alpha.6 (above) are the first six slices; this entry is done
when the rest of that list ships.

## v2.1.0 - Remaining additional providers

ISBNdb - explicitly deprioritized for now, at the user's request.
Needs a paid API key this project doesn't have to implement and verify
for real, unlike Google Books/Internet Archive/Open Library, which is
why it's the one piece of the original spec still not attempted while
everything else (including the GUI, worked ahead of schedule) has
moved forward. Revisit if/when an API key becomes available.

## v3.0.0 - Plugin SDK and provider marketplace

A packaging/discovery layer on top of the `providers/` interface that
already exists (`Providers.md`) - every provider already implements
`MetadataProvider`, so this is chiefly about distribution, not a new
interface.
