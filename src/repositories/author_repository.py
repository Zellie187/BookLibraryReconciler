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
