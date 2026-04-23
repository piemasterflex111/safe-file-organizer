from pathlib import Path
from .config import ALLOWED_EXTENSIONS

def scan_files(
    folder_path: Path,
    *,
    allowed_extensions: set[str] | None = ALLOWED_EXTENSIONS,
) -> tuple[list[Path], list[tuple[str,str]]]:
    accepted: list[Path] = []
    skipped: list[tuple[str,str]] = []

    if not folder_path.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    for item in folder_path.iterdir():
        if item.is_file():
            if allowed_extensions is None or item.suffix.lower() in allowed_extensions:
                accepted.append(item)
            else:
                skipped.append((item.name, "extension not allowed"))
        elif item.is_dir():
            child_accepted, child_skipped = scan_files(
                item,
                allowed_extensions=allowed_extensions,
            )
            accepted.extend(child_accepted)
            skipped.extend(child_skipped)
        else:
            skipped.append((str(item), "unknown item type"))

    return accepted, skipped


def scan_all_files(folder_path: Path) -> tuple[list[Path], list[tuple[str, str]]]:
    """Recursively scan every file regardless of extension."""
    return scan_files(folder_path, allowed_extensions=None)
