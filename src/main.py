"""
Book Library Reconciler
"""

import argparse
import sys

from analyzers.library_analyzer import LibraryAnalyzer
from core.config import LIBRARY_ROOT, METADATA_DB, OUTPUT_FOLDER
from core.constants import VERSION
from core.database import DatabaseManager
from metadata.health_score import MetadataScorer
from repair.backup import backup_database
from repair.file_organizer import FileOrganizer
from repair.organize_applier import OrganizeApplier
from reports.report_generator import write_health_report_csv, write_organize_plan_csv
from services.library_service import LibraryService

LINE = "=" * 60


def print_header():

    print(LINE)
    print("📚 BOOK LIBRARY RECONCILER")
    print(f"Version {VERSION}")
    print(LINE)
    print(f"Library  : {LIBRARY_ROOT}")
    print(f"Database : {METADATA_DB}")
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


def open_library():

    db = DatabaseManager(METADATA_DB)
    db.connect()

    return db, LibraryService(db)


def run_preview(args):

    db, library = open_library()

    total = library.get_book_count()

    print(f"Books in Library : {total:,}")

    print()
    print(LINE)
    print(f"FIRST {args.limit} BOOKS")
    print(LINE)

    books = library.get_books(limit=args.limit)

    for book in books:
        print_book(book)

    analyzer = LibraryAnalyzer(books)

    print(LINE)
    print("LIBRARY STATISTICS (loaded sample)")
    print(LINE)
    print(f"Unique Authors      : {analyzer.unique_authors()}")
    print(f"Unique Series       : {analyzer.unique_series()}")
    print(f"Missing ISBN        : {analyzer.books_missing_isbn()}")
    print(f"Missing Series      : {analyzer.books_missing_series()}")
    print(f"Missing Comments    : {analyzer.books_missing_comments()}")
    print(f"Missing Cover       : {analyzer.books_missing_cover()}")

    db.close()


def run_health(args):

    db, library = open_library()

    books = library.get_all_books()

    scorer = MetadataScorer()
    reports = scorer.score_library(books)

    print(f"Average Metadata Health Score : {scorer.average_score(books)}%")

    worst = sorted(reports, key=lambda r: r.score)[: args.limit]

    print(f"\n{args.limit} books most in need of attention:\n")

    for report in worst:
        failed = ", ".join(report.failed) if report.failed else "none"
        print(f"[{report.score:>3}%] #{report.book_id:<6} {report.title!r:<50} missing: {failed}")

    if args.csv:
        output_path = write_health_report_csv(reports, OUTPUT_FOLDER / "health_report.csv")
        print(f"\nFull report written to:\n{output_path}")

    db.close()


def run_organize(args):

    db, library = open_library()

    books = library.get_all_books()

    organizer = FileOrganizer()
    plans = organizer.plans_with_changes(books)

    print(f"Books scanned          : {len(books):,}")
    print(f"Proposed reorganizes   : {len(plans):,}")

    for plan in plans[: args.limit]:
        print(f"\n#{plan.book_id}  {plan.current_path}  ->  {plan.proposed_path}")
        for rename in plan.format_renames:
            if rename.changed:
                print(f"    {rename.old_name}.{rename.format.lower()} -> {rename.new_name}.{rename.format.lower()}")

    if len(plans) > args.limit:
        print(f"\n... and {len(plans) - args.limit:,} more (use --csv for the full list)")

    if args.csv:
        output_path = write_organize_plan_csv(plans, OUTPUT_FOLDER / "organize_plan.csv")
        print(f"\nFull plan written to:\n{output_path}")

    if not args.apply:
        db.close()
        print("\nDry run only - nothing was moved. Re-run with --apply to make changes.")
        return

    if not plans:
        db.close()
        print("\nNothing to apply.")
        return

    print(f"\nBacking up database: {METADATA_DB}")
    backup_path = backup_database(METADATA_DB)
    print(f"Backup written to  : {backup_path}")

    applier = OrganizeApplier(LIBRARY_ROOT, library)
    results = applier.apply(plans)

    moved = sum(1 for result in results if result.moved)
    failed = [result for result in results if result.error]

    print(f"\nMoved     : {moved:,}")
    print(f"Failed    : {len(failed):,}")

    for result in failed:
        print(f"  #{result.book_id}: {result.error}")

    db.close()


def build_parser():

    parser = argparse.ArgumentParser(description="Book Library Reconciler")

    subparsers = parser.add_subparsers(dest="command")

    preview_parser = subparsers.add_parser("preview", help="Show the first N books and library stats")
    preview_parser.add_argument("--limit", type=int, default=10)
    preview_parser.set_defaults(func=run_preview)

    health_parser = subparsers.add_parser("health", help="Score every book's metadata completeness")
    health_parser.add_argument("--limit", type=int, default=10)
    health_parser.add_argument("--csv", action="store_true", help="Write the full report to output/health_report.csv")
    health_parser.set_defaults(func=run_health)

    organize_parser = subparsers.add_parser(
        "organize", help="Preview (default) or apply an Author/Title reorganization"
    )
    organize_parser.add_argument("--limit", type=int, default=10, help="How many proposed changes to print")
    organize_parser.add_argument("--csv", action="store_true", help="Write the full plan to output/organize_plan.csv")
    organize_parser.add_argument(
        "--apply", action="store_true", help="Actually move files and update metadata.db (backs it up first)"
    )
    organize_parser.set_defaults(func=run_organize)

    return parser


def main():

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print_header()

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        args = parser.parse_args(["preview"])

    args.func(args)


if __name__ == "__main__":
    main()
