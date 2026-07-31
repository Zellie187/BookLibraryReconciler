# Version Roadmap

See `CHANGELOG.md` for the detailed, dated history. This is the
forward-looking summary.

## v1.0.0-alpha (current)

Foundation - done:

- [x] Models (`Book`, `Author`, `Series`, `FormatFile`)
- [x] Database layer (`DatabaseManager`, schema/database explorers)
- [x] Repository ("gateway") layer for every fixed-schema Calibre
      entity: books, authors, series, publishers, ratings, languages,
      tags, identifiers, comments, formats
- [x] Builder layer (`BookBuilder`)
- [x] Service layer + `Application` bootstrap with dependency injection
- [x] Logging (`utils/logger.py` - not yet wired into the CLI, see below)
- [x] Testing framework (pytest, 52+ tests, fixture Calibre-schema database)
- [x] First Metadata Engine slice: completeness scoring, validation
      heuristics, non-destructive repair suggestions
- [x] First Repair Engine slice: Author/Title file reorganizer with
      preview, backup, and apply
- [x] First Provider slice: the `MetadataProvider` interface + a
      working `CalibreProvider`
- [x] First Report Engine slice: CSV and JSON writers behind a common interface

Not done in this phase:

- [ ] Wire `utils/logger.py` into the CLI (currently `print()`-only)
- [ ] Custom column support (needs dynamic `custom_column_N` table handling)

## v1.1.0 - Metadata Analysis

- [ ] Duplicate detection (likely title+author fuzzy matching)
- [ ] Wire `MetadataEngine.books_needing_attention()` into a CLI command
      (today `health` only uses the scorer directly)
- [ ] Library health trends over time (needs a place to persist past scores)

## v1.2.0 - Metadata Providers

- [ ] Implement `OpenLibraryProvider.find_candidates()` for real
- [ ] Implement `GoogleBooksProvider.find_candidates()` for real
- [ ] Implement `IsbndbProvider.find_candidates()` for real
- [ ] A `MetadataComparator` that ranks candidates from multiple
      providers against the current Calibre value

## v1.3.0 - Repair Engine (metadata side)

- [ ] Wire `MetadataRepair` suggestions to an approve/reject preview
      flow (mirroring `organize --apply`'s pattern)
- [ ] Cover fetching from provider candidates, with a preview before
      writing into Calibre's cover storage
- [ ] `metadata_repair.py`'s suggestions currently cover two patterns
      (`title_contains_by_clause`, `title_matches_author`) - expand as
      more real-world patterns are found

## v1.4.0 - Reporting

- [ ] `ExcelReport` (needs the `openpyxl` dependency, not yet added to
      `requirements.txt` since nothing uses it yet)
- [ ] `HtmlReport`
- [ ] A "Library Health Report" / "Duplicate Books Report" preset on
      top of the existing `ReportWriter` interface

## v2.0.0 - Desktop Application

- [ ] PySide6 GUI (see `GUI.md`)
- [ ] Plugin marketplace concept for providers/report formats
