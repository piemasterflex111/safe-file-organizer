"""Filename normalization helpers."""

import re
from pathlib import Path

def normalize_filename(filename: str) -> str:
    """Clean filename by removing noise while keeping meaning."""
    name = filename.strip()  # Remove leading/trailing whitespace

    # Remove file extensions temporarily.
    stem = Path(name).stem
    ext = Path(name).suffix.lower()

    # Replace multiple spaces/underscores with a single underscore
    stem = re.sub(r'[\s_]+', '_', stem)

    # Remove common noise words (case-insensitive)
    noise_words = ['copy', 'final', 'v1', 'v2', 'v3', 'v4', 'old', 'backup', 'untitled', 'new folder', 'gold', 'pass', 'clean']
    for word in noise_words:
        stem = re.sub(rf'_{word}_?', '_', stem, flags=re.IGNORECASE)

    # Convert to lowercase
    stem = stem.lower()

    # Remove leading/trailing underscores
    stem = stem.strip('_')

    # If filename becomes too short or empty, keep original stem
    if len(stem) < 3:
        stem = Path(name).stem.lower().replace(' ', '_')

    return stem + ext

# Test function - run this file directly to test
if __name__ == "__main__":
    test_names = [
        "Manufacturing_Onsite_ATE_v3.5_PRESENTATION_Pass3_DensityCollapse.pptx",
        "Candidate_Resume_ACCENTED_APPLIED_FROM_REPORT.pptx",
        "System_Validation_Visual_Diagrams.pptx",
        "winner-v3.pptx",
        "v4_SAFE.pptx",
        "untitled folder/Complete_Interview_Answer_Bank_v2_2.pptx",
    ]
    
    print("=== Normalization Test ===\n")
    for name in test_names:
        cleaned = normalize_filename(name)
        print(f"Original : {name}")
        print(f"Cleaned  : {cleaned}")
        print("-" * 80)
