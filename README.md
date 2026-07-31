# BookLibraryReconciler

An open-source book library analysis and metadata reconciliation platform.
It points at a **Calibre** library, tells you what's wrong with your
metadata, and can safely reorganize messy filenames/folders into a clean
`Author/Title` layout without breaking Calibre's own database.

Status: v1.0.0-alpha (foundation + first reorganize/health-scoring slice).

## Requirements

- Python 3.14+
- A Calibre library (a `metadata.db` file). A small sample library
  (`data/metadata.db`, 7,000+ real-world-messy entries) is bundled for
  trying the tool out before pointing it at your own books.

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

**Before running `organize --apply` against a real library: close
Calibre first.** Calibre keeps its own connection to `metadata.db` open
while it runs, and having two processes writing to it at once can
corrupt the database.

## Usage

Always run through `run.py`:

```bash
python run.py preview --limit 10   # show N books + basic library stats (default command)
python run.py health --limit 10    # metadata completeness score per book
python run.py organize --limit 10  # preview a reorganize, changes nothing
python run.py organize --apply     # back up metadata.db, then actually move files
```

Add `--csv` to `health` or `organize` to write the full results to
`output/health_report.csv` / `output/organize_plan.csv`.

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
Application Layer   (src/main.py)
Service Layer       (src/services)
Repository Layer    (src/repositories)  -- reads/writes metadata.db
Builder Layer       (src/builders)      -- assembles Book objects
Domain Models       (src/models)
Metadata Engine     (src/metadata)      -- completeness/health scoring
Repair Engine       (src/repair)        -- reorganize plan + apply + backup
Reports             (src/reports)       -- CSV exports
```

## Not implemented yet

- External metadata providers (Open Library, Google Books, ISBNdb) —
  stubs exist in `src/services/` but are not wired up (planned v1.2.0).
- EPUB-embedded metadata reading (`src/readers/epub_reader.py`) — not
  needed for the Calibre-first workflow above.
- Duplicate detection, cover-fetching, Excel/HTML reports, GUI — see
  the version roadmap in `CHANGELOG.md` (v1.1.0 and later).

## License

MIT
