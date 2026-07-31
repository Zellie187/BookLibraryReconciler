"""
Shared pytest fixtures.

Builds a small SQLite database matching Calibre's metadata.db schema
(only the tables/columns this project reads or writes) so tests never
depend on a real Calibre library.
"""

import sqlite3

import pytest

from core.database import DatabaseManager

SCHEMA = """
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT,
    sort TEXT,
    timestamp TEXT,
    pubdate TEXT,
    series_index REAL,
    author_sort TEXT,
    path TEXT,
    uuid TEXT,
    has_cover BOOL,
    last_modified TEXT
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    sort TEXT,
    link TEXT
);

CREATE TABLE books_authors_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    author INTEGER
);

CREATE TABLE series (
    id INTEGER PRIMARY KEY,
    name TEXT,
    sort TEXT,
    link TEXT
);

CREATE TABLE books_series_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    series INTEGER
);

CREATE TABLE identifiers (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    type TEXT,
    val TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    text TEXT
);

CREATE TABLE publishers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    sort TEXT,
    link TEXT
);

CREATE TABLE books_publishers_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    publisher INTEGER
);

CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    rating INTEGER,
    link TEXT
);

CREATE TABLE books_ratings_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    rating INTEGER
);

CREATE TABLE languages (
    id INTEGER PRIMARY KEY,
    lang_code TEXT,
    link TEXT
);

CREATE TABLE books_languages_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    lang_code INTEGER,
    item_order INTEGER
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT,
    link TEXT
);

CREATE TABLE books_tags_link (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    tag INTEGER
);

CREATE TABLE data (
    id INTEGER PRIMARY KEY,
    book INTEGER,
    format TEXT,
    uncompressed_size INTEGER,
    name TEXT
);
"""


@pytest.fixture
def calibre_db_path(tmp_path):

    db_path = tmp_path / "metadata.db"

    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA)
    connection.commit()
    connection.close()

    return db_path


@pytest.fixture
def seeded_db(calibre_db_path):
    """
    Two books:
      1: complete metadata, single format, no series.
      2: messy title/author (mirrors real-world Calibre imports),
         two formats, a series, no ISBN/cover/comments.
    """

    connection = sqlite3.connect(calibre_db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO books (id, title, sort, timestamp, pubdate, series_index, "
        "author_sort, path, uuid, has_cover) VALUES "
        "(1, 'Doctor Sleep', 'Doctor Sleep', '2020-01-01', '2013-01-01', 0, "
        "'King, Stephen', 'Stephen King/Doctor Sleep (1)', 'uuid-1', 1)"
    )
    cursor.execute(
        "INSERT INTO books (id, title, sort, timestamp, pubdate, series_index, "
        "author_sort, path, uuid, has_cover) VALUES "
        "(2, 'The Maze of Bones by Rick Riordan', 'Maze of Bones', '2020-01-02', '', 1.0, "
        "'Unknown', 'Unknown/The Maze of Bones by Rick Riordan (2)', 'uuid-2', 0)"
    )

    cursor.execute("INSERT INTO authors (id, name, sort, link) VALUES (1, 'Stephen King', 'King, Stephen', '')")
    cursor.execute("INSERT INTO books_authors_link (book, author) VALUES (1, 1)")

    cursor.execute("INSERT INTO identifiers (book, type, val) VALUES (1, 'isbn', '9781501144525')")
    cursor.execute("INSERT INTO comments (book, text) VALUES (1, 'A haunted boy grows up.')")

    cursor.execute("INSERT INTO publishers (id, name, sort, link) VALUES (1, 'Scribner', 'Scribner', '')")
    cursor.execute("INSERT INTO books_publishers_link (book, publisher) VALUES (1, 1)")

    cursor.execute("INSERT INTO ratings (id, rating, link) VALUES (1, 8, '')")
    cursor.execute("INSERT INTO books_ratings_link (book, rating) VALUES (1, 1)")

    cursor.execute("INSERT INTO languages (id, lang_code, link) VALUES (1, 'eng', '')")
    cursor.execute("INSERT INTO books_languages_link (book, lang_code, item_order) VALUES (1, 1, 0)")

    cursor.execute("INSERT INTO tags (id, name, link) VALUES (1, 'Horror', '')")
    cursor.execute("INSERT INTO books_tags_link (book, tag) VALUES (1, 1)")

    cursor.execute("INSERT INTO series (id, name, sort, link) VALUES (1, 'The Shining', 'Shining, The', '')")
    cursor.execute("INSERT INTO books_series_link (book, series) VALUES (1, 1)")

    cursor.execute(
        "INSERT INTO data (book, format, uncompressed_size, name) VALUES "
        "(1, 'EPUB', 1000, 'Doctor Sleep - Stephen King')"
    )
    cursor.execute(
        "INSERT INTO data (book, format, uncompressed_size, name) VALUES "
        "(2, 'PDF', 2000, 'The Maze of Bones by Rick Riord - Unknown')"
    )

    connection.commit()
    connection.close()

    return calibre_db_path


@pytest.fixture
def database_manager(seeded_db):

    manager = DatabaseManager(seeded_db)
    manager.connect()

    yield manager

    manager.close()
