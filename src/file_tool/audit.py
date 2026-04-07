from pathlib import Path
import csv 
from datetime import datetime

from .normalize import normalize_filename
from .classifier import classify_name
from .categories import DESTINATIONS

def build_audit_row(item: Path, onedrive_root: Path) -> dict[str, str]:
    original_name = item.name
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
        }



if __name__ == "__main__":
    test_file = Path(r"C:\Users\payam_vngz\OneDrive\audit_test_4-7-26\file.pdf")
    onedrive_root = Path(r"C:\Users\payam_vngz\OneDrive\audit_test_4-7-26")
    row = build_audit_row(test_file, onedrive_root)
    print(row)



    




