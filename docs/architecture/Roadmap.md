# Version Roadmap

See `CHANGELOG.md` for the detailed, dated history. This is the
forward-looking summary, following the numbering from the "Feature
Specifications - Version 1.x Roadmap" document (this supersedes an
earlier draft numbering that had metadata analysis/reporting before
search - search is what actually shipped first).

| Version | Features |
|---|---|
| v1.0.0-alpha | Core architecture, models, repositories, builders, database layer |
| v1.1.0 | Search engine and library navigation |
| v1.2.0 | Metadata analysis and health scoring |
| v1.3.0 | Metadata repair engine |
| v1.4.0 | Open Library provider and cover downloads |
| v1.5.0 | Report engine (CSV, Excel, HTML, JSON, PDF) |
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

## v1.2.0 - Metadata analysis and health scoring (mostly done, shipped early)

Built during the v1.0.0-alpha architecture pass, ahead of this
version's turn in the sequence - see `Metadata-Engine.md`.

- [x] Completeness scoring (`MetadataScorer`/`metadata_score.py`)
- [x] Validation heuristics (`MetadataValidator`): title matches
      author name, title contains a "by \<author\>" clause, empty
      title, series_index of 0
- [x] Facade tying scoring + validation + repair suggestions together
      (`MetadataEngine`)
- [ ] Duplicate detection (title+author fuzzy matching - `SearchService`'s
      `fuzzy` operator is reusable here)
- [ ] Invalid ISBN checksum validation
- [ ] Broken series order detection (gaps/duplicates in `series_index`
      within a series)
- [ ] Wire `MetadataEngine.books_needing_attention()` into a CLI command
      (today `health` only uses the scorer directly)

## v1.3.0 - Metadata repair engine

- [x] Non-destructive repair suggestions (`metadata_repair.py`) - two
      patterns so far (`title_contains_by_clause`, `title_matches_author`)
- [ ] Repair sources comparison (Calibre vs Open Library vs Google
      Books vs ISBNdb) - blocked on v1.4.0/v2.1.0 providers being real
- [ ] Automatic / semi-automatic / manual repair modes
- [ ] Preview -> approve -> apply -> backup workflow for metadata
      writes (the *file* reorganize side of this already exists - see
      `repair/organize_applier.py` - this is the metadata-field
      equivalent)
- [ ] Duplicate author merging
- [ ] Broken series order repair

## v1.4.0 - Open Library provider and cover downloads

- [ ] Implement `OpenLibraryProvider.find_candidates()` for real
      (search by ISBN/title/author, response caching, rate limiting,
      offline mode, error handling for network failure/invalid
      ISBN/not found/timeout)
- [ ] Cover Download Engine: provider list (Open Library, Google
      Books, Internet Archive, user folder; Amazon only as
      metadata-only if legally appropriate), resolution/duplicate/
      quality checks, image validation, automatic resize, JPG/PNG/WEBP

## v1.5.0 - Report engine (CSV, Excel, HTML, JSON, PDF)

- [x] Common `ReportWriter` interface; `CsvReport`/`JsonReport` real
- [ ] `ExcelReport` (needs `openpyxl`, not yet a dependency)
- [ ] `HtmlReport`
- [ ] PDF export (needs a PDF library)
- [ ] Report presets: Library Health, Duplicate Report, Series Report,
      Statistics (books per author/series/language/year, largest/
      smallest books)
- [ ] Scheduling (manual/automatic/on-demand) - needs a place to run on
      a timer, which implies either the GUI or a separate scheduler
      process

## v2.0.0 - PySide6 desktop application

See `GUI.md`. Dashboard, library view (grid/list/table), book details,
metadata comparison, report viewer, search (instant/advanced/smart
collections), settings, notifications.

## v2.1.0 - Additional providers

Google Books, Internet Archive, and others, once v1.4.0's
`OpenLibraryProvider` establishes the pattern for a real (non-stub)
provider implementation.

## v3.0.0 - Plugin SDK and provider marketplace

A packaging/discovery layer on top of the `providers/` interface that
already exists (`Providers.md`) - every provider already implements
`MetadataProvider`, so this is chiefly about distribution, not a new
interface.
