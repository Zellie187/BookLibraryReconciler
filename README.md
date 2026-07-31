# BookLibraryReconciler

An open-source book library analysis and metadata reconciliation platform.
It points at a **Calibre** library, tells you what's wrong with your
metadata, and can safely reorganize messy filenames/folders into a clean
`Author/Title` layout without breaking Calibre's own database.

Status: v1.0.0-alpha foundation + v1.1.0 search engine + v1.2.0
metadata analysis/health scoring + v1.3.0 metadata repair engine +
v1.4.0 report engine + v1.5.0 Open Library provider + v1.5.1 Cover
Download Engine shipped.

## Requirements

- Python 3.14+
- A Calibre library (a `metadata.db` file). A small sample library
  (`data/metadata.db`, 7,000+ real-world-messy entries) is bundled for
  trying the tool out before pointing it at your own books.
- Internet access, only for `python run.py lookup` and
  `python run.py covers` (both query Open Library) — every other
  command works fully offline. `--offline` on either restricts them to
  the local response cache.
- `Pillow` (already in `requirements.txt`) for `python run.py covers` -
  only imported when that command actually validates or saves an image.

## Setup

```bash
pip install -r requirements.txt
```

By default the tool reads the bundled sample library in `data/`. To
point it at your own Calibre library, edit `Settings/config.json`:

```json
{
    "library_path": "C:/Users/you/Calibre Library",
    "metadata_db": ""
}
```

Leave `metadata_db` blank to use `<library_path>/metadata.db` (the
normal location Calibre itself uses).

**Before running `organize --apply` or `repair --apply` against a real
library: close Calibre first.** Calibre keeps its own connection to
`metadata.db` open while it runs, and having two processes writing to
it at once can corrupt the database.

## Usage

Always run through `run.py`:

```bash
python run.py preview --limit 10   # show N books + basic library stats (default command)
python run.py health --limit 10    # metadata completeness score per book
python run.py analyze --limit 10   # full inspection: score + validation + duplicates + series order
python run.py repair --limit 10    # preview title-repair suggestions + duplicate-author merges
python run.py repair --apply       # back up metadata.db, then rewrite titles + merge duplicate authors
python run.py organize --limit 10  # preview a reorganize, changes nothing
python run.py organize --apply     # back up metadata.db, then actually move files
python run.py search "author=King" "isbn:missing" --sort title --limit 20
python run.py report --type statistics --format excel
python run.py lookup 1              # compare a book's Calibre metadata against Open Library (read-only)
python run.py covers 1              # find + validate cover candidates for a book (read-only)
python run.py covers 1 --apply --best   # back up metadata.db, then save the best candidate as the cover
```

Add `--csv` to `health`, `analyze`, `repair`, `organize`, or `search`
to write the full results to `output/health_report.csv` /
`output/library_analysis.csv` / `output/repair_suggestions.csv` /
`output/organize_plan.csv` / `output/search_results.csv`.

### How `lookup` works

Read-only: prints Calibre's current metadata for a book id next to
every candidate `OpenLibraryProvider` finds for it (ISBN lookup if the
book has one, otherwise a title/author search). Nothing is written -
there's no `--apply` yet, since deciding which fields to trust and
overwrite is a real policy question this project hasn't answered.
Responses are cached (`cache/openlibrary/`, 1-week TTL); `--offline`
only consults that cache and never touches the network. See
`docs/architecture/Providers.md` for a real data-quality surprise found
while building this (Open Library returning unrelated books for bogus
ISBNs, rather than a clean "not found").

```bash
python run.py lookup 1
python run.py lookup 1 --offline
```

### How `covers` works

Preview-first, same pattern as `repair`/`organize`: finds cover
candidates for a book from Open Library (reusing the `cover_url` a
`lookup`-style call already found - no extra round-trip) and, if given
`--user-folder PATH`, from local files named `<book_id>.jpg/.png/.webp`
in that folder. Each candidate is downloaded and validated (format,
resolution, aspect ratio, corruption, file size) and scored 0-100;
candidates matching the book's existing cover byte-for-byte are
flagged as duplicates. Nothing is written by default.

With `--apply`, pick a candidate explicitly - `--best` (highest score
among valid, non-duplicate candidates) or `--candidate N` (1-indexed,
from the preview list) - and it backs up `metadata.db`, resizes the
image to a maximum 800px dimension, saves it as `cover.jpg` in the
book's folder, and updates `has_cover`. Needs `Pillow`, installed via
`requirements.txt`.

```bash
python run.py covers 1
python run.py covers 1 --offline --user-folder "C:/my-covers"
python run.py covers 1 --apply --best
python run.py covers 1 --apply --candidate 2
```

### How `report` works

Four report presets - `--type health|duplicates|series|statistics` -
each available in five formats - `--format csv|json|excel|html|pdf`
(default `csv`, output to `output/<type>_report.<ext>` unless
`--output` is given). CSV/JSON/HTML need nothing extra; Excel and PDF
need `openpyxl`/`fpdf2` (already in `requirements.txt`), only imported
when you actually pick those formats. See
`docs/architecture/Reports.md` for exactly what each preset contains.

