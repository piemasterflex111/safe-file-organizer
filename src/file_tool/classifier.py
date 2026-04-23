"""
Classifier Module
=================
Decides which clean bucket each file should go to 
(CAREER, ENGINEERING, FINANCE, etc.).
Looks at both the filename and the current folder path.
"""

from pathlib import Path
from .config import CLASSIFICATION_KEYWORDS, TARGET_BUCKETS   

def classify_file(file_path: Path) -> str:
    """
    Decide the category for a file.
    Uses both filename and full path for better routing into subfolders.
    """
    name_lower = file_path.name.lower()
    full_path_lower = str(file_path).lower()

    # High priority: Job Search (company names, interview, resume, onsite, etc.)
    if any(k in full_path_lower for k in ["mach", "tesla", "relativity", "palomar", "rocketlab", "masimo", "neros", "castelion", "terran", "gatekeeper", "onsite", "interview", "phone_screen", "resume", "job_search", "vp_call", "fve", "mfg"]):
        return "JOB_SEARCH"

    if any(k in full_path_lower for k in ["medical", "certificate", "identity", "passport", "license", "unemployment"]):
        return "ADMIN"

    if any(k in full_path_lower for k in ["tax", "taxes", "pay stub", "pay_stubs", "ynab", "verizon", "dad", "money", "bill", "finance"]):
        return "FINANCE"

    if any(k in full_path_lower for k in ["iphone", "phone link", "pictures", "videos", "camera roll", "screenshots", "media"]):
        return "MEDIA"

    # Study / Prep materials
    if any(k in full_path_lower for k in ["study", "drill", "cheat_sheet", "answer_bank", "prep", "script", "rehearse", "moebius", "phone_drill", "ev_playbook", "first_principles", "fundamentals", "ohm", "voltage_divider"]):
        return "STUDY"

    # Engineering / Validation / STM32 / PCBA / Firmware
    if any(k in full_path_lower for k in ["stm32", "pcba", "bringup", "validation", "firmware", "test_station", "hardware", "diagram", "architecture", "embedded", "debug", "execution_traces", "mermaid"]):
        return "ENGINEERING"

    # Fallback to config keywords
    for category, keywords in CLASSIFICATION_KEYWORDS.items():
        if any(keyword in name_lower for keyword in keywords) or any(keyword in full_path_lower for keyword in keywords):
            return category

    # Default
    return "INBOX"


def get_destination_bucket(file_path: Path) -> str:
    category = classify_file(file_path)
    
    mapping = {
        "JOB_SEARCH": "02_CAREER/01_Job_Search",
        "STUDY": "02_CAREER/02_Study_Materials",
        "ENGINEERING": "03_ENGINEERING/02_Validation_And_Testing",
        "CAREER": "02_CAREER",
        "FINANCE": "01_FINANCE",
        "ADMIN": "00_ADMIN",
        "PERSONAL": "05_PERSONAL",
        "MEDIA": "06_MEDIA",
        "ARCHIVE": "90_ARCHIVE",
        "INBOX": "_INBOX_REVIEW",
    }
    
    return mapping.get(category, "_INBOX_REVIEW")


def get_directory_destination_bucket(directory_path: Path) -> str:
    """Classify a directory for whole-folder organization."""
    name_lower = directory_path.name.lower()
    path_lower = str(directory_path).lower()

    if any(k in path_lower for k in ["archive", "_reorg", "snapshot", "old computer"]):
        return "90_ARCHIVE"
    if any(k in path_lower for k in ["tax", "taxes", "pay stub", "pay_stubs", "ynab", "verizon", "dad", "money", "bill"]):
        return "01_FINANCE"
    if any(k in path_lower for k in ["resume", "linkedin", "tesla", "mach", "interview", "job", "vp mach"]):
        return "02_CAREER/01_Job_Search"
    if any(k in path_lower for k in ["python", "stm32", "github", "engineering", "automation", "kicad"]):
        return "03_ENGINEERING/01_Active_Projects"
    if any(k in path_lower for k in ["medical", "certificate", "unemployment", "identity"]):
        return "00_ADMIN"
    if any(k in path_lower for k in ["iphone", "phone link", "pictures", "videos", "media"]):
        return "06_MEDIA"
    if name_lower in {"chatgpt", "chatgpt_knowledge", "custom_gpt_prompts", "imports", "gmail exports"}:
        return "90_ARCHIVE"

    return get_destination_bucket(directory_path)
    

# Improved Test Block
if __name__ == "__main__":
    print("=== Classification Test ===\n")
    
    test_files = [
        Path("C:/Users/example/OneDrive/02_CAREER/resume_v3.pdf"),
        Path("C:/Users/example/OneDrive/engineering_project/diagram.pptx"),
        Path("C:/Users/example/OneDrive/01_FINANCE/taxes_2025.pdf"),
        Path("C:/Users/example/OneDrive/New folder/untitled.pptx"),
    ]
    
    for f in test_files:
        category = classify_file(f)
        bucket = get_destination_bucket(f)
        print(f"File: {f.name}")
        print(f"Category: {category}")
        print(f"Destination Bucket: {bucket}")
        print("-" * 60)
