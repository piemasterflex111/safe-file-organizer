from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INBOX_DIR = DATA_DIR /  "sample_input"
LOG_DIR = DATA_DIR / "logs"

ALLOWED_EXTENSIONS = {
    ".md", ".png", ".jpg", ".jpeg", ".pdf", 
    ".docx", ".xlsx", ".pptx",".txt", ".csv", 
    ".zip", ".rar", ".7z", ".tar.gz", ".mp4", 
    ".avi", ".mkv", ".mp3", ".wav"
    }


