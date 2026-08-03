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

## v2.0.0 - Full PySide6 desktop application

See `GUI.md`. Dashboard, library view (grid/list/table), book details,
metadata comparison, report viewer, search (instant/advanced/smart
collections), settings, notifications. v2.0.0-alpha and
v2.0.0-alpha.2 (above) are the first two slices; this entry is done
when the rest of that list ships.

## v2.1.0 - Remaining additional providers

ISBNdb, once the v2.0.0 GUI ships (Google Books and Internet Archive
already shipped early, as v1.6.0/v1.7.0 - see the reordering note at
the top of this doc). Needs a paid API key to implement and verify for
real, unlike Google Books/Internet Archive/Open Library.

## v3.0.0 - Plugin SDK and provider marketplace

A packaging/discovery layer on top of the `providers/` interface that
already exists (`Providers.md`) - every provider already implements
`MetadataProvider`, so this is chiefly about distribution, not a new
interface.
