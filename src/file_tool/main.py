"""
OneDrive Organizer Tool - Main CLI Entry Point
==============================================

Safe tool to scan, plan, and organize files from a messy OneDrive.

Commands:
  --scan          : Show summary of files found
  --plan          : Generate move plan CSV (safe preview)
  --apply         : Apply the latest move plan (with confirmation)
"""

from pathlib import Path
import argparse
import sys

from .config import ONEDRIVE_ROOT, SAMPLE_INPUT_DIR, LOG_DIR
from .audit import build_audit_rows, write_audit_csv
from .cleanup import (
    build_cleanup_rows,
    quarantine_dependency_folders,
    quarantine_generated_cache,
    remove_empty_dirs,
    write_cleanup_csv,
)
from .directory_planner import apply_directory_plan, build_directory_plan, write_directory_plan
from .scanner import scan_all_files, scan_files
from .planner import build_move_plan, write_move_plan
from .mover import apply_move_plan
from .review import build_remaining_work_rows, write_collision_groups_csv, write_remaining_work_csv
from .year_planner import (
    apply_year_archive_plan,
    apply_year_finish_plan,
    apply_year_topic_plan,
    build_year_plan,
    write_year_plan,
)


def _count_actions(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        action = row.get("action", "UNKNOWN")
        counts[action] = counts.get(action, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def _count_review_actions(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        action = row.get("review_action", "UNKNOWN")
        counts[action] = counts.get(action, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OneDrive Organizer - Safely clean and organize your files."
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default=str(SAMPLE_INPUT_DIR),
        help="Folder to scan"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan files and show summary only"
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include every file extension instead of only configured extensions"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Write a CSV audit of every file and directory under the input"
    )
    parser.add_argument(
        "--cleanup-audit",
        action="store_true",
        help="Write a report-only cleanup audit for cache, dependency, Git, and project paths"
    )
    parser.add_argument(
        "--delete-generated-cache",
        action="store_true",
        help="Move generated-cache cleanup candidates to a quarantine folder"
    )
    parser.add_argument(
        "--delete-empty-dirs",
        action="store_true",
        help="Remove empty directory candidates and write a recreate undo script"
    )
    parser.add_argument(
        "--quarantine-dependencies",
        action="store_true",
        help="Move dependency folders like .venv, venv, site-packages, node_modules to quarantine"
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Generate detailed move plan CSV (safe preview)"
    )
    parser.add_argument(
        "--directory-plan",
        action="store_true",
        help="Generate a whole-folder plan for organizing top-level directories"
    )
    parser.add_argument(
        "--apply-directory-plan",
        action="store_true",
        help="Apply the latest whole-folder directory plan after confirmation"
    )
    parser.add_argument(
        "--remaining-work",
        action="store_true",
        help="Classify unresolved move-plan rows into explicit review buckets"
    )
    parser.add_argument(
        "--year-plan",
        action="store_true",
        help="Generate a professional bucket/year/topic organization plan"
    )
    parser.add_argument(
        "--apply-year-archive",
        action="store_true",
        help="Apply only low-value generated/raw data rows from the latest year plan"
    )
    parser.add_argument(
        "--apply-year-topic",
        action="store_true",
        help="Apply safe bucket/year/topic moves from the latest year plan"
    )
    parser.add_argument(
        "--apply-year-finish",
        action="store_true",
        help="Move year-plan review rows into dated folders and rename same-name collisions"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the latest move plan (with safety confirmation)"
    )

    args = parser.parse_args()

    target_folder = Path(args.input)

    if not target_folder.exists():
        print(f"[ERROR] Folder does not exist: {target_folder}")
        sys.exit(1)
    if not target_folder.is_dir():
        print(f"[ERROR] Path is not a directory: {target_folder}")
        sys.exit(1)

    print(f"Target folder: {target_folder}")

    try:
        if args.audit:
            print("Building full path audit...")
            rows = build_audit_rows(target_folder, destination_root=ONEDRIVE_ROOT)
            output_file = write_audit_csv(rows)

            file_count = sum(1 for row in rows if row["item_type"] == "file")
            dir_count = sum(1 for row in rows if row["item_type"] == "directory")
            empty_dir_count = sum(1 for row in rows if row["action"] == "REVIEW_EMPTY_DIR")

            print("\n[OK] Path audit generated!")
            print(f"Saved to: {output_file}")
            print(f"Files: {file_count}")
            print(f"Directories: {dir_count}")
            print(f"Empty directories to review: {empty_dir_count}")

        elif args.cleanup_audit:
            print("Building cleanup audit...")
            rows = build_cleanup_rows(target_folder)
            output_file = write_cleanup_csv(rows)

            print("\n[OK] Cleanup audit generated!")
            print(f"Saved to: {output_file}")
            for action, count in _count_actions(rows).items():
                print(f"{action}: {count}")

        elif args.delete_generated_cache:
            print("Building cleanup audit for generated-cache deletion...")
            rows = build_cleanup_rows(target_folder)
            delete_count = sum(1 for row in rows if row["action"] == "DELETE_GENERATED_CACHE")

            print(f"Generated-cache candidates: {delete_count}")
            print("Candidates will be moved to a quarantine folder, not permanently deleted.")
            response = input("Type 'YES' to quarantine generated-cache candidates: ")
            if response.strip().upper() != "YES":
                print("Generated-cache cleanup cancelled.")
                return

            quarantine_root, report_path, summary = quarantine_generated_cache(target_folder, rows)

            print("\n[OK] Generated-cache cleanup completed.")
            print(f"Quarantine folder: {quarantine_root}")
            print(f"Delete report: {report_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.delete_empty_dirs:
            print("Building cleanup audit for empty-directory deletion...")
            rows = build_cleanup_rows(target_folder)
            empty_dir_count = sum(1 for row in rows if row["action"] == "REVIEW_EMPTY_DIR")

            print(f"Empty-directory candidates: {empty_dir_count}")
            print("Only directories that are still empty at deletion time will be removed.")
            response = input("Type 'YES' to remove empty directories: ")
            if response.strip().upper() != "YES":
                print("Empty-directory cleanup cancelled.")
                return

            report_path, undo_path, summary = remove_empty_dirs(target_folder, rows)

            print("\n[OK] Empty-directory cleanup completed.")
            print(f"Delete report: {report_path}")
            print(f"Undo script: {undo_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.quarantine_dependencies:
            print("Building cleanup audit for dependency quarantine...")
            rows = build_cleanup_rows(target_folder)
            dependency_roots = {
                row["matched_root"]
                for row in rows
                if row["action"] == "REVIEW_DEPENDENCY_FOLDER" and row.get("matched_root")
            }

            print(f"Dependency roots to review/quarantine: {len(dependency_roots)}")
            print("Folders are moved to quarantine, not permanently deleted.")
            response = input("Type 'YES' to quarantine dependency folders: ")
            if response.strip().upper() != "YES":
                print("Dependency quarantine cancelled.")
                return

            quarantine_root, report_path, summary = quarantine_dependency_folders(target_folder, rows)

            print("\n[OK] Dependency quarantine completed.")
            print(f"Quarantine folder: {quarantine_root}")
            print(f"Report: {report_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.scan:
            if args.all_files:
                accepted, skipped = scan_all_files(target_folder)
            else:
                accepted, skipped = scan_files(target_folder)
            print("\n[OK] Scan completed!")
            print(f"   Accepted files : {len(accepted)}")
            print(f"   Skipped files  : {len(skipped)}")

        elif args.plan:
            print("Building move plan...")
            plan = build_move_plan(target_folder, all_files=args.all_files)
            output_file = write_move_plan(plan)
            
            if output_file:
                print("\n[OK] Move plan generated!")
                print(f"Saved to: {output_file}")
                print("Review the CSV, then run --apply when ready.")

        elif args.directory_plan:
            print("Building top-level directory organization plan...")
            rows = build_directory_plan(target_folder, destination_root=ONEDRIVE_ROOT)
            output_file = write_directory_plan(rows)

            print("\n[OK] Directory plan generated!")
            print(f"Saved to: {output_file}")
            for action, count in _count_actions(rows).items():
                print(f"{action}: {count}")

        elif args.apply_directory_plan:
            plan_files = list(LOG_DIR.glob("directory_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No directory plan found. Run --directory-plan first.")
                sys.exit(1)

            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest directory plan: {latest_plan}")
            response = input("This will move whole folders. Type 'YES' to continue: ")
            if response.strip().upper() != "YES":
                print("Directory apply cancelled.")
                return

            report_path, undo_path, summary = apply_directory_plan(latest_plan, dry_run=False)

            print("\n[OK] Directory plan apply completed.")
            print(f"Apply report: {report_path}")
            if undo_path:
                print(f"Undo script: {undo_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.remaining_work:
            plan_files = list(LOG_DIR.glob("move_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No move plan found. Run --plan first.")
                sys.exit(1)

            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest move plan: {latest_plan}")
            rows = build_remaining_work_rows(latest_plan)
            output_file = write_remaining_work_csv(rows)
            group_file = write_collision_groups_csv(rows)

            print("\n[OK] Remaining-work report generated!")
            print(f"Saved to: {output_file}")
            if group_file:
                print(f"Collision groups: {group_file}")
            for action, count in _count_review_actions(rows).items():
                print(f"{action}: {count}")

        elif args.year_plan:
            print("Building bucket/year/topic organization plan...")
            rows = build_year_plan(target_folder)
            output_file = write_year_plan(rows)

            print("\n[OK] Year organization plan generated!")
            print(f"Saved to: {output_file}")
            for action, count in _count_actions(rows).items():
                print(f"{action}: {count}")

        elif args.apply_year_archive:
            plan_files = list(LOG_DIR.glob("year_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No year plan found. Run --year-plan first.")
                sys.exit(1)

            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest year plan: {latest_plan}")
            response = input("This will move low-value data into year archive folders. Type 'YES' to continue: ")
            if response.strip().upper() != "YES":
                print("Year archive apply cancelled.")
                return

            report_path, undo_path, summary = apply_year_archive_plan(latest_plan, dry_run=False)

            print("\n[OK] Year archive apply completed.")
            print(f"Apply report: {report_path}")
            if undo_path:
                print(f"Undo script: {undo_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.apply_year_topic:
            plan_files = list(LOG_DIR.glob("year_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No year plan found. Run --year-plan first.")
                sys.exit(1)

            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest year plan: {latest_plan}")
            response = input("This will move safe files into bucket/year/topic folders. Type 'YES' to continue: ")
            if response.strip().upper() != "YES":
                print("Year topic apply cancelled.")
                return

            report_path, undo_path, summary = apply_year_topic_plan(latest_plan, dry_run=False)

            print("\n[OK] Year topic apply completed.")
            print(f"Apply report: {report_path}")
            if undo_path:
                print(f"Undo script: {undo_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.apply_year_finish:
            plan_files = list(LOG_DIR.glob("year_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No year plan found. Run --year-plan first.")
                sys.exit(1)

            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest year plan: {latest_plan}")
            print("Collisions will be moved with deterministic renamed filenames.")
            response = input("This will finish organizing review/collision rows. Type 'YES' to continue: ")
            if response.strip().upper() != "YES":
                print("Year finish apply cancelled.")
                return

            report_path, undo_path, summary = apply_year_finish_plan(latest_plan, dry_run=False)

            print("\n[OK] Year finish apply completed.")
            print(f"Apply report: {report_path}")
            if undo_path:
                print(f"Undo script: {undo_path}")
            for key, value in summary.items():
                if value:
                    print(f"{key}: {value}")

        elif args.apply:
            # Find latest move plan
            plan_files = list(LOG_DIR.glob("move_plan_*.csv"))
            if not plan_files:
                print("[ERROR] No move plan found. Run --plan first.")
                sys.exit(1)
            
            latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest plan: {latest_plan}")
            
            # For safety, always start with dry-run confirmation
            response = input("This will move files. Type 'YES' to continue: ")
            if response.strip().upper() == "YES":
                apply_move_plan(latest_plan, dry_run=False)
            else:
                print("Apply cancelled.")

        else:
            parser.print_help()

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
