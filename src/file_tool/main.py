from .config import INBOX_DIR
from .scanner import scan_files
from .renamer import rename_files
import argparse
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(INBOX_DIR), help="Folder to scan")
    args = parser.parse_args()

    target_folder = Path(args.input)
    print(f"Using input folder: {target_folder}")
    print(f"Exists: {target_folder.exists()}")
    print(f"Is dir: {target_folder.is_dir()}")

    accepted, skipped_scan = scan_files(target_folder)
    renamed, skipped_rename = rename_files(accepted, apply_changes=False)

    print("Accepted files:")
    for path in accepted:
        print(f"    {path}")

    print("\nScan skips:")
    for name, reason in skipped_scan:
        print(f"    {name} -> {reason}")
    
    print("\nRename preview:")
    for old, new in renamed:
        print(f"    {old} -> {new}")
    
    print("\nRename skips:")
    for name, reason in skipped_rename:
        print(f" {name} -> {reason}")

    print(f"Accepted files: {len(accepted)}")
    print(f"Scan skips: {len(skipped_scan)}")
    print(f"Rename preview count: {len(renamed)}")
    print(f"Rename skips: {len(skipped_rename)}")

if __name__=="__main__":
    main()
    print("\nSummary:")

