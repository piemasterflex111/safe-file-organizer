from config import INBOX_DIR, ALLOWED_EXTENSIONS

def scan_files(folder_path):
    accepted = []
    skipped = []

    for item in folder_path.iterdir():
        if not item.is_file():
            skipped.append((item.name, "not a file"))
            continue

        if item.suffix.lower() in ALLOWED_EXTENSIONS:
            accepted.append(item)
        else:
            skipped.append((item.name, "extension not allowed"))

    return accepted, skipped