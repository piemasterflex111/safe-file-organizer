"""
Remaining-work review reports.

These reports classify unresolved move-plan rows into explicit review buckets.
They do not move or delete files.
"""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from pathlib import Path

from .config import LOG_DIR


def _sha256(path: Path, max_bytes: int = 64 * 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    remaining = max_bytes

    with path.open("rb") as f:
        while remaining > 0:
            chunk = f.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            hasher.update(chunk)
            remaining -= len(chunk)

    return hasher.hexdigest()


def _file_info(path: Path, *, hash_small_files: bool = False) -> tuple[bool, str, str]:
    if not path.exists() or not path.is_file():
        return False, "", ""

    stat = path.stat()
    size = str(stat.st_size)
    digest = ""
    if hash_small_files and stat.st_size <= 64 * 1024 * 1024:
        try:
            digest = _sha256(path)
        except OSError:
            digest = ""

    return True, size, digest


def _classify_review_row(row: dict[str, str], *, hash_small_files: bool = False) -> dict[str, str]:
    source = Path(row["source_path"])
    destination = Path(row["proposed_path"])
    action = row["action"]

    source_exists, source_size, source_hash = _file_info(source, hash_small_files=hash_small_files)
    destination_exists, destination_size, destination_hash = _file_info(destination, hash_small_files=hash_small_files)

    review_action = "NO_REVIEW"
    recommendation = "No manual action needed"

    if action == "MOVE_RENAME":
        if not source_exists:
            review_action = "SKIP_SOURCE_MISSING"
            recommendation = "Already moved or removed"
        elif destination.exists():
            review_action = "REVIEW_DESTINATION_NOW_EXISTS"
            recommendation = "Destination appeared after plan creation"
        else:
            review_action = "APPLY_SAFE_MOVE"
            recommendation = "Safe to move with apply"
    elif action == "REVIEW_COLLISION":
        if source_exists and destination_exists and source_size == destination_size and source_hash and source_hash == destination_hash:
            review_action = "REVIEW_DUPLICATE_SAME_HASH"
            recommendation = "Likely duplicate; source can be archived or deleted after manual confirmation"
        elif source_exists and destination_exists and source_size == destination_size:
            review_action = "REVIEW_SAME_SIZE"
            recommendation = "Same size; hash later if needed before deleting"
        else:
            review_action = "REVIEW_NAME_COLLISION_DIFFERENT_CONTENT"
            recommendation = "Keep both or rename one; do not overwrite"
    elif action == "REVIEW_PLAN_COLLISION":
        review_action = "REVIEW_MANY_TO_ONE_DESTINATION"
        recommendation = "Multiple sources normalize to the same destination; group and choose keep/rename/delete"
    elif action == "NO_CHANGE":
        review_action = "NO_CHANGE"
        recommendation = "Already in planned location"
    elif action.startswith("SKIP_"):
        review_action = action
        recommendation = "Excluded from file moves by planner safety rules"

    return {
        **row,
        "review_action": review_action,
        "recommendation": recommendation,
        "source_exists": str(source_exists),
        "source_size": source_size,
        "source_hash": source_hash,
        "destination_exists": str(destination_exists),
        "destination_size": destination_size,
        "destination_hash": destination_hash,
    }


def build_remaining_work_rows(plan_csv_path: Path, *, hash_small_files: bool = False) -> list[dict[str, str]]:
    rows = []

    with plan_csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["action"] == "NO_CHANGE":
                continue
            rows.append(_classify_review_row(row, hash_small_files=hash_small_files))

    return rows


def write_remaining_work_csv(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"remaining_work_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def build_collision_group_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row["review_action"] != "REVIEW_MANY_TO_ONE_DESTINATION":
            continue
        groups.setdefault(row["proposed_path"], []).append(row)

    output = []
    for proposed_path, group_rows in groups.items():
        existing_sources = [
            row["source_path"] for row in group_rows
            if row["source_exists"] == "True"
        ]
        sizes = sorted({
            row["source_size"] for row in group_rows
            if row["source_size"]
        })
        output.append({
            "proposed_path": proposed_path,
            "source_count": str(len(group_rows)),
            "existing_source_count": str(len(existing_sources)),
            "distinct_size_count": str(len(sizes)),
            "sample_sources": " | ".join(existing_sources[:5]),
            "recommendation": "Review as a group; keep best source, rename meaningful variants, delete generated duplicates",
        })

    output.sort(key=lambda row: int(row["source_count"]), reverse=True)
    return output


def write_collision_groups_csv(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    group_rows = build_collision_group_rows(rows)
    if not group_rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"collision_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(group_rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(group_rows)

    return output_path
