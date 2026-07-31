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

| Version | Features |
|---|---|
| v1.0.0-alpha | Core architecture, models, repositories, builders, database layer |
| v1.1.0 | Search engine and library navigation |
| v1.2.0 | Metadata analysis and health scoring |
| v1.3.0 | Metadata repair engine |
| v1.4.0 | Report engine (CSV, Excel, HTML, JSON, PDF) - spec's v1.5.0, built first |
| v1.5.0 | Open Library provider - spec's v1.4.0, built after |
| v1.5.1 | Cover Download Engine, completing v1.5.0's originally-deferred scope |
| v2.0.0 | PySide6 desktop application |
| v2.1.0 | Additional providers (Google Books, Internet Archive, etc.) |
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

- [ ] Google Books, Internet Archive, and Amazon (metadata-only) as
      cover sources - blocked on their own provider work (v2.1.0)
- [ ] Perceptual/fuzzy duplicate detection - exact byte-hash only for now

## v2.0.0 - PySide6 desktop application

See `GUI.md`. Dashboard, library view (grid/list/table), book details,
metadata comparison, report viewer, search (instant/advanced/smart
collections), settings, notifications.

## v2.1.0 - Additional providers

Google Books, Internet Archive, and others, once v1.5.0's
`OpenLibraryProvider` establishes the pattern for a real (non-stub)
provider implementation.

## v3.0.0 - Plugin SDK and provider marketplace

A packaging/discovery layer on top of the `providers/` interface that
already exists (`Providers.md`) - every provider already implements
`MetadataProvider`, so this is chiefly about distribution, not a new
interface.
