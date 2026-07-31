# Security Policy

## Supported Versions

This project is pre-1.0 (currently `v1.1.0`, see `docs/architecture/Roadmap.md`).
Only the latest commit on `main` is supported with security fixes
until a first stable release tags a supported-versions table here.

## Reporting a Vulnerability

Please **do not open a public issue** for security vulnerabilities.
Instead, use GitHub's private vulnerability reporting
(Security tab -> "Report a vulnerability") on this repository, or
contact the maintainer directly.

Include, where possible:

- A description of the vulnerability and its impact.
- Steps to reproduce it, or a minimal proof of concept.
- The version/commit you tested against.

We aim to acknowledge reports within 5 business days.

## Scope and Known Risk Areas

Given what this project does, the areas most worth scrutiny are:

- **Filesystem operations** (`src/repair/organize_applier.py`): moves
  and renames files based on metadata read from `metadata.db`. Book
  titles/authors are sanitized before being used as path components
  (`src/repair/file_organizer.py:sanitize_component`) specifically to
  prevent path traversal or invalid-path issues; a bypass there would
  be a valid finding.
- **Database writes** (`src/repositories/*.py`): all queries use
  parameterized SQL (`?` placeholders) - never string-interpolated
  values - to avoid SQL injection. Table/column names that are
  interpolated (e.g. `PRAGMA table_info({table_name})` in
  `src/core/schema_explorer.py`) are only ever fed known,
  hard-coded names, not user input.
- **External metadata providers** (`src/providers/`): not implemented
  yet. When Open Library/Google Books/ISBNdb support lands, this
  section will be updated to cover network-facing concerns (SSRF,
  response parsing, API key handling via `src/config/providers.py`).

## Dependencies

Development dependencies are pinned to minimum versions in
`requirements.txt`. The application itself has no runtime dependencies
outside the Python standard library.
