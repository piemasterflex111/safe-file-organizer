"""
Directory-level organization planning.

This planner treats top-level folders as units instead of flattening all files.
It is intended for organizing the visible OneDrive root.
"""

from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path

from .classifier import get_directory_destination_bucket
from .config import LOG_DIR, ONEDRIVE_ROOT, TARGET_BUCKETS
from .normalize import normalize_filename


PROTECTED_TOP_LEVEL_DIRS = {
    value.split("/")[0].casefold()
    for value in TARGET_BUCKETS.values()
}
PROTECTED_TOP_LEVEL_DIRS.update({
    "desktop",
    "documents",
    "apps",
    "personal vault",
})


def _same_path(left: Path, right: Path) -> bool:
    return str(left).casefold() == str(right).casefold()


def _count_children(folder: Path) -> tuple[int, int]:
    file_count = 0
    dir_count = 0

    for item in folder.rglob("*"):
        if item.is_file():
            file_count += 1
        elif item.is_dir():
            dir_count += 1

    return file_count, dir_count


def _normalize_folder_name(name: str) -> str:
    return normalize_filename(name).rstrip(".")


def build_directory_plan(root_path: Path, destination_root: Path = ONEDRIVE_ROOT) -> list[dict[str, str]]:
    rows = []

    for folder in sorted((item for item in root_path.iterdir() if item.is_dir()), key=lambda item: item.name.casefold()):
        file_count, dir_count = _count_children(folder)
        normalized_name = _normalize_folder_name(folder.name)
        destination_bucket = get_directory_destination_bucket(folder)
        destination_parent = destination_root / destination_bucket
        proposed_path = destination_parent / normalized_name

        if folder.name.casefold() in PROTECTED_TOP_LEVEL_DIRS:
            action = "KEEP_STRUCTURAL_FOLDER"
        elif _same_path(folder, proposed_path):
            action = "NO_CHANGE"
        elif file_count == 0 and dir_count == 0:
            action = "REVIEW_EMPTY_TOP_LEVEL_DIR"
        elif proposed_path.exists():
            action = "REVIEW_MERGE_FOLDER"
        else:
            action = "MOVE_FOLDER"

        rows.append({
            "source_path": str(folder),
            "folder_name": folder.name,
            "normalized_folder_name": normalized_name,
            "file_count": str(file_count),
            "dir_count": str(dir_count),
            "destination_bucket": destination_bucket,
            "proposed_path": str(proposed_path),
            "action": action,
        })

    proposed_counts: dict[str, int] = {}
    for row in rows:
        if row["action"] == "MOVE_FOLDER":
            key = row["proposed_path"].casefold()
            proposed_counts[key] = proposed_counts.get(key, 0) + 1

    for row in rows:
        if row["action"] == "MOVE_FOLDER" and proposed_counts[row["proposed_path"].casefold()] > 1:
            row["action"] = "REVIEW_PLAN_FOLDER_COLLISION"

    return rows


def write_directory_plan(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"directory_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def apply_directory_plan(plan_csv_path: Path, dry_run: bool = True) -> tuple[Path | None, Path | None, dict[str, int]]:
    if not plan_csv_path.exists():
        raise FileNotFoundError(f"Directory plan not found: {plan_csv_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = LOG_DIR / f"apply_directory_report_{timestamp}.csv"
    undo_path = LOG_DIR / f"undo_directory_moves_{timestamp}.ps1"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    report_rows = []
    undo_commands = []
    summary = {
        "moved": 0,
        "dry_run": 0,
        "skipped": 0,
        "missing": 0,
        "destination_exists": 0,
        "failed": 0,
    }

    with plan_csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = Path(row["source_path"])
            destination = Path(row["proposed_path"])
            action = row["action"]

            if action != "MOVE_FOLDER":
                summary["skipped"] += 1
                report_rows.append({
                    **row,
                    "status": "SKIPPED",
                    "reason": f"Action is {action}",
                })
                continue

            if not source.exists():
                summary["missing"] += 1
                report_rows.append({
                    **row,
                    "status": "SKIPPED",
                    "reason": "Source folder missing",
                })
                continue

            if destination.exists():
                summary["destination_exists"] += 1
                report_rows.append({
                    **row,
                    "status": "SKIPPED",
                    "reason": "Destination already exists",
                })
                continue

            if dry_run:
                summary["dry_run"] += 1
                report_rows.append({
                    **row,
                    "status": "DRY_RUN",
                    "reason": "Preview only",
                })
                continue

            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                undo_commands.append(f'Move-Item -LiteralPath "{destination}" -Destination "{source}"')
                summary["moved"] += 1
                report_rows.append({
                    **row,
                    "status": "MOVED",
                    "reason": "",
                })
            except OSError as exc:
                summary["failed"] += 1
                report_rows.append({
                    **row,
                    "status": "FAILED",
                    "reason": str(exc),
                })

    fieldnames = list(report_rows[0].keys()) if report_rows else []
    if fieldnames:
        with report_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(report_rows)

    if not dry_run and undo_commands:
        with undo_path.open("w", encoding="utf-8") as f:
            f.write("# Undo whole-directory moves\n")
            for command in undo_commands:
                f.write(command + "\n")
    else:
        undo_path = None

    return report_path if fieldnames else None, undo_path, summary
