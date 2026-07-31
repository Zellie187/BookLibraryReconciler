"""
Author Repository
"""

from collections import defaultdict

from models.author import Author


class AuthorRepository:

    def __init__(self, database_manager):

        self.db = database_manager

    # ---------------------------------------------------------

    def get_authors_for_book(self, book_id):

        return self.get_all_authors().get(book_id, [])

    # ---------------------------------------------------------

    def get_all_authors(self):

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT

                bal.book,

                a.id,
                a.name,
                a.sort,
                a.link

            FROM books_authors_link bal

            JOIN authors a

                ON a.id = bal.author

            ORDER BY bal.book
            """)

        books = defaultdict(list)

        for row in cursor.fetchall():

            author = Author()

            author.id = row["id"]
            author.name = row["name"]
            author.sort = row["sort"]
            author.link = row["link"]

            books[row["book"]].append(author)

        return books

    # ---------------------------------------------------------

    def get_all_author_records(self):
        """
        Every distinct author row (regardless of book linkage) - used
        for duplicate-author detection, which cares about the authors
        table itself, not which books reference it.
        """

        cursor = self.db.connection.cursor()

        cursor.execute("SELECT id, name, sort, link FROM authors ORDER BY id")

        authors = []

        for row in cursor.fetchall():

            author = Author()

            author.id = row["id"]
            author.name = row["name"]
            author.sort = row["sort"]
            author.link = row["link"]

            authors.append(author)

        return authors

    # ---------------------------------------------------------

    def merge_authors(self, canonical_author_id, duplicate_author_ids):
        """
        Repoint every book linked to a duplicate author over to the
        canonical author id, then delete the now-unused duplicate
        author rows. If a book is already linked to both, the
        duplicate link is simply dropped rather than creating a
        second link to the same author.
        """

        cursor = self.db.connection.cursor()

        for duplicate_id in duplicate_author_ids:

            cursor.execute(
                "SELECT book FROM books_authors_link WHERE author = ?",
                (duplicate_id,),
            )
            book_ids = [row["book"] for row in cursor.fetchall()]

            for book_id in book_ids:

                cursor.execute(
                    "SELECT 1 FROM books_authors_link WHERE book = ? AND author = ?",
                    (book_id, canonical_author_id),
                )

                if cursor.fetchone():
                    cursor.execute(
                        "DELETE FROM books_authors_link WHERE book = ? AND author = ?",
                        (book_id, duplicate_id),
                    )
                else:
                    cursor.execute(
                        "UPDATE books_authors_link SET author = ? WHERE book = ? AND author = ?",
                        (canonical_author_id, book_id, duplicate_id),
                    )

            cursor.execute("DELETE FROM authors WHERE id = ?", (duplicate_id,))

        self.db.connection.commit()