```bash
python run.py report --type health --format html
python run.py report --type duplicates --format excel
python run.py report --type statistics --format pdf --output my_stats.pdf
```

### How `repair` works

Two independent fixes, both preview-first:

- **Title repairs** - `MetadataRepair` suggests stripping a trailing
  `" by <Author>"` clause some imports leave embedded in the title
  itself (e.g. `"The Maze of Bones by Rick Riordan"` ->
  `"The Maze of Bones"`). Only suggestions with a concrete value are
  auto-applicable; titles that are just an echo of the author's own
  name (the real title is genuinely unknown) are always reported as
  needing manual review, never guessed at.
- **Duplicate author merging** - `AuthorDuplicateFinder` groups Calibre
  author records that are the same person recorded differently
  (`"Stephen King"` / `"King, Stephen"` / `"King| Stephen"`), and
  `--apply` repoints every affected book to one canonical author id.

`--apply` backs up `metadata.db` first, same as `organize`. See
`docs/architecture/Metadata-Engine.md` for how a real false-positive
in the title heuristic (misfiring on real titles like "Married by
Morning") was found and fixed before this could ship.

### How `analyze` works

Runs the whole Metadata Engine against the library in one pass:
per-book completeness score and validation issues (wrong-looking
titles, invalid ISBN checksums, series position of 0), plus two
library-wide checks - likely-duplicate books (exact ISBN match, or a
fuzzy title match blocked by author) and series order problems
(duplicate or missing positions). See `docs/architecture/Metadata-Engine.md`
for exactly how the duplicate/false-positive heuristics were tuned
against the bundled sample library.

### How `search` works

Every AND-combined filter term is `field=value`, `field:mode=value`
(`exact`/`contains`/`starts_with`/`ends_with`/`regex`/`fuzzy`),
`field:missing`/`field:present`, or a numeric comparison like
`rating>=4`. Convenience aliases cover the spec's "Missing ISBN"/"Has
Cover" style filters directly: `missing-isbn`, `missing-cover`,
`has-cover`, `missing-series`, `missing-description`. See
`docs/architecture/Search.md` for the full field list, every operator,
and how sorting works.

```bash
python run.py search "series:exact=Dark Tower" "language=eng" --sort series
python run.py search missing-isbn has-cover --sort rating --desc
```

### How `organize` works

For every book, it builds a target path from `Author/Title` (using the
existing Calibre title/author fields — it does not try to "clean up"
the text itself, only where the files live) and renames the format
files inside each book's folder to match. Folder name collisions are
disambiguated with the book's id, the same way Calibre itself does.

Nothing is touched until you pass `--apply`. When you do:

1. `metadata.db` is copied to `metadata.<timestamp>.bak` next to itself.
2. Each book's folder is moved and its format files renamed on disk.
3. The `path` and per-format filename in `metadata.db` are updated to
   match, so Calibre keeps seeing the same book in the same place.

One book failing (e.g. its folder is missing) does not stop the rest —
failures are collected and reported at the end.

## Running tests

```bash
pytest
```

## Architecture

```
Application Layer   (src/app)           -- bootstrap + dependency injection
Controller Layer    (src/controllers)   -- parses CLI query syntax into service calls
Service Layer       (src/services)
Repository Layer    (src/repositories)  -- reads/writes metadata.db
Builder Layer       (src/builders)      -- assembles Book objects
Domain Models       (src/models)
Metadata Engine     (src/metadata)      -- completeness/health scoring, validation, repair suggestions
Repair Engine       (src/repair)        -- reorganize/repair plan + apply + backup, cover find/apply
Reports             (src/reports)       -- CSV/JSON/HTML/Excel/PDF behind a common interface
Providers           (src/providers)     -- pluggable metadata sources (Calibre + Open Library work; Google Books/ISBNdb are stubs)
Configuration       (src/config)        -- paths, Settings/config.json, constants
```

Full write-up, including why each layer exists and how to extend it,
is in `docs/architecture/` - start with `Architecture.md` and
`Developer-Guide.md`.

## Not implemented yet

- Google Books and ISBNdb providers — interface-conformant stubs exist
  in `src/providers/` but raise `NotImplementedError` (planned
  v2.1.0). Calibre and Open Library are both wired up as working
  providers (`src/providers/calibre/`, `src/providers/openlibrary/`).
- Applying a provider's metadata back into `metadata.db` — `lookup`
  shows the comparison; there's no write path yet (a real policy
  question, not just an implementation gap — see `docs/architecture/Roadmap.md`).
- EPUB-embedded metadata reading (`src/readers/epub_reader.py`) — not
  needed for the Calibre-first workflow above.
- GUI, duplicate *file* detection (duplicate *books* by ISBN/title and
  duplicate *authors* are both covered), report scheduling — see
  `docs/architecture/Roadmap.md`.

## Contributing

See `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.

## License

MIT — see `LICENSE`.
