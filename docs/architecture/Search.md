# Search Module (v1.1.0)

```
SearchController
      |
SearchService
      |
BookRepository
      |
SQLite
```

Unlike the diagram's implication of dynamic SQL, `SearchService` loads
the library once (`BookRepository.get_books(limit=None)`, the same
call `health`/`organize` already use) and filters/sorts the resulting
`list[Book]` in memory - see `Architecture.md`'s note on why this
project favors in-memory processing over a dynamic query builder at
this library size.

## `SearchCriteria` (`src/models/search_criteria.py`)

One AND-combined condition: `{field, operator, value}`. A search is
just `list[SearchCriteria]` - `SearchService.search()` requires a book
to satisfy every one of them.

## `SearchService` (`src/services/search_service.py`)

### Fields

`title`, `author`, `isbn`, `uuid`, `series`, `publisher`, `language`,
`tag`, `format`, `comments`, `path`, `date_added` (Calibre's
`timestamp`), `last_modified`, `rating`, `has_cover`.

Every field is extracted as a *list* of raw values (`FIELD_EXTRACTORS`)
so multi-valued fields (authors, tags, languages, formats) and
single-valued fields are matched identically - a criteria matches a
book if it matches *any* of that field's values.

### Operators

| Operator | Meaning |
|---|---|
| `exact` | case-insensitive whole-string match |
| `contains` | case-insensitive substring (default for text fields) |
| `starts_with` / `ends_with` | case-insensitive prefix/suffix |
| `regex` | `re.search()`, case-insensitive; invalid patterns raise `ValueError` rather than crashing |
| `fuzzy` | `difflib.SequenceMatcher` ratio >= 0.6 (stdlib only, no new dependency) |
| `missing` / `present` | field is empty (or the list of values is empty, e.g. no series) / has a value |
| `eq` / `gte` / `lte` / `gt` / `lt` | numeric comparison (default `eq` for `rating` when no mode is given) |

### Sorting

`title`, `author`, `series` (name, then `series_index`), `rating`,
`date_added`, `last_modified`, `size` - see `SORT_KEYS`. `descending`
reverses the sort; ties preserve the original (id) order since Python's
sort is stable.

## `SearchController` (`src/controllers/search_controller.py`)

Parses the CLI's small query syntax into `SearchCriteria`, so
`SearchService` never has to know anything about text parsing:

```
field=value              contains (default) - or eq for numeric fields
field:mode=value          exact/contains/starts_with/ends_with/regex/fuzzy
field:missing             field:present
field>=value              field<=value / field>value / field<value
```

Plus aliases matching the spec's "Missing ISBN" / "Has Cover" style
filters: `missing-isbn`, `missing-cover`, `has-cover`, `missing-series`,
`missing-description`, `missing-publisher`, `missing-language`,
`missing-tags`, `missing-rating`.

Parsing order matters and is deliberate: a `field:mode=value` check
only fires when the colon appears *before* the first `=` - this is why
`path=C:\Books\file.epub` (a colon inside the *value*, from a Windows
path) still parses as a plain `field=value` term instead of being
misread as `field:mode`.

## CLI

```bash
python run.py search "author=King" "series:exact=Dark Tower" "isbn:missing" --sort title
python run.py search missing-cover missing-isbn --sort rating --desc
python run.py search "rating>=4" --csv
```

Each result line shows exactly the fields the spec calls for: cover
(yes/no - no image rendering without a GUI), title, author, series,
rating, metadata score (via `MetadataScorer`, see `Metadata-Engine.md`),
ISBN, and formats. `--csv` writes the same fields for every match
(not just the printed page) to `output/search_results.csv` via
`ReportWriter.write_search_results()`.

## Not implemented (see `Roadmap.md`)

Instant search, saved searches, search history, and smart collections
are GUI-era features (`GUI.md`) - the CLI is a single request/response
tool, so there's no "session" for history or instant-as-you-type to
attach to yet.
