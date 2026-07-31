"""
Book Library Reconciler
"""

import argparse
import sys

from analyzers.library_analyzer import LibraryAnalyzer
from app.application import Application
from config.constants import LINE, VERSION
from config.paths import OUTPUT_FOLDER
from controllers.search_controller import SearchController
from metadata.author_duplicate_finder import AuthorDuplicateFinder
from metadata.library_inspector import LibraryInspector
from metadata.metadata_repair import MetadataRepair
from metadata.metadata_score import MetadataScorer
from repair.author_merger import AuthorMerger
from repair.backup import backup_database
from repair.file_organizer import FileOrganizer
from repair.metadata_repair_applier import MetadataRepairApplier
from repair.organize_applier import OrganizeApplier
from reports.csv_report import CsvReport
from services.search_service import SORT_KEYS


def print_header(app):

    print(LINE)
    print("📚 BOOK LIBRARY RECONCILER")
    print(f"Version {VERSION}")
    print(LINE)
    print(f"Library  : {app.library_root}")
    print(f"Database : {app.database_path}")
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


def run_preview(args, app):

    library = app.library_service

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


def run_health(args, app):

    books = app.library_service.get_all_books()

    scorer = MetadataScorer()
    reports = scorer.score_library(books)

    print(f"Average Metadata Health Score : {scorer.average_score(books)}%")

    worst = sorted(reports, key=lambda r: r.score)[: args.limit]

    print(f"\n{args.limit} books most in need of attention:\n")

    for report in worst:
        failed = ", ".join(report.failed) if report.failed else "none"
        print(f"[{report.score:>3}%] #{report.book_id:<6} {report.title!r:<50} missing: {failed}")

    if args.csv:
        report_writer = CsvReport()
        output_path = report_writer.write_health_report(
            reports, OUTPUT_FOLDER / "health_report.csv"
        )
        print(f"\nFull report written to:\n{output_path}")


def run_analyze(args, app):

    books = app.library_service.get_all_books()

    inspection = LibraryInspector().inspect(books)
    needing_attention = inspection.books_needing_attention

    print(f"Average Metadata Health Score : {inspection.average_score}%")
    print(f"Books needing attention       : {len(needing_attention):,} / {len(books):,}")
    print(f"ISBN duplicate groups         : {len(inspection.isbn_duplicate_groups):,}")
    print(f"Title duplicate groups        : {len(inspection.title_duplicate_groups):,}")
    print(f"Series order issues           : {len(inspection.series_order_issues):,}")

    if inspection.isbn_duplicate_groups:
        print("\nISBN duplicates:\n")
        for group in inspection.isbn_duplicate_groups[: args.limit]:
            print(f"  {group.reason}: books {group.book_ids}")

    if inspection.title_duplicate_groups:
        print("\nTitle duplicates:\n")
        for group in inspection.title_duplicate_groups[: args.limit]:
            print(f"  {group.reason}: books {group.book_ids}")

    if inspection.series_order_issues:
        print("\nSeries order issues:\n")
        for issue in inspection.series_order_issues[: args.limit]:
            print(f"  {issue.series_name!r} {issue.issue_type}: {issue.detail}")

    worst = sorted(needing_attention, key=lambda a: a.score)[: args.limit]

    print(f"\n{args.limit} books most in need of attention:\n")

    for analysis in worst:
        issues = "; ".join(analysis.issues) if analysis.issues else "none"
        print(f"[{analysis.score:>3}%] #{analysis.book_id:<6} {analysis.title!r:<45} {issues}")

    if args.csv:
        report_writer = CsvReport()
        output_path = report_writer.write_library_analysis(
            inspection.book_analyses, OUTPUT_FOLDER / "library_analysis.csv"
        )
        print(f"\nFull per-book analysis written to:\n{output_path}")


