# Report Engine

```
ReportWriter (abstract: write_table(headers, rows, output_path))
    |
    +-- CsvReport    - stdlib csv
    +-- JsonReport   - stdlib json
    +-- HtmlReport   - stdlib only, self-contained styled <table>
    +-- ExcelReport  - openpyxl (optional dependency, lazy-imported)
    +-- PdfReport    - fpdf2 (optional dependency, lazy-imported)
```

Every format writer only has to implement `write_table(headers, rows,
output_path)` - a single flat table. `base_report.py`'s content methods
(`write_organize_plan`, `write_health_report`, `write_search_results`,
and the four preset reports below) all shape their data into
`(headers, rows)` and hand it to `write_table()`, so adding a new
report *type* never touches the format writers, and adding a new
format writer never touches the report content.

## Optional dependencies, lazy-imported

`ExcelReport` and `PdfReport` `import openpyxl` / `import fpdf` inside
`write_table()`, not at module load time. If the package isn't
installed, calling that specific writer raises a clear `ImportError`
("Excel reports need the optional 'openpyxl' dependency - install it
with: pip install openpyxl") instead of crashing on `import
reports.excel_report` at startup - CSV/JSON/HTML and everything else in
the app work with zero runtime dependencies either way.
`requirements.txt` includes both anyway so CI actually exercises these
code paths, not just their fallback.

## The four preset reports (`base_report.py`)

| Method | Spec name | Shape |
|---|---|---|
| `write_library_health_summary(books)` | Library Health | `(metric, value)` - total books, unique authors/series/formats, average metadata score, missing ISBN/description/cover/publisher/language counts |
| `write_duplicate_report(isbn_groups, title_groups, author_groups=None)` | Duplicate Report | `(type, reason, ids)` - `type` is `isbn`/`title`/`author`; duplicate *files* aren't detected yet (see `Roadmap.md`) |
| `write_series_report(issues)` | Series Report | `(series_name, issue_type, detail)` - reuses `SeriesOrderIssue` from `series_order.py` directly |
| `write_statistics_report(books)` | Statistics | `(category, label, value)` - see below |

`write_library_health_summary` is deliberately distinct from
`write_health_report`/`write_library_analysis`: those are one row per
*book*; this is one row per library-wide *metric*. Don't confuse the
three - "health" appears in all three names for a reason (they're all
downstream of the same `MetadataScorer`/`LibraryAnalyzer`), but they
answer different questions.

## `analyzers/library_statistics.py` - long format, not one section per breakdown

The spec's Statistics report has six breakdowns (books per author,
series, language, year, largest books, smallest books). Rather than
model that as six separate tables/sheets/sections - which would need
every format writer to support a multi-section concept, expanding the
`ReportWriter` interface - `LibraryStatistics` and
`write_statistics_report` emit **one flat table** with a `category`
column identifying which breakdown each row belongs to:

```
category,label,value
books_per_author,Maxwell Grant,336
books_per_author,Koontz| Dean,140
books_per_series,The Shadow,336
books_per_year,2020,412
largest_books,War and Peace,3245891
```

This is standard "long"/"tidy" format - trivially filterable/pivotable
in a spreadsheet, and it means `write_statistics_report` needed zero
new format-writer code at all. Verified against the bundled 7,000-book
sample: 1,468 authors and 2,365 series produce a ~3,855-row table
across all formats without issue (CSV 142KB, JSON 377KB, Excel 88KB,
PDF 202KB - all sane sizes, not exploding).

Two sentinel exclusions, consistent with how this project already
treats Calibre's other "not really set" placeholder values
(`series_index == 0` in `series_order.py`):

- **`books_per_year`** excludes Calibre's `"0101-01-01"` "no pubdate
  recorded" sentinel - in the bundled sample, 7,028 of 7,029 books have
  this exact placeholder, so without the exclusion this breakdown would
  be almost entirely meaningless noise.
- **`smallest_books`** excludes books with `size == 0` (no format files
  at all) - otherwise every book missing a file would tie for
  "smallest," crowding out books that actually have a small file.

## CLI

```bash
python run.py report --type health --format csv
python run.py report --type duplicates --format excel
python run.py report --type series --format html
python run.py report --type statistics --format pdf --output my_stats.pdf
```

`--type` (default `health`) is one of `health`/`duplicates`/`series`/`statistics`.
`--format` (default `csv`) is one of `csv`/`json`/`excel`/`html`/`pdf`,
dispatched through `main.py`'s `FORMAT_WRITERS` registry. `--output`
overrides the default `output/<type>_report.<ext>` path.

## Not implemented (see `Roadmap.md`)

- Duplicate *file* detection (duplicate *books*, by ISBN or title, and
  duplicate *authors* are all covered).
- Scheduling (manual/automatic/on-demand) - there's no long-running
  process to attach a schedule to yet; this is really a GUI-era or
  separate-scheduler-process concern.
