"""
Configuration for Safe File Organizer.

Paths, target folder structure, and classification rules live here so the CLI
can be adapted without changing the workflow code.
"""

import os
from pathlib import Path

# ====================== ROOT PATHS ======================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_INPUT_DIR = DATA_DIR / "sample_files"
LOG_DIR = PROJECT_ROOT / "logs"

# ====================== TARGET STRUCTURE ======================
TARGET_BUCKETS = {
    "ADMIN": "00_ADMIN",
    "FINANCE": "01_FINANCE",
    "CAREER": "02_CAREER",
    "JOB_SEARCH": "02_CAREER/01_Job_Search",
    "STUDY": "02_CAREER/02_Study_Materials",
    "PORTFOLIO": "02_CAREER/03_Portfolio_And_Projects",
    "ENGINEERING": "03_ENGINEERING",
    "PROJECTS": "03_ENGINEERING/01_Active_Projects",
    "VALIDATION": "03_ENGINEERING/02_Validation_And_Testing",
    "DIAGRAMS": "03_ENGINEERING/03_Diagrams_And_Docs",
    "PERSONAL": "05_PERSONAL",
    "MEDIA": "06_MEDIA",
    "ARCHIVE": "90_ARCHIVE",
    "INBOX": "_INBOX_REVIEW",
}

# Default root for local OneDrive-style cleanup runs. Override with
# FILE_TOOL_ONEDRIVE_ROOT when running against another directory.
ONEDRIVE_ROOT = Path(os.environ.get("FILE_TOOL_ONEDRIVE_ROOT", Path.home() / "OneDrive"))

# ====================== ALLOWED EXTENSIONS ======================
ALLOWED_EXTENSIONS = {".md", ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".heic",".avi", ".mkv", ".zip", ".rar", ".7z", ".csv", ".json", ".xml", ".html", ".css", ".js", ".py", ".ipynb", ".exe", ".dll", ".iso", ".bin", ".apk", ".dmg", ".tar", ".gz"}

# ====================== KEYWORD RULES (for classification) ======================
CLASSIFICATION_KEYWORDS = {
    "CAREER": {
        "resume", "interview", "job", "offer", "linkedin", "mach", "tesla", 
        "relativity", "palomar", "rocketlab", "masimo", "neros", "onsite", 
        "presentation", "deck", "pptx", "slide", "powerpoint", "story", 
        "vp_call", "phone_screen", "recruiter", "answer_bank", "study_packet",
        "cheat_sheet", "script", "prep", "status", "log", "recap"
    },
    "ENGINEERING": {
        "stm32", "firmware", "pcba", "bringup", "validation", "test", "engineer",
        "hardware", "software", "diagram", "architecture", "framework", "can",
        "uart", "spi", "i2c", "debug", "probe", "bench", "sitl", "hitl",
        "embedded", "python", "backend", "api"
    },
    "FINANCE": {
        "tax", "ynab", "wells fargo", "statement", "budget", "pay stub", 
        "bill", "finance", "payment", "insurance"
    },
    "ARCHIVE": {
        "archive", "old", "backup", "final", "v1", "v2", "v3", "v4", "v5", 
        "pass", "gold", "legacy", "reorg", "run_", "snapshot"
    },
    "INBOX": {
        "inbox", "new folder", "untitled", "temp", "junk", "test", "_reorg"
    },
}
