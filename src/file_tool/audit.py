"""
Full OneDrive path audit.

This module inventories every file and directory under a root path. It does not
move, rename, or delete anything.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .classifier import get_destination_bucket
from .config import LOG_DIR, ONEDRIVE_ROOT
from .normalize import normalize_filename


def _relative_path(item: Path, root: Path) -> Path:
    try:
        return item.relative_to(root)
    except ValueError:
        return item


def _top_level_folder(relative_path: Path) -> str:
    if len(relative_path.parts) <= 1:
        return ""
    return relative_path.parts[0]


def _modified_time(item: Path) -> str:
    return datetime.fromtimestamp(item.stat().st_mtime).isoformat(
        sep=" ",
        timespec="seconds",
    )


def _is_empty_dir(item: Path) -> bool:
    if not item.is_dir():
        return False
    try:
        next(item.iterdir())
    except StopIteration:
        return True
    return False


def build_audit_row(item: Path, root: Path, destination_root: Path) -> dict[str, str]:
    relative_path = _relative_path(item, root)
    item_type = "directory" if item.is_dir() else "file"
    normalized_name = normalize_filename(item.name) if item.is_file() else item.name
    normalized_path = item.with_name(normalized_name)
    rename_needed = item.is_file() and item.name != normalized_name
    rename_collision = rename_needed and normalized_path.exists()
    is_empty_dir = _is_empty_dir(item)

    destination_bucket = ""
    planned_destination_path = ""
    action = "NO_ACTION"

    if item.is_file():
        destination_bucket = get_destination_bucket(item)
        planned_destination_path = str(destination_root / destination_bucket / normalized_name)
        if rename_collision:
            action = "REVIEW_RENAME_COLLISION"
        elif rename_needed:
            action = "RENAME_PREVIEW"
        else:
            action = "FILE_AUDIT_ONLY"
    elif is_empty_dir:
        action = "REVIEW_EMPTY_DIR"
    else:
        action = "DIR_AUDIT_ONLY"

    size_bytes = ""
    if item.is_file():
        size_bytes = str(item.stat().st_size)

    return {
        "item_type": item_type,
        "source_path": str(item),
        "relative_path": str(relative_path),
        "parent_folder": str(item.parent),
        "top_level_folder": _top_level_folder(relative_path),
        "name": item.name,
        "extension": item.suffix.lower() if item.is_file() else "",
        "size_bytes": size_bytes,
        "modified_time": _modified_time(item),
        "depth": str(len(relative_path.parts)),
        "is_empty_dir": str(is_empty_dir),
        "normalized_name": normalized_name,
        "rename_needed": str(rename_needed),
        "rename_collision": str(rename_collision),
        "destination_bucket": destination_bucket,
        "planned_destination_path": planned_destination_path,
        "action": action,
    }


def build_audit_rows(root: Path, destination_root: Path = ONEDRIVE_ROOT) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for item in root.rglob("*"):
        try:
            rows.append(build_audit_row(item, root, destination_root))
        except OSError as exc:
            rows.append({
                "item_type": "unknown",
                "source_path": str(item),
                "relative_path": str(_relative_path(item, root)),
                "parent_folder": str(item.parent),
                "top_level_folder": "",
                "name": item.name,
                "extension": "",
                "size_bytes": "",
                "modified_time": "",
                "depth": "",
                "is_empty_dir": "",
                "normalized_name": "",
                "rename_needed": "",
                "rename_collision": "",
                "destination_bucket": "",
                "planned_destination_path": "",
                "action": "AUDIT_ERROR",
                "error": str(exc),
            })

    return rows


def write_audit_csv(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"path_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path
