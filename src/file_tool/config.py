"""
Configuration for PneDrive Organize Tool
======================================
All paths, target folder structure, and rules live here.
Easy to change without touching other files.
"""

from pathlib import Path

# ====================== ROOT PATHS ======================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample_files"
LOG_DIR = PROJECT_ROOT / "logs"

# ====================== TARGET STRUCTURE ======================
TARGET_BUCKETS = {
    "00_ADMIN": "00_ADMIN",
    "01_FINANCE": "01_FINANCE",
    "02_CAREER": "02_CAREER",
    "03_ENGINEERING": "03_ENGINEERING",
    "04_PROJECTS": "04_PROJECTS",
    "05_PERSONAL": "05_PERSONAL",   
    "06_MEDIA": "06_MEDIA",
    "90_ARCHIVE": "90_ARCHIVE",
    "INBOX": "INBOX_REVIEW",    # temporary drop zone
}

# Default root for my real OneDrive
ONEDRIVE_ROOT = Path(r"C:\Users\payam_vngz\OneDrive")

# ====================== ALLOWED EXTENSIONS ======================
ALLOWED_EXTENSIONS = {".md", ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".heic",".avi", ".mkv", ".zip", ".rar", ".7z", ".csv", ".json", ".xml", ".html", ".css", ".js", ".py", ".ipynb", ".exe", ".dll", ".iso", ".bin", ".apk", ".dmg", ".tar", ".gz"}

# ====================== KEYWORD RULES (for classification) ======================
CLASSIFICATION_RULES = {
    "CAREER": {"resume", "mach", "tesla", "relativity", "job", "offer", "interview", "linkedin"},
    "ENGINEERING": {"stm32", "python", "firmware", "test", "engineer", "pptx", "diagram"},
    "FINANCE": {"tax", "ynab", "pay stub", "bill", "budget"},
    "ARCHIVE": {"old", "archive", "backup", "v1", "v2", "final"},
    "INBOX": {"inbox", "new folder", "untitled"},
    }