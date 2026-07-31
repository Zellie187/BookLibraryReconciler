import sqlite3

import pytest

from core.calibre_functions import calculate_title_sort
from core.database import DatabaseManager
from repositories.author_repository import AuthorRepository


@pytest.fixture
def merge_db(calibre_db_path):

    connection = sqlite3.connect(calibre_db_path)
    connection.create_function("title_sort", 1, calculate_title_sort)
    cursor = connection.cursor()

    # Book 1: King, Stephen (canonical, id=1)
    # Book 2: King| Stephen (duplicate spelling, id=2)
    # Book 3: linked to BOTH id=1 and id=2 (the collision case)
    cursor.execute("INSERT INTO books (id, title) VALUES (1, 'Doctor Sleep')")
    cursor.execute("INSERT INTO books (id, title) VALUES (2, 'The Gunslinger')")
    cursor.execute("INSERT INTO books (id, title) VALUES (3, 'Bad Import')")

    cursor.execute("INSERT INTO authors (id, name, sort, link) VALUES (1, 'Stephen King', 'King, Stephen', '')")
    cursor.execute("INSERT INTO authors (id, name, sort, link) VALUES (2, 'King| Stephen', 'King, Stephen', '')")

    cursor.execute("INSERT INTO books_authors_link (book, author) VALUES (1, 1)")
    cursor.execute("INSERT INTO books_authors_link (book, author) VALUES (2, 2)")
    cursor.execute("INSERT INTO books_authors_link (book, author) VALUES (3, 1)")
    cursor.execute("INSERT INTO books_authors_link (book, author) VALUES (3, 2)")

    connection.commit()
    connection.close()

    manager = DatabaseManager(calibre_db_path)
    manager.connect()

    yield manager

    manager.close()


def test_get_all_author_records_returns_every_author(merge_db):

    repository = AuthorRepository(merge_db)
    records = repository.get_all_author_records()

    assert {(a.id, a.name) for a in records} == {(1, "Stephen King"), (2, "King| Stephen")}


def test_merge_repoints_link_to_canonical(merge_db):

    repository = AuthorRepository(merge_db)
    repository.merge_authors(canonical_author_id=1, duplicate_author_ids=[2])

    cursor = merge_db.connection.cursor()
    cursor.execute("SELECT author FROM books_authors_link WHERE book = 2")
    assert cursor.fetchone()[0] == 1


def test_merge_drops_link_when_book_already_has_canonical(merge_db):

    repository = AuthorRepository(merge_db)
    repository.merge_authors(canonical_author_id=1, duplicate_author_ids=[2])

    cursor = merge_db.connection.cursor()
    cursor.execute("SELECT author FROM books_authors_link WHERE book = 3")
    rows = cursor.fetchall()

    # book 3 was linked to both 1 and 2 - after merging, only one link to 1 remains.
    assert [row[0] for row in rows] == [1]


def test_merge_deletes_the_duplicate_author_row(merge_db):

    repository = AuthorRepository(merge_db)
    repository.merge_authors(canonical_author_id=1, duplicate_author_ids=[2])

    remaining_ids = {a.id for a in repository.get_all_author_records()}
    assert remaining_ids == {1}
