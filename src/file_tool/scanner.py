from pathlib import Path
from .config import ALLOWED_EXTENSIONS

def scan_files(folder_path: Path) -> tuple[list[Path], list[tuple[str,str]]]:
    accepted: list[Path] = []
    skipped: list[tuple[str,str]] = []

    if not folder_path.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    for item in folder_path.iterdir():
        if item.is_file():
            if item.suffix.lower() in ALLOWED_EXTENSIONS:
                accepted.append(item)
            else:
                skipped.append((item.name, "extension not allowed"))
        elif item.is_dir():
            child_accepted, child_skipped = scan_files(item)
            accepted.extend(child_accepted)
            skipped.extend(child_skipped)
        else:
            skipped.append((str(item), "unknown item type"))

    return accepted, skipped