"""
Book Library Reconciler

Version 0.7
"""

from core.config import METADATA_DB
from core.database import DatabaseManager
from services.library_service import LibraryService

LINE = "=" * 60


def print_header():

    print(LINE)
    print("📚 BOOK LIBRARY RECONCILER")
    print("Version 0.7")
    print(LINE)


def print_book(book):

    print()

    print(f"ID          : {book.id}")
    print(f"Title       : {book.title}")
    print(f"Authors     : {book.author_names}")
    print(f"Series      : {book.series_name}")
    print(f"Book Number : {book.series_index}")
    print(f"UUID        : {book.uuid}")
    print(f"ISBN        : {book.isbn}")
    print(f"Path        : {book.path}")
    print(f"Cover       : {book.has_cover}")

    if book.comments:

        preview = book.comments.replace("\n", " ")
        preview = preview.replace("\r", " ")

        if len(preview) > 100:
            preview = preview[:100] + "..."

        print(f"Comments    : {preview}")

    if book.identifiers:

        print("\nIdentifiers")

        for key, value in sorted(book.identifiers.items()):

            print(f"    {key:<15} {value}")

    print("-" * 60)


def main():

    print_header()

    print("\nOpening database...\n")

    db = DatabaseManager(METADATA_DB)

    db.connect()

    print("✅ Connected\n")

    library = LibraryService(db)

    total = library.get_book_count()

    print(f"Books in Library : {total:,}")

    print()
    print(LINE)
    print("FIRST 10 BOOKS")
    print(LINE)

    books = library.get_books(limit=10)

    for book in books:

        print_book(book)

    db.close()

    print("\nDatabase Closed")


if __name__ == "__main__":
    main()