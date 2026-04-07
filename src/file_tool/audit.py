from pathlib import Path
import csv 
from datetime import datetime

from .normalize import normalize_filename
from .classifier import classify_name
from .categories import DESTINATIONS

def build_audit_row(item: Path, onedrive_root: Path) -> dict[str, str]:
    original_name = item.name
    relative_path = get_relative_path(item, onedrive_root)
    top_level_folder = get_top_level_folder(relative_path)
    normalized_name = normalize_filename(original_name)
    rename_needed = original_name != normalized_name
    normalized_path = item.with_name(normalized_name)
    rename_collision = rename_needed and normalized_path.exists()
    category_key = classify_name(original_name)
    destination_bucket = DESTINATIONS[category_key]
    planned_destination_path = onedrive_root / destination_bucket / normalized_name
    stat = item.stat()
    size_bytes = stat.st_size
    modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat(sep=" ", timespec="seconds")
    parent_folder = str(item.parent)
    extension = item.suffix.lower()
    if rename_collision:
        action = "REVIEW_COLLISION"
    elif rename_needed:
        action = "RENAME_PREVIEW"
    else:
        action = "NO_RENAME_NEEDED"
    return {
        "source_path": str(item),
        "parent_folder": parent_folder,
        "filename": original_name,
        "extension": extension,
        "size_bytes": str(size_bytes),
        "modified_time": modified_time,
        "normalized_filename": normalized_name,
        "rename_needed": str(rename_needed),
        "rename_collision": str(rename_collision),
        "category": category_key,
        "destination_bucket": destination_bucket,
        "planned_destination_path": str(planned_destination_path),
        "action": action,
        "relative_path": str(relative_path),
        "top_level_folder": top_level_folder if top_level_folder is not None else "",
        }

def build_audit_rows(root: Path, onedrive_root: Path):
    rows = []
    for item in root.iterdir():
        if item.is_file():
            row = build_audit_row(item, onedrive_root)
            rows.append(row)
        elif item.is_dir():
            child_rows = build_audit_rows(item, onedrive_root)
            rows.extend(child_rows)
    return rows

def get_relative_path(item: Path, onedrive_root: Path):
    return item.relative_to(onedrive_root)


def get_top_level_folder(relative_path: Path):
    parts = relative_path.parts
    if len(parts) <= 1:
        return None
    return parts[0]

def write_audit_csv(rows: list[dict], out_path: Path) -> None:
    if not rows:
        return
    fieldname = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    test_file = Path(r"C:\Users\payam_vngz\OneDrive")
    onedrive_root = Path(r"C:\Users\payam_vngz\OneDrive")
    rows = build_audit_rows(test_file, onedrive_root)
    write_audit_csv(rows, Path("audit_csv.csv"))
    print("Wrote audit_csv.csv")  




 

