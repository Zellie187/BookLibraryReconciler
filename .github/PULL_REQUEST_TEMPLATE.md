## Summary

<!-- What does this PR change, and why? -->

## Related issue

<!-- Closes #... -->

## Checklist

- [ ] `pytest` passes locally
- [ ] `ruff check src tests` passes
- [ ] `black --check src tests` passes
- [ ] `mypy src` passes
- [ ] Added/updated tests for the behavior change
- [ ] Updated `CHANGELOG.md`
- [ ] If this touches `repair/` or writes to `metadata.db`: confirmed
      the preview-first / explicit-apply / backup-before-write pattern
      is preserved
