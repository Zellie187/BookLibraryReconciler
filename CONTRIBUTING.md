# Contributing to BookLibraryReconciler

Thanks for considering a contribution. This project is still in its
alpha foundation stage (see `CHANGELOG.md` for what's built so far and
the roadmap for what's next), so expect the architecture to keep
settling for a while.

## Coding style

- Python 3.14+, type hints on public function signatures.
- Formatted with `black` and linted with `ruff` (`pyproject.toml` holds
  the config for both, plus `mypy`):

```bash
black src tests
ruff check src tests
mypy src
```

- Docstrings explain *why*, not *what* - the code should already read
  clearly enough that a comment restating it would be noise.
- Follow the existing layering (see `docs/architecture/Architecture.md`):
  `app` -> `services` -> `repositories` -> `core`/`config`, with
  `providers`, `metadata`, `repair`, and `reports` as their own
  independent packages. Don't reach across layers (e.g. a repository
  should never import from `services`).
- No feature you add should be able to write to a real Calibre library
  or delete anything without an explicit, separate "apply" step and a
  backup - see `repair/organize_applier.py` and `repair/backup.py` for
  the pattern to follow.

## Branch strategy

- `main` is always releasable.
- Branch names: `feature/<short-description>`, `fix/<short-description>`,
  `docs/<short-description>`.
- Rebase on `main` before opening a pull request; avoid merge commits
  in feature branches.

## Commit conventions

Commit subject lines are short, imperative, and describe *why* over
*what* (the diff already shows what changed):

```
Fix ISBN lookup missing the 979 EAN prefix
Add Google Books provider stub behind the MetadataProvider interface
```

Reference an issue number in the body when one exists.

## Pull request process

1. Make sure `pytest`, `ruff check`, `black --check`, and `mypy` all
   pass locally (the `python.yml` GitHub Actions workflow runs the
   same checks on every PR).
2. Add or update tests for any behavior change - see `tests/conftest.py`
   for the fixture Calibre-schema database used across the suite.
3. Update `CHANGELOG.md` under an "Unreleased" or the current version
   heading.
4. Open the PR against `main` using the template in
   `.github/PULL_REQUEST_TEMPLATE.md`. Small, focused PRs review faster
   than large ones.
5. A maintainer will review and may ask for changes before merging.
