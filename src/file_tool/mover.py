"""
Mover Module - Safe Apply
=========================
Reads the move plan CSV and safely moves files.
Creates an undo script for safety.
"""

from pathlib import Path
import csv
import shutil
from datetime import datetime

from .config import ONEDRIVE_ROOT, LOG_DIR

def _display(value: object) -> str:
    """Return console-safe text for Windows code pages."""
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def _write_apply_report(rows: list[dict]) -> Path | None:
    """Write a per-row apply report so skipped items are visible."""
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOG_DIR / f"apply_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fieldnames = [
        "source_path",
        "proposed_path",
        "action",
        "status",
        "reason",
    ]

    with report_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return report_path

def apply_move_plan(plan_csv_path: Path, dry_run: bool = True) -> None:
    """
    Apply the moves from a move plan CSV.
    dry_run=True means only show what would happen (safer).
    """
    if not plan_csv_path.exists():
        print(f"[ERROR] Move plan not found: {plan_csv_path}")
        return

    moves_applied = []
    undo_commands = []
    report_rows = []
    summary = {
        "moved": 0,
        "dry_run": 0,
        "no_change": 0,
        "review_collision": 0,
        "missing_source": 0,
        "destination_exists": 0,
        "failed": 0,
        "unsupported_action": 0,
    }

    print("DRY RUN - Preview only" if dry_run else "APPLYING MOVES")

    with plan_csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = Path(row["source_path"])
            destination = Path(row["proposed_path"])
            action = row.get("action", "MOVE_RENAME")

            if action == "NO_CHANGE":
                summary["no_change"] += 1
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": "Already in planned location",
                })
                continue

            if action == "REVIEW_COLLISION":
                summary["review_collision"] += 1
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": "Destination existed when the plan was created; review manually",
                })
                continue

            if action == "REVIEW_PLAN_COLLISION":
                summary["review_collision"] += 1
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": "Multiple plan rows target the same destination; review manually",
                })
                continue

            if action != "MOVE_RENAME":
                summary["unsupported_action"] += 1
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": f"Unsupported action: {action}",
                })
                continue

            if not source.exists():
                summary["missing_source"] += 1
                print(f"[WARN] Source file missing: {_display(source.name)}")
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": "Source file missing",
                })
                continue

            if destination.exists():
                summary["destination_exists"] += 1
                print(f"[WARN] Destination already exists, skipping: {_display(destination.name)}")
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "SKIPPED",
                    "reason": "Destination already exists",
                })
                continue

            if dry_run:
                summary["dry_run"] += 1
                print(f"Would move: {_display(source.name)} -> {_display(destination.parent.name)}/{_display(destination.name)}")
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "DRY_RUN",
                    "reason": "Preview only",
                })
                continue

            # Create destination folder
            destination.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(source), str(destination))
                moves_applied.append((source, destination))
                undo_commands.append(f'move "{destination}" "{source}"')
                summary["moved"] += 1
                print(f"[OK] Moved: {_display(source.name)} -> {_display(destination.name)}")
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "MOVED",
                    "reason": "",
                })
            except Exception as e:
                summary["failed"] += 1
                print(f"[ERROR] Failed to move {_display(source.name)}: {_display(e)}")
                report_rows.append({
                    "source_path": str(source),
                    "proposed_path": str(destination),
                    "action": action,
                    "status": "FAILED",
                    "reason": str(e),
                })

    if not dry_run and moves_applied:
        undo_path = LOG_DIR / f"undo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ps1"
        with undo_path.open("w", encoding="utf-8") as f:
            f.write("# Undo script - run this PowerShell script to revert moves\n")
            for cmd in undo_commands:
                f.write(cmd + "\n")
        
        print("\n[OK] All moves completed!")
        print(f"Undo script created at: {undo_path}")
        print("Run the undo script if you need to revert.")

    report_path = _write_apply_report(report_rows)
    if report_path:
        print(f"Apply report created at: {report_path}")

    print("\nApply summary:")
    for key, value in summary.items():
        if value:
            print(f"  {key}: {value}")

    if dry_run:
        print("\nThis was a dry run. No files were moved.")
        print("Review the plan, then run --apply again and type YES to execute.")

def main():
    # For testing - find the latest move plan
    plan_files = list(LOG_DIR.glob("move_plan_*.csv"))
    if not plan_files:
        print("No move plan found. Run --plan first.")
        return
    
    latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
    print(f"Using latest plan: {latest_plan}")
    
    # Dry run by default for safety
    apply_move_plan(latest_plan, dry_run=True)

if __name__ == "__main__":
    main()
