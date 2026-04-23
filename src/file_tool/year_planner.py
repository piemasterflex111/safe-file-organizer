"""
Professional year-based organization planner.

This planner routes loose files into stable bucket/year/topic folders. It is
report-only; no files are moved here.
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
from datetime import datetime
from pathlib import Path

from .config import LOG_DIR, ONEDRIVE_ROOT


LOW_VALUE_DATA_EXTENSIONS = {
    ".asc",
    ".ncd",
    ".ntb",
    ".dat",
    ".tmp",
    ".log",
    ".pyc",
    ".pyo",
}

ENGINEERING_EXTENSIONS = {
    ".py",
    ".ipynb",
    ".json",
    ".xml",
    ".csv",
    ".kicad_pcb",
    ".kicad_pro",
    ".kicad_sch",
    ".stl",
    ".3mf",
    ".step",
    ".stp",
    ".sldprt",
    ".sldasm",
    ".cs",
    ".cpp",
    ".c",
    ".hpp",
    ".h",
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".md",
    ".txt",
}

MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".heic",
    ".heif",
    ".mov",
    ".mp4",
    ".webm",
}


def _modified_year(path: Path) -> str:
    return str(datetime.fromtimestamp(path.stat().st_mtime).year)


def _relative_to_onedrive(path: Path) -> Path:
    try:
        return path.relative_to(ONEDRIVE_ROOT)
    except ValueError:
        return path


def _safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return value.strip("._-") or "root"


def _collision_destination(source: Path, destination: Path) -> Path:
    try:
        source_hint = "_".join(source.relative_to(ONEDRIVE_ROOT).parts[-4:-1])
    except ValueError:
        source_hint = source.parent.name
    hint = _safe_name(source_hint)[:80]
    digest = hashlib.sha1(str(source).encode("utf-8", errors="ignore")).hexdigest()[:10]
    base = f"{destination.stem}__from_{hint}_{digest}"
    candidate = destination.with_name(f"{base}{destination.suffix}")
    counter = 2

    while candidate.exists():
        candidate = destination.with_name(f"{base}_{counter}{destination.suffix}")
        counter += 1

    return candidate


def _topic_for_file(path: Path) -> tuple[str, str, str]:
    text = str(path).casefold()
    ext = path.suffix.casefold()

    if ext in LOW_VALUE_DATA_EXTENSIONS:
        return "90_ARCHIVE", "Generated_And_Raw_Data", "Low-value generated/data artifact"

    if any(word in text for word in ["resume", "linkedin", "interview", "job", "tesla", "mach", "recruiter", "offer"]):
        return "02_CAREER", "Resume_And_Applications", "Career/resume/application content"

    if any(word in text for word in ["tax", "taxes", "pay_stub", "pay stub", "ynab", "bill", "verizon", "unemployment", "statement"]):
        return "01_FINANCE", "Taxes_Pay_Bills", "Finance/tax/pay/bill content"

    if any(word in text for word in ["medical", "certificate", "identity", "license", "passport"]):
        return "00_ADMIN", "Identity_Medical_Certificates", "Admin/identity/medical content"

    if ext in MEDIA_EXTENSIONS:
        return "06_MEDIA", "Photos_Video_Audio", "Media file"

    if ext in ENGINEERING_EXTENSIONS or any(word in text for word in ["python", "stm32", "kicad", "github", "firmware", "validation", "automation"]):
        return "03_ENGINEERING", "Projects_And_Technical", "Engineering/project content"

    if ext in DOCUMENT_EXTENSIONS:
        return "_INBOX_REVIEW", "Documents_To_Classify", "Document needs manual topic classification"

    return "_INBOX_REVIEW", "Other_To_Classify", "Unclassified file type"


def build_year_plan(root: Path = ONEDRIVE_ROOT) -> list[dict[str, str]]:
    rows = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        bucket, topic, reason = _topic_for_file(path)
        year = _modified_year(path)
        destination_dir = root / bucket / year / topic
        proposed_path = destination_dir / path.name

        if str(path.parent).casefold() == str(destination_dir).casefold():
            action = "NO_CHANGE"
        elif proposed_path.exists():
            action = "REVIEW_YEAR_COLLISION"
        elif bucket == "_INBOX_REVIEW":
            action = "REVIEW_CLASSIFY_TO_YEAR"
        elif path.suffix.casefold() in LOW_VALUE_DATA_EXTENSIONS:
            action = "REVIEW_ARCHIVE_LOW_VALUE_DATA"
        else:
            action = "MOVE_TO_YEAR_TOPIC"

        rows.append({
            "source_path": str(path),
            "relative_path": str(_relative_to_onedrive(path)),
            "year": year,
            "bucket": bucket,
            "topic": topic,
            "reason": reason,
            "extension": path.suffix.lower(),
            "size_bytes": str(path.stat().st_size),
            "proposed_path": str(proposed_path),
            "action": action,
        })

    return rows


def write_year_plan(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"year_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def _apply_year_plan_actions(
    plan_csv_path: Path,
    *,
    allowed_actions: set[str],
    report_prefix: str,
    undo_title: str,
    rename_collisions: bool = False,
    dry_run: bool = True,
) -> tuple[Path | None, Path | None, dict[str, int]]:
    if not plan_csv_path.exists():
        raise FileNotFoundError(f"Year plan not found: {plan_csv_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = LOG_DIR / f"{report_prefix}_report_{timestamp}.csv"
    undo_path = LOG_DIR / f"undo_{report_prefix}_{timestamp}.ps1"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    report_rows = []
    undo_commands = []
    summary = {
        "moved": 0,
        "dry_run": 0,
        "skipped": 0,
        "missing": 0,
        "destination_exists": 0,
        "failed": 0,
    }

    with plan_csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = Path(row["source_path"])
            destination = Path(row["proposed_path"])
            action = row["action"]

            if action not in allowed_actions:
                summary["skipped"] += 1
                continue

            if not source.exists():
                summary["missing"] += 1
                report_rows.append({**row, "status": "MISSING", "apply_reason": "Source no longer exists"})
                continue

            if destination.exists():
                if rename_collisions and action == "REVIEW_YEAR_COLLISION":
                    destination = _collision_destination(source, destination)
                else:
                    summary["destination_exists"] += 1
                    report_rows.append({**row, "status": "SKIPPED", "apply_reason": "Destination already exists"})
                    continue

            if dry_run:
                summary["dry_run"] += 1
                report_rows.append({**row, "status": "DRY_RUN", "apply_reason": "Preview only"})
                continue

            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                undo_commands.append(f'Move-Item -LiteralPath "{destination}" -Destination "{source}"')
                summary["moved"] += 1
                report_rows.append({**row, "status": "MOVED", "applied_path": str(destination), "apply_reason": ""})
            except OSError as exc:
                summary["failed"] += 1
                report_rows.append({**row, "status": "FAILED", "apply_reason": str(exc)})

    if report_rows:
        fieldnames = list(report_rows[0].keys())
        with report_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(report_rows)
    else:
        report_path = None

    if not dry_run and undo_commands:
        with undo_path.open("w", encoding="utf-8") as f:
            f.write(f"# {undo_title}\n")
            for command in undo_commands:
                f.write(command + "\n")
    else:
        undo_path = None

    return report_path, undo_path, summary


def apply_year_archive_plan(plan_csv_path: Path, dry_run: bool = True) -> tuple[Path | None, Path | None, dict[str, int]]:
    """Apply only REVIEW_ARCHIVE_LOW_VALUE_DATA rows from a year plan."""
    return _apply_year_plan_actions(
        plan_csv_path,
        allowed_actions={"REVIEW_ARCHIVE_LOW_VALUE_DATA"},
        report_prefix="apply_year_archive",
        undo_title="Undo year archive moves",
        dry_run=dry_run,
    )


def apply_year_topic_plan(plan_csv_path: Path, dry_run: bool = True) -> tuple[Path | None, Path | None, dict[str, int]]:
    """Apply only safe MOVE_TO_YEAR_TOPIC rows from a year plan."""
    return _apply_year_plan_actions(
        plan_csv_path,
        allowed_actions={"MOVE_TO_YEAR_TOPIC"},
        report_prefix="apply_year_topic",
        undo_title="Undo year topic moves",
        dry_run=dry_run,
    )


def apply_year_finish_plan(plan_csv_path: Path, dry_run: bool = True) -> tuple[Path | None, Path | None, dict[str, int]]:
    """Apply review rows into dated inbox folders and rename same-name collisions."""
    return _apply_year_plan_actions(
        plan_csv_path,
        allowed_actions={"REVIEW_CLASSIFY_TO_YEAR", "REVIEW_YEAR_COLLISION"},
        report_prefix="apply_year_finish",
        undo_title="Undo year finish moves",
        rename_collisions=True,
        dry_run=dry_run,
    )