def run_search(args, app):

    controller = SearchController(app.search_service)

    try:
        results = controller.search(
            args.where, sort_by=args.sort, descending=args.desc, limit=None
        )
    except ValueError as error:
        print(f"Error: {error}")
        return

    print(f"Matches: {len(results):,}\n")

    scorer = MetadataScorer()

    for book in results[: args.limit]:

        score = scorer.score_book(book).score
        cover = "yes" if book.has_cover else "no"

        print(
            f"#{book.id:<6} {book.title!r:<45} {book.author_names:<25} "
            f"series={book.series_name or '-':<20} rating={book.rating} "
            f"score={score:>3}% isbn={book.isbn or '-':<15} cover={cover:<3} "
            f"formats={','.join(book.formats) or '-'}"
        )

    if len(results) > args.limit:
        print(f"\n... and {len(results) - args.limit:,} more (use --csv for the full list)")

    if args.csv:
        report_writer = CsvReport()
        output_path = report_writer.write_search_results(
            results, OUTPUT_FOLDER / "search_results.csv", scorer=scorer
        )
        print(f"\nFull results written to:\n{output_path}")


def run_repair(args, app):

    books = app.library_service.get_all_books()

    suggestions = MetadataRepair().suggest_for_library(books)
    applicable = [s for s in suggestions if s.suggested_value]
    needs_review = [s for s in suggestions if not s.suggested_value]

    author_records = app.library_service.get_all_author_records()
    author_groups = AuthorDuplicateFinder().find_duplicates(author_records)

    print(
        f"Title repair suggestions      : {len(suggestions):,} "
        f"({len(applicable):,} auto-applicable, {len(needs_review):,} need manual review)"
    )
    print(f"Duplicate author groups       : {len(author_groups):,}")

    if applicable:
        print("\nAuto-applicable title repairs:\n")
        for suggestion in applicable[: args.limit]:
            print(f"  #{suggestion.book_id}: {suggestion.current_value!r} -> {suggestion.suggested_value!r}")

    if needs_review:
        print("\nNeeds manual review (no automatic suggestion possible):\n")
        for suggestion in needs_review[: args.limit]:
            print(f"  #{suggestion.book_id}: {suggestion.current_value!r} - {suggestion.reason}")

    if author_groups:
        print("\nDuplicate author groups:\n")
        for group in author_groups[: args.limit]:
            print(f"  {group.names} -> merge into author #{group.canonical_author_id}")

    if args.csv:
        report_writer = CsvReport()
        output_path = report_writer.write_repair_suggestions(
            suggestions, OUTPUT_FOLDER / "repair_suggestions.csv"
        )
        print(f"\nFull suggestions written to:\n{output_path}")

    if not args.apply:
        print("\nDry run only - nothing was changed. Re-run with --apply to make changes.")
        return

    if not applicable and not author_groups:
        print("\nNothing to apply.")
        return

    print(f"\nBacking up database: {app.database_path}")
    backup_path = backup_database(app.database_path)
    print(f"Backup written to  : {backup_path}")

    title_results = MetadataRepairApplier(app.library_service).apply(applicable)
    author_results = AuthorMerger(app.library_service).apply(author_groups)

    title_applied = sum(1 for result in title_results if result.applied)
    title_failed = [result for result in title_results if result.error]

    author_merged = sum(1 for result in author_results if result.merged)
    author_failed = [result for result in author_results if result.error]

    print(f"\nTitles repaired      : {title_applied:,}")
    print(f"Title failures       : {len(title_failed):,}")
    for result in title_failed:
        print(f"  #{result.book_id}: {result.error}")

    print(f"\nAuthor groups merged : {author_merged:,}")
    print(f"Author merge failures: {len(author_failed):,}")
    for result in author_failed:
        print(f"  canonical #{result.canonical_author_id}: {result.error}")


