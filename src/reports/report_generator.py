"""
Report Generator

Writes CSV reports for the organize plan and library health checks.
"""

import csv
from pathlib import Path


def write_organize_plan_csv(plans, output_path):

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(
            ["book_id", "title", "author", "current_path", "proposed_path", "format_renames"]
        )

        for plan in plans:

            renames = "; ".join(
                f"{rename.old_name} -> {rename.new_name}"
                for rename in plan.format_renames
                if rename.changed
            )

            writer.writerow(
                [
                    plan.book_id,
                    plan.title,
                    plan.author,
                    plan.current_path,
                    plan.proposed_path,
                    renames,
                ]
            )

    return output_path


def write_health_report_csv(reports, output_path):

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(["book_id", "title", "score", "failed_checks"])

        for report in reports:

            writer.writerow(
                [
                    report.book_id,
                    report.title,
                    report.score,
                    ", ".join(report.failed),
                ]
            )

    return output_path
