# Changelog

All notable changes to this project will be documented here.

---

## Version 1.0.0-alpha

### Added
- Repositories (gateway layer) for publishers, ratings, languages, tags,
  and on-disk formats, completing the entity list from the dev spec.
- `BookBuilder` now assembles the full `Book` object: publisher, pubdate,
  rating, languages, tags, and format files (with sizes).
- Metadata Engine (`src/metadata/health_score.py`): per-book completeness
  scoring (title/author/ISBN/cover/description) plus library averages.
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