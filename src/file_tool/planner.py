"""
Planner Module
==============
Builds a safe move plan by combining scanning, classification, and normalization.
Generates a CSV file showing exactly where each file should go.
"""

from pathlib import Path
import csv
from datetime import datetime

from .scanner import scan_all_files, scan_files
from .classifier import get_destination_bucket
from .normalize import normalize_filename
from .config import ONEDRIVE_ROOT, LOG_DIR

EXCLUDED_PATH_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "site-packages",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
}

EXCLUDED_FILENAMES = {
    "desktop.ini",
    "thumbs.db",
    ".ds_store",
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
}


def _same_path(left: Path, right: Path) -> bool:
    """Compare paths case-insensitively for Windows-friendly planning."""
    return str(left).casefold() == str(right).casefold()


def _is_excluded_from_file_moves(file_path: Path) -> tuple[bool, str]:
    parts = {part.casefold() for part in file_path.parts}
    if parts & EXCLUDED_PATH_PARTS:
        return True, "SKIP_PROJECT_INTERNAL"

    if file_path.name.casefold() in EXCLUDED_FILENAMES or file_path.suffix.casefold() in EXCLUDED_EXTENSIONS:
        return True, "SKIP_GENERATED_FILE"

    return False, ""


def build_move_plan(root_path: Path, *, all_files: bool = False) -> list[dict]:
    """Build a detailed move plan for all files."""
    plan = []
    
    if all_files:
        accepted, skipped = scan_all_files(root_path)
    else:
        accepted, skipped = scan_files(root_path)
    
    print(f"Found {len(accepted)} files to plan...")

    for file_path in accepted:
        is_excluded, excluded_action = _is_excluded_from_file_moves(file_path)
        original_name = file_path.name
        normalized_name = normalize_filename(original_name)
        
        # Use the classifier to get the correct destination bucket
        destination_bucket = get_destination_bucket(file_path)
        
        destination_folder = ONEDRIVE_ROOT / destination_bucket
        proposed_path = destination_folder / normalized_name
        
        if is_excluded:
            action = excluded_action
        elif _same_path(file_path, proposed_path):
            action = "NO_CHANGE"        # Already in correct folder
        elif proposed_path.exists():
            action = "REVIEW_COLLISION" # Name collision
        else:
            action = "MOVE_RENAME"      # Should move to new bucket

        plan.append({
            "source_path": str(file_path),
            "original_name": original_name,
            "normalized_name": normalized_name,
            "destination_bucket": destination_bucket,
            "proposed_path": str(proposed_path),
            "action": action,
        })
    
    destination_counts: dict[str, int] = {}
    for row in plan:
        if row["action"] == "MOVE_RENAME":
            key = row["proposed_path"].casefold()
            destination_counts[key] = destination_counts.get(key, 0) + 1

    for row in plan:
        if row["action"] == "MOVE_RENAME":
            key = row["proposed_path"].casefold()
            if destination_counts[key] > 1:
                row["action"] = "REVIEW_PLAN_COLLISION"

    return plan

def write_move_plan(plan: list[dict]) -> Path:
    """Write the move plan to a timestamped CSV file."""
    if not plan:
        print("No files to plan.")
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = LOG_DIR / f"move_plan_{timestamp}.csv"

    fieldnames = ["source_path", "original_name", "normalized_name", 
                  "destination_bucket", "proposed_path", "action"]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(plan)

    print(f"Move plan saved to: {output_path}")
    return output_path
