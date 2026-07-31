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

These are heuristics, not proof of an error - `books_with_issues()`
returns them for a human to review, never to auto-correct.

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
in this library needs a human to look at it" - not yet wired into the
CLI (today's `health` command uses `MetadataScorer` directly), but this
is the class future commands (e.g. a combined `analyze` command) should
build on.
