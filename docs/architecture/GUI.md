# GUI (Planned - v2.0.0)

Not built yet. This document exists so the eventual desktop
application has a landing spot for its design decisions, and so
`resources/` isn't a mystery folder in the meantime.

## Technology

PySide6 (Qt for Python).

## Planned features

- Dashboard - library health at a glance (average metadata score,
  counts of missing ISBN/cover/description, unique authors/series).
- Search / filters over the loaded library.
- Metadata comparison - side-by-side `MetadataCandidate` objects from
  multiple providers (see `Providers.md`) with a pick-a-value UI,
  feeding into `metadata/metadata_repair.py`'s suggestion model.
- Repair wizard - a visual front-end for what `python run.py organize`
  already does at the CLI: preview a plan, let the user deselect
  individual books, then apply with the same backup-first guarantee.
- Reports - render whatever `reports/` can produce (currently CSV/JSON;
  see `Roadmap.md` for Excel/HTML).

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

All four currently contain only a `.gitkeep` placeholder.

## Design constraint carried over from the CLI

Whatever the GUI ends up doing, it inherits the project's one
non-negotiable rule: no destructive action (a metadata write, a file
move) happens without an explicit preview step and an explicit user
approval, mirroring `repair/organize_applier.py`'s preview/apply split.
