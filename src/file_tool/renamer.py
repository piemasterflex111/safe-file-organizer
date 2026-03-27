from config import ALLOWED_EXTENSIONS, INBOX_DIR
from normalize import normalize_filename

def process_file(file_path, remamed, skipped):
            if not file_path.is_file():
                skipped.append((file_path.name, "not a file"))
                return  
            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                skipped.append((file_path.name, "extension not allowed"))
                return
            old_name = file_path.name
            new_name = normalize_filename(old_name)
            if old_name == new_name:
                skipped.append((old_name, "already normalized"))
                return
            new_path = file_path.with_name(new_name)
            if new_path.exists():
                skipped.append((old_name, "target name already exists"))
                return
            file_path.rename(new_path)
            remamed.append((old_name, new_name))

def walk_and_rename(folder_path, renamed, skipped):
      for item in folder_path.iterdir():
            print(f"Checking: {item}")
            if item.is_file():
                  process_file(item, renamed, skipped)
            elif item.is_dir():
                  print(f"Entering directory: {item}")
                  walk_and_rename(item, renamed, skipped)
            else:
                  skipped.append((item.name,"unknown item type"))

def rename_files(folder_path):
        renamed = []
        skipped = []
        walk_and_rename(folder_path, renamed,skipped)
        return renamed, skipped

if __name__ == "__main__":
    print(f"Scanning directory: {INBOX_DIR}")
    renamed, skipped = rename_files(INBOX_DIR)
    print("\nRenamed Files:")
    for old, new in renamed:
        print(f"  {old} -> {new}")
    print("\nSkipped Items:")
    for name, reason in skipped:
        print(f"  {name} (reason: {reason})")


