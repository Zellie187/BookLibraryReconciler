# GUI (v2.0.0-alpha through v2.0.0-alpha.8 shipped, v2.0.0 planned)

An MVP is built: `python run.py gui` opens a six-tab window - a
searchable library table with a read-only book detail dialog (which
opens a read-only Metadata Comparison dialog and a Cover Finder dialog
that *can* save a cover), a Dashboard tab showing library health at a
glance, a Reports tab rendering the 4 CLI report presets as text, an
Organize tab and a Repair tab (the two halves of the repair wizard -
preview + selectively apply a reorganization, and preview +
selectively apply title repairs/duplicate-author merges), and a
Settings tab editing `Settings/config.json`. See `Roadmap.md`'s
v2.0.0-alpha through v2.0.0-alpha.8 entries for the full list of
what's done. This document covers the design decisions - both the
ones already implemented and the ones still ahead for the full
v2.0.0 scope.

## Technology

PySide6 (Qt for Python). Lazy-imported, same pattern as `Pillow`/
`openpyxl`/`fpdf2` - the rest of the CLI runs without it installed,
and `python run.py gui` prints a friendly install message if it's
missing rather than crashing with an `ImportError` traceback.

## What's built (`src/gui/`)

```
gui/
    main_window.py                MainWindow - "Library"/"Dashboard"/"Reports"/"Settings" tabs, search bar, status bar
    book_table_model.py           BookTableModel - read-only QAbstractTableModel
    book_detail_dialog.py         BookDetailDialog - double-click a row for full detail
    dashboard_widget.py           DashboardWidget - library health at a glance
    metadata_comparison_dialog.py MetadataComparisonDialog - Calibre vs. a chosen provider
    report_viewer_widget.py       ReportViewerWidget - the 4 CLI report presets, as text
    settings_widget.py            SettingsWidget - edits Settings/config.json
    cover_finder_dialog.py        CoverFinderDialog - find + apply a cover (writes cover.jpg)
    organize_wizard_widget.py     OrganizeWizardWidget - preview + selectively apply a reorganization
    repair_wizard_widget.py       RepairWizardWidget - preview + selectively apply title repairs/author merges
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

`MetadataComparisonDialog` (opened via a "Compare Metadata..." button
on `BookDetailDialog`) is the GUI equivalent of `python run.py lookup`:
Calibre's current metadata next to whatever candidates the chosen
provider finds, with the same `--provider`/`--offline` options as a
dropdown and checkbox. Same scope as `lookup` too - no write path.
`format_comparison()` is the display-text formatting step, kept as a
plain function separate from the dialog for the same testability
reason as `compute_stats()`. The provider dropdown reads from
`src/providers/registry.py`'s `PROVIDERS` mapping - the same registry
`main.py`'s `lookup`/`covers` commands use, extracted out of `main.py`
specifically so GUI code could import it without a circular
dependency (`main.py` imports `gui.main_window`, so GUI modules can't
import back from `main.py`).

`ReportViewerWidget` is the "Reports" tab - a dropdown for the same
four presets as `python run.py report --type` and a "Generate" button.
`generate_report_text()` is, once again, a plain function with no Qt
dependency, this time reusing `MetadataScorer`, `DuplicateDetector`,
`AuthorDuplicateFinder`, `find_series_order_issues`, and
`LibraryStatistics` - the exact same analyzers `preview`/`health`/
`analyze`/`report` already use. Unlike the CLI's `report` command,
nothing is written to disk here - the point is an on-screen view, not
a file export (that's still what `python run.py report --format
excel/pdf/...` is for).

`SettingsWidget` is the "Settings" tab: folder/file pickers for
`library_path`/`metadata_db`, backed by `save_settings()` - another
plain function, this one writing exactly the two keys
`config.settings.load_settings()` already reads, so the file format
stays whatever the CLI's existing hand-edit instructions describe (see
README.md). Not live - `config.settings.LIBRARY_ROOT`/`METADATA_DB`
are computed once at import time and threaded through `Application` at
`python run.py gui` startup, so a saved change only takes effect on
the *next* launch; the widget says so rather than pretending otherwise.
The library-folder field is validated (must exist) before saving; the
`metadata.db` field is optional and unvalidated (Calibre's own default
location, `<library_path>/metadata.db`, is used when it's left blank).

`CoverFinderDialog` (opened via a "Find Cover..." button on
`BookDetailDialog`) is the GUI equivalent of `python run.py covers` -
and the first GUI slice that actually writes anything. Unlike the
Metadata Comparison dialog, this isn't blocked by an unanswered policy
question: the CLI's `covers --apply --best|--candidate N` semantics
(backup-first, resize, convert to JPEG, update `has_cover`) were
already decided and tested back in v1.5.1, so this dialog just calls
the same `CoverFinder`/`CoverApplier`/`backup_database` the CLI does,
with the same provider dropdown/offline checkbox as Metadata
Comparison. `format_candidate_line()` and `pick_best_candidate()` are,
once again, plain functions kept separate from the dialog for
testability. Because `MainWindow`/`BookDetailDialog` previously only
threaded `library_service`/`search_service` through (no filesystem
paths), this slice added `library_root`/`database_path` to both
constructors - `CoverFinder`/`CoverApplier`/`backup_database` all need
real paths, not just the service layer. After the detail dialog
closes, `MainWindow` repaints the library table
(`table_model.layoutChanged.emit()`) rather than reloading it, since
`book_at()` returns the same `Book` object `CoverFinderDialog` may
have just mutated (`has_cover`) - a repaint picks up the change
without resetting an active search filter or paying for a redundant
database round-trip.

`OrganizeWizardWidget` is the "Organize" tab - the first half of the
"repair wizard" `GUI.md` always planned, and the second GUI slice that
writes anything. Unlike the still-unbuilt Metadata Comparison *apply*
step, this one isn't blocked by an unanswered policy question: the
CLI's `organize --apply` semantics (backup-first, one book failing
doesn't stop the rest) were already decided and tested. What the CLI
*doesn't* have is per-item selection - `--apply` moves every book in
the plan, all or nothing. The wizard's checkable list (checked by
default, "Select All"/"Select None" convenience buttons) is strictly
*safer* than that, not a new policy - a genuine UI improvement, not a
design risk. `format_plan_line()`/`summarize_apply_results()` are, once
again, plain functions kept separate from the widget for testability.
Because this is a whole-library operation (unlike the per-book Cover
Finder/Metadata Comparison dialogs), it lives as its own top-level tab
rather than something reachable from `BookDetailDialog`.

`RepairWizardWidget` is the "Repair" tab - the second and final half
of the repair wizard, completing the whole concept `GUI.md` described
from the start. Same non-policy-question reasoning as Organize: the
CLI's `repair --apply` semantics (backup-first, auto-applicable-only,
one item failing doesn't stop the rest) were already decided and
tested. Three sections: a checkable list of auto-applicable
title-repair suggestions, a **read-only** list of suggestions needing
manual review (deliberately not checkable - a suggestion with no
concrete `suggested_value` has nothing to apply, matching the CLI's
own "needs manual review" distinction exactly rather than inventing a
new one), and a checkable list of duplicate author groups.
`format_suggestion_line()`/`format_needs_review_line()`/
`format_author_group_line()`/`summarize_repair_results()` are, once
again, plain functions kept separate from the widget for testability.
Like Organize, it's a whole-library operation and lives as its own
top-level tab.

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
- A pick-a-value UI on top of the Metadata Comparison dialog, feeding
  into `metadata/metadata_repair.py`'s suggestion model - the dialog
  itself is built, but it's read-only (text side-by-side), same as
  `lookup`. Applying a chosen candidate's fields back into
  `metadata.db` is still a real, unanswered policy question (per-field
  approve? whole-candidate approve?), not just an implementation gap.
- Exporting the Reports tab's output to CSV/Excel/HTML/PDF from the
  GUI itself - the tab shows the same numbers on screen, but saving to
  disk in a specific format is still CLI-only (`python run.py report
  --format ...`).
- A `--user-folder` equivalent on the Cover Finder dialog - the CLI's
  `covers --user-folder PATH` (local files named `<book_id>.jpg/.png/
  .webp`) has no GUI picker yet; only provider-sourced candidates are
  shown.
- Instant search, saved searches, search history, smart collections -
  the current search box is a manual one-shot query, same as the CLI.
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
`CoverFinderDialog` (v2.0.0-alpha.6), `OrganizeWizardWidget`
(v2.0.0-alpha.7), and `RepairWizardWidget` (v2.0.0-alpha.8) all prove
this: candidates/plans/suggestions are previewed first, nothing is
written until an explicit apply click, and `backup_database()` runs
before every save - the same rule the CLI has always followed, now
exercised by the GUI itself for every write path except one. The only
remaining write path this constraint hasn't been tested against is a
Metadata Comparison apply step, which doesn't exist yet - and won't,
until the per-field-vs-whole-candidate policy question is actually
answered rather than deferred.
