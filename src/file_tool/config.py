from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INBOX_DIR = DATA_DIR / "sample_input"
LOG_DIR = DATA_DIR / "logs"

ALLOWED_EXTENSIONS = {
    ".md", ".png", ".jpg", ".jpeg", ".pdf",
    ".docx", ".xlsx", ".pptx", ".txt", ".csv",
    ".zip", ".rar", ".7z", ".tar.gz", ".mp4",
    ".avi", ".mkv", ".mp3", ".wav",
}

TRUSTED_TOP_LEVEL_FOLDERS = {
    "00_ADMIN",
    "01_FINANCE",
    "02_CAREER",
    "03_ENGINEERING",
    "04_PROJECTS",
    "05_PERSONAL",
    "06_MEDIA",
    "90_ARCHIVE",
}

DUPLICATE_ROOT_TO_CANONICAL = {
    "ARCHIVE_9-19-25": "90_ARCHIVE",
    "RESUME_DIRECTORY_9-19-25": "02_CAREER",
    "Linkedin Resumes 3-23-26": "02_CAREER",
    "Stm32": "03_ENGINEERING",
    "TAXES_10-4-25": "01_FINANCE",
    "PAY STUBS 10-20-25": "01_FINANCE",
    "YNAB 10-24-25": "01_FINANCE",
}

GENERIC_ROOTS = {
    "Desktop",
    "Documents",
    "Imports",
    "GMAIL EXPORTS",
}