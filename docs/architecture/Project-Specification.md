# Project Specification

- Version: v1.2.0 (see `Roadmap.md` for the full version sequence)
- Language: Python 3.14+
- License: MIT

## Purpose

BookLibraryReconciler is an open-source book library analysis and
metadata reconciliation platform. It helps users manage, clean,
analyse, and improve digital book libraries regardless of the original
library software used.

First supported platform: **Calibre**.

Future support: folder-based libraries, Komga, Kavita, and other ebook
management systems.

## Problem Statement

Large digital libraries often suffer from:

- Missing ISBN information
- Missing covers
- Missing descriptions
- Incorrect author names
- Duplicate books
- Incorrect series information
- Inconsistent metadata
- Poor file organisation

Existing tools can manage books, but they typically lack cross-library
analysis, metadata health scoring, automated reconciliation, external
metadata comparison, and safe repair workflows.

## Vision

```
Import Library
      |
Analyse Metadata
      |
Identify Problems
      |
Find Better Metadata
      |
Preview Changes
      |
Apply Repairs
      |
Generate Reports
```

## Domain Model

The central object is the **Book**:

```
Book
 |-- Title
 |-- Authors
 |-- Series
 |-- Publisher
 |-- ISBN / Identifiers
 |-- Description (comments)
 |-- Covers
 |-- Formats (with on-disk filenames and sizes)
 |-- Tags / Languages / Rating
 `-- Metadata Score (computed, not stored - see Metadata-Engine.md)
```

External providers improve this object:

```
Calibre -> Book Object -> Open Library -> Improved Book Object -> Repair Engine
```

See `docs/architecture/Architecture.md` for how the code implements this.

## Success Criteria

A user can point BookLibraryReconciler at a library and answer:

- What books do I have?
- What metadata is missing?
- Which books need attention?
- Which metadata is better?
- How can I improve my collection safely?

## Non-negotiable rule

**No automatic destructive changes.** Every metadata or filesystem
modification requires a human to review a preview and explicitly
approve it (see `repair/organize_applier.py` and
`metadata/metadata_repair.py` for how this is enforced in code).

## Current status vs. this spec

See `Roadmap.md` for what's implemented today versus what's planned.
