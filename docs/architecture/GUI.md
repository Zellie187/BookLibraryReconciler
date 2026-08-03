# GUI (v2.0.0-alpha + v2.0.0-alpha.2 shipped, v2.0.0 planned)

An MVP is built: `python run.py gui` opens a two-tab window - a
searchable library table with a read-only book detail dialog, and a
Dashboard tab showing library health at a glance. See `Roadmap.md`'s
v2.0.0-alpha and v2.0.0-alpha.2 entries for the full list of what's
done. This document covers the design decisions - both the ones
already implemented and the ones still ahead for the full v2.0.0
scope.

## Technology

PySide6 (Qt for Python). Lazy-imported, same pattern as `Pillow`/
`openpyxl`/`fpdf2` - the rest of the CLI runs without it installed,
and `python run.py gui` prints a friendly install message if it's
missing rather than crashing with an `ImportError` traceback.

## What's built (`src/gui/`)

```
gui/
    main_window.py         MainWindow - "Library"/"Dashboard" tabs, search bar, status bar
    book_table_model.py    BookTableModel - read-only QAbstractTableModel
    book_detail_dialog.py  BookDetailDialog - double-click a row for full detail
    dashboard_widget.py    DashboardWidget - library health at a glance
```

`MainWindow` doesn't parse search queries itself - it hands the typed
text straight to `SearchController(app.search_service)`, the exact
same class the CLI's `search` command uses. This means the GUI search
box and `python run.py search "..."` understand identical query syntax
(`author=King`, `isbn:missing`, `rating>=4`, ...; see `Search.md`) by
construction, not by convention - there's only one place (`SearchController`)
that parses search terms into `SearchCriteria`.

`BookTableModel` is deliberately read-only: no `setData()`/`flags()`
write path. It only ever displays whatever `Book` objects it's given;
saving/repairing/organizing stays CLI-only for now (see "Not yet
built" below).

`DashboardWidget` doesn't compute anything new either - `compute_stats()`
is a plain function (no Qt dependency, directly unit-testable) that
just calls `LibraryAnalyzer` and `LibraryInspector`, the exact same
analyzers `python run.py preview`/`analyze` already use. Total books,
unique authors/series, average health score, books needing attention,
missing ISBN/cover/description counts, and ISBN/title duplicate group
+ series-order-issue counts, laid out as a 3-column grid of stat tiles
with a manual "Refresh" button (no auto-refresh - recomputing
duplicate detection over the whole library isn't instant, so it's
opt-in, not on every keystroke or tab switch).

## CLI: `python run.py gui`

No arguments. Launches the window and blocks on Qt's event loop
(`QApplication.exec()`) until closed.

## Testing a GUI without a real display

`tests/test_gui_book_table_model.py` tests `BookTableModel`'s logic
directly (`data()`, `headerData()`, `set_books()`, `book_at()`) without
needing a rendered window. A session-scoped `qt_app` fixture in
`tests/conftest.py` provides the one `QApplication` instance every GUI
test that needs one shares (`QApplication` is a singleton -
constructing a second one raises). `conftest.py` also sets
`QT_QPA_PLATFORM=offscreen` before that fixture ever runs, so the
suite works on a CI box with no attached display - CI additionally
needs a few system Qt libraries installed via `apt` (see
`.github/workflows/python.yml`) since PySide6's wheels don't bundle
everything Linux needs, even for the offscreen platform.
`tests/test_gui_dashboard_widget.py` tests `compute_stats()` the same
way, but since that function has no Qt dependency at all, those tests
don't need the `qt_app` fixture (or even `QT_QPA_PLATFORM`) in the
first place.

A real-machine caveat found while building this: under
`QT_QPA_PLATFORM=offscreen` on this Windows dev machine, rendered text
came out as blank glyph boxes (no font found for the offscreen
platform) even though the window's *structure* - column count, layout
regions, row/field counts - was all correct. Switching to the native
`windows` platform (no forced offscreen) rendered every label
correctly, confirmed with actual screenshots (`QWidget.grab()`) of the
running window and detail dialog. The CI workflow installs
`fontconfig`/`fonts-dejavu-core` alongside the Qt system libraries as
a precaution, though this hasn't been verified against a real GitHub
Actions run.

## Not yet built (rest of the spec's v2.0.0 scope)

- Grid/list library views (table only for now).
- Metadata comparison - side-by-side `MetadataCandidate` objects from
  multiple providers (see `Providers.md`) with a pick-a-value UI,
  feeding into `metadata/metadata_repair.py`'s suggestion model. The
  CLI's `lookup` command already does the comparison at the text
  level; this is its GUI equivalent.
- Repair wizard - a visual front-end for what `python run.py organize`/
  `repair --apply` already do at the CLI: preview a plan, let the user
  deselect individual books, then apply with the same backup-first
  guarantee.
- Report viewer - render whatever `reports/` can produce (CSV/JSON/
  HTML/Excel/PDF - see `Reports.md`).
- Cover Download Engine front-end, and a `--provider` picker in the
  GUI matching the CLI's `openlibrary`/`googlebooks`/`internetarchive`
  choice.
- Instant search, saved searches, search history, smart collections -
  the current search box is a manual one-shot query, same as the CLI.
- Settings screen - `Settings/config.json` still needs hand-editing.
- Notifications.

## `resources/`

Reserved for UI assets, kept out of `src/` so packaging (e.g.
PyInstaller) doesn't need to special-case which files under `src/` are
code versus assets:

```
resources/
    icons/
    images/
    themes/
    fonts/
```

All four currently contain only a `.gitkeep` placeholder - the MVP
doesn't use any custom icons/themes/fonts yet, it renders with
whatever Qt/the OS provides by default.

## Design constraint carried over from the CLI

Whatever the GUI ends up doing, it inherits the project's one
non-negotiable rule: no destructive action (a metadata write, a file
move) happens without an explicit preview step and an explicit user
approval, mirroring `repair/organize_applier.py`'s preview/apply split.
The MVP shipped in v2.0.0-alpha doesn't write anything at all yet, so
this constraint hasn't been tested by the GUI itself - it becomes
load-bearing once the repair wizard and metadata-comparison apply path
are built.
