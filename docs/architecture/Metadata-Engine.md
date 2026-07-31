# Metadata Engine

The "intelligence layer" - `src/metadata/`. Operates on `list[Book]`,
never touches the database or filesystem itself.

## `metadata_score.py` - completeness

`MetadataScorer` checks five things per book, each worth 20%: `title`,
`author`, `isbn`, `cover`, `description`. `HealthReport.score` is the
percentage that passed.

```
Book:
Title        v
Author       v
ISBN         x
Cover        v
Description  x

Score: 60%
```

`score_library()` / `average_score()` run this across a whole library.
This is what `python run.py health` reports.

## `metadata_validator.py` - "does this look wrong?"

Scoring only measures *missing* data. `MetadataValidator` flags data
that's *present but probably wrong*, based on patterns actually seen in
the bundled 7,000-book sample library (mixed-source Calibre imports are
full of these):

| Code | Example from the sample library |
|---|---|
| `title_matches_author` | Book #4: title `"Taylor, Roger"`, author name `"Taylor, Roger"` |
| `title_contains_by_clause` | Book #2: title `"The Maze of Bones by Rick Riordan"` |
| `empty_title` | Title is blank/whitespace |
| `series_index_zero` | Book is in a series but `series_index == 0` |
| `invalid_isbn` | ISBN present but fails its checksum (see `isbn_validator.py`) |

These are heuristics, not proof of an error - `books_with_issues()`
returns them for a human to review, never to auto-correct.

### `isbn_validator.py` - checksum only, not a real-ISBN lookup

`is_valid_isbn()` implements the standard ISBN-10 and ISBN-13 check
digit algorithms (stdlib only - `re`, no dependency). It only tells you
whether an ISBN is *internally consistent*; it cannot tell you whether
it's the ISBN for this particular book, or a real ISBN at all - that
needs a provider lookup (`Providers.md`).

## `metadata_repair.py` - suggestions, never automatic

`MetadataRepair` turns a subset of validator findings into concrete
*suggested* field values:

- `title_contains_by_clause` -> suggests the title with the trailing
  `" by <Author>"` clause stripped (e.g. `"The Maze of Bones by Rick
  Riordan"` -> `"The Maze of Bones"`).
- `title_matches_author` -> flagged, but **no** suggested value - the
  real title is genuinely unknown from local data alone (this is
  exactly the kind of case an external provider match, once
  `providers/` goes live, would help resolve).

`suggest_for_book()`/`suggest_for_library()` return `RepairSuggestion`
objects. Nothing calls these automatically and nothing writes them
anywhere - wiring an "apply suggested title" flow is future work, and
per the project's non-negotiable rule (`Project-Specification.md`) it
would still require an explicit human approval step, the same way
`repair/organize_applier.py` does for file moves.

## `metadata_engine.py` - the facade

`MetadataEngine` composes the three pieces above (constructor-injected,
so tests can swap any of them) into one `BookAnalysis` per book:

```python
engine = MetadataEngine()
analysis = engine.analyze_book(book)
# analysis.score, analysis.failed_checks, analysis.issues, analysis.repair_suggestions
# analysis.needs_attention  ->  score < 100 or any issues
```

`books_needing_attention(books)` is the one-call entry point for "what
in this library needs a human to look at it" per book. It's used by
`LibraryInspector` (below), which wires it into `python run.py analyze`
alongside the library-wide checks.

## `duplicate_detector.py` - likely-duplicate books

`DuplicateDetector` never merges or deletes anything - it only returns
`DuplicateGroup(reason, book_ids)` lists for a human to review.

- `find_isbn_duplicates()` - exact match on a non-empty `book.isbn`.
  Strong signal: the same real-world edition recorded under two ids.
- `find_title_duplicates()` - fuzzy title matching (`difflib`,
  threshold 0.95 by default), blocked by primary author so it stays
  fast on large libraries (each book is only ever compared against
  others sharing its first author).

Two exclusions matter and were both found by running this against the
bundled 7,000-book sample and checking the output by hand:

1. **Author-name-echo titles.** A book whose title is just its own
   author's name (any word order/punctuation - "Berry, Steve" /
   "Steve Berry" both match) is a placeholder from a failed import
   (see `title_matches_author` above), not a real title. Grouping ten
   different books that all lack a title as "duplicates of each
   other" would be noise. Without this exclusion the sample library
   produced 265 groups; most weren't real duplicates.
2. **Numbered-volume titles.** `"318 - Maxwell Grant"` vs
   `"317 - Maxwell Grant"` (or `"Elminster 1 - ..."` vs
   `"Elminster 2 - ..."`) share a long template and only differ by a
   digit - `difflib` scores that highly similar even though they're
   different volumes. `_differs_only_by_a_number()` strips digits
   from both titles first and skips the pair if that makes them
   identical. This dropped the sample library from 265 to 46 groups,
   and the 46 remaining are, on inspection, genuinely identical
   titles (almost all real re-imports of the same book).

A trailing re-import marker Calibre itself adds on duplicate import
(`"Point Blank - Coulter, Catherine"` vs `"...Catherine(1)"`) is
*not* excluded - that's exactly the kind of real duplicate this
should catch, and it does.

## `series_order.py` - is a series internally consistent?

`find_series_order_issues(books)` groups books by series and flags:

- `duplicate_position` - two+ books sharing the same `series_index`.
- `gap` - a hole in an otherwise-sequential run of whole-number
  positions (e.g. books at 1, 2, 4 but nothing at 3).

`series_index == 0` (Calibre's "not set" sentinel - already flagged
per-book as `series_index_zero`) is excluded from both checks entirely.
Fractional positions (`1.5`, a between-volumes novella - a normal
Calibre convention) count toward the duplicate-position check but are
excluded from the gap check, which only looks at whole numbers.

## `library_inspector.py` - the whole-library facade

`LibraryInspector.inspect(books)` runs `MetadataEngine`,
`DuplicateDetector`, and `find_series_order_issues()` together and
returns one `LibraryInspection` (per-book analyses, isbn/title
duplicate groups, series order issues, average score, plus a
`books_needing_attention` property). This is what
`python run.py analyze` uses - see the root `README.md` for the CLI.
