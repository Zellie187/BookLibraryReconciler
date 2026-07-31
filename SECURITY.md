# Security Policy

## Supported Versions

This project is pre-1.0 (currently `v1.5.0`, see `docs/architecture/Roadmap.md`).
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
- **External metadata providers** (`src/providers/openlibrary/`): the
  only outbound network calls in this project. Requests go to a
  hard-coded `https://openlibrary.org` base URL (`src/config/providers.py`)
  built from either a book's own ISBN or its title/author - never from
  a URL supplied externally, so this isn't SSRF-able. Responses are
  parsed with stdlib `json` (no `eval`/pickle-style deserialization)
  and cached to disk (`src/providers/response_cache.py`) as plain JSON.
  Google Books/ISBNdb are still stubs; when they land, this section
  gets updated for their API key handling (`src/config/providers.py`).
- **Local response cache** (`cache/openlibrary/*.json`): filenames are
  a `sha256` hash of the request URL, not derived from unsanitized
  input, so this isn't a path-traversal vector. Cache contents are
  Open Library's own API responses, not executable.
- **HTML report generation** (`src/reports/html_report.py`): every
  cell value (which ultimately comes from `metadata.db`, i.e. from
  whatever wrote your library's metadata) is passed through
  `html.escape()` before being embedded in the page - never
  string-interpolated raw. A bypass there (a value that renders as
  live HTML/script in a generated report) would be a valid finding.

## Dependencies

Dependencies are pinned to minimum versions in `requirements.txt`. Most
of the application (including CSV/JSON/HTML reports) is stdlib-only;
`openpyxl` and `fpdf2` are used only for `report --format
excel`/`pdf`, and are lazy-imported so the rest of the app works
without them installed (see `docs/architecture/Reports.md`).