def run_organize(args, app):

    books = app.library_service.get_all_books()

    organizer = FileOrganizer()
    plans = organizer.plans_with_changes(books)

    print(f"Books scanned          : {len(books):,}")
    print(f"Proposed reorganizes   : {len(plans):,}")

    for plan in plans[: args.limit]:
        print(f"\n#{plan.book_id}  {plan.current_path}  ->  {plan.proposed_path}")
        for rename in plan.format_renames:
            if rename.changed:
                print(
                    f"    {rename.old_name}.{rename.format.lower()} -> {rename.new_name}.{rename.format.lower()}"
                )

    if len(plans) > args.limit:
        print(f"\n... and {len(plans) - args.limit:,} more (use --csv for the full list)")

    if args.csv:
        report_writer = CsvReport()
        output_path = report_writer.write_organize_plan(plans, OUTPUT_FOLDER / "organize_plan.csv")
        print(f"\nFull plan written to:\n{output_path}")

    if not args.apply:
        print("\nDry run only - nothing was moved. Re-run with --apply to make changes.")
        return

    if not plans:
        print("\nNothing to apply.")
        return

    print(f"\nBacking up database: {app.database_path}")
    backup_path = backup_database(app.database_path)
    print(f"Backup written to  : {backup_path}")

    applier = OrganizeApplier(app.library_root, app.library_service)
    results = applier.apply(plans)

    moved = sum(1 for result in results if result.moved)
    failed = [result for result in results if result.error]

    print(f"\nMoved     : {moved:,}")
    print(f"Failed    : {len(failed):,}")

    for result in failed:
        print(f"  #{result.book_id}: {result.error}")


def build_parser():

    parser = argparse.ArgumentParser(description="Book Library Reconciler")

    subparsers = parser.add_subparsers(dest="command")

    preview_parser = subparsers.add_parser(
        "preview", help="Show the first N books and library stats"
    )
    preview_parser.add_argument("--limit", type=int, default=10)
    preview_parser.set_defaults(func=run_preview)

    health_parser = subparsers.add_parser("health", help="Score every book's metadata completeness")
    health_parser.add_argument("--limit", type=int, default=10)
    health_parser.add_argument(
        "--csv", action="store_true", help="Write the full report to output/health_report.csv"
    )
    health_parser.set_defaults(func=run_health)

    organize_parser = subparsers.add_parser(
        "organize", help="Preview (default) or apply an Author/Title reorganization"
    )
    organize_parser.add_argument(
        "--limit", type=int, default=10, help="How many proposed changes to print"
    )
    organize_parser.add_argument(
        "--csv", action="store_true", help="Write the full plan to output/organize_plan.csv"
    )
    organize_parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move files and update metadata.db (backs it up first)",
    )
    organize_parser.set_defaults(func=run_organize)

    repair_parser = subparsers.add_parser(
        "repair", help="Preview (default) or apply metadata repairs: title fixes + author merges"
    )
    repair_parser.add_argument(
        "--limit", type=int, default=10, help="How many findings to print per section"
    )
    repair_parser.add_argument(
        "--csv", action="store_true", help="Write the full suggestions to output/repair_suggestions.csv"
    )
    repair_parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rewrite titles and merge duplicate authors in metadata.db (backs it up first)",
    )
    repair_parser.set_defaults(func=run_repair)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Full library inspection: health score, validation issues, duplicates, series order",
    )
    analyze_parser.add_argument("--limit", type=int, default=10, help="How many findings to print per section")
    analyze_parser.add_argument(
        "--csv", action="store_true", help="Write the full per-book analysis to output/library_analysis.csv"
    )
    analyze_parser.set_defaults(func=run_analyze)

    search_parser = subparsers.add_parser(
        "search", help="Search the library by any field, with AND-combined filters"
    )
    search_parser.add_argument(
        "where",
        nargs="*",
        help=(
            "Filter terms, e.g. author=King series:exact='Dark Tower' "
            "isbn:missing rating>=4 missing-cover"
        ),
    )
    search_parser.add_argument("--sort", choices=sorted(SORT_KEYS.keys()), default=None)
    search_parser.add_argument("--desc", action="store_true", help="Sort descending")
    search_parser.add_argument("--limit", type=int, default=20, help="How many matches to print")
    search_parser.add_argument(
        "--csv", action="store_true", help="Write the full results to output/search_results.csv"
    )
    search_parser.set_defaults(func=run_search)

    return parser


def main():

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        args = parser.parse_args(["preview"])

    with Application() as app:
        print_header(app)
        args.func(args, app)


if __name__ == "__main__":
    main()
