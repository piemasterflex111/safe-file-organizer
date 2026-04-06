from .config import ALLOWED_EXTENSIONS, INBOX_DIR
from .normalize import normalize_filename

def rename_files(files: list[Path], apply_changes: bool = False) -> tuple[list[tuple[str,str]]]:
        renamed: list[tuple[str,str]] = []
        skipped: list[tuple[str,str]] = []

        for file_path in files:
              old_name = file_path.name
              new_name = normalize_filename(old_name)
              if old_name == new_name:
                    skipped.append((old_name, "already normalized"))
                    continue
              new_path = file_path.with_name(new_name)
              if new_path.exists():
                    skipped.append((old_name, "target name already exists"))
                    continue
              if apply_changes:
                    file_path.rename(new_path)
              renamed.append((old_name, new_name))
        return renamed, skipped
                                   













