"""
Cleanup audit for generated files, dependency folders, and project directories.

This module is report-only. It does not delete or move anything.
"""

from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path

from .config import LOG_DIR


GENERATED_CACHE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
}

DEPENDENCY_DIR_NAMES = {
    "node_modules",
    "venv",
    ".venv",
    "site-packages",
}

GIT_DIR_NAMES = {
    ".git",
}

GENERATED_FILE_NAMES = {
    ".ds_store",
    "thumbs.db",
    "desktop.ini",
}

GENERATED_FILE_EXTENSIONS = {
    ".pyc",
    ".pyo",
}

BUILD_OUTPUT_DIR_NAMES = {
    "dist",
    "build",
}

PROJECT_MARKER_FILES = {
    ".git",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "cargo.toml",
    "go.mod",
    "setup.py",
    "setup.cfg",
    "makefile",
    "cmakelists.txt",
}

PROJECT_MARKER_EXTENSIONS = {
    ".kicad_pro",
    ".kicad_pcb",
    ".sln",
    ".csproj",
}

MANAGED_CONTAINER_NAMES = {
    "_inbox_review",
    "_reorg",
    "_reorg_runs",
    "00_admin",
    "01_finance",
    "02_career",
    "03_engineering",
    "04_projects",
    "05_personal",
    "06_media",
    "90_archive",
}

PROTECTED_EMPTY_DIR_NAMES = {
    "apps",
    "desktop",
    "documents",
    "github",
    "imports",
    "inbox",
    "identity",
    "ids",
    "legal",
    "medical",
    "certificates",
    "bills",
    "budgeting",
    "income",
    "investing",
    "networth",
    "net_worth",
    "pay_stubs",
    "tax",
    "taxes",
    "auto",
    "car",
    "music",
    "pictures",
    "videos",
    "bytype",
    "byyear",
    "legacy",
}


def _relative_path(item: Path, root: Path) -> Path:
    try:
        return item.relative_to(root)
    except ValueError:
        return item


def _path_parts_lower(path: Path) -> list[str]:
    return [part.casefold() for part in path.parts]


def _nearest_named_ancestor(item: Path, root: Path, names: set[str]) -> Path | None:
    relative = _relative_path(item, root)
    parts = relative.parts

    for index, part in enumerate(parts):
        if part.casefold() in names:
            return root.joinpath(*parts[: index + 1])

    return None


def _is_empty_dir(item: Path) -> bool:
    if not item.is_dir():
        return False
    try:
        next(item.iterdir())
    except StopIteration:
        return True
    return False


def _is_managed_container(item: Path, root: Path) -> bool:
    relative = _relative_path(item, root)
    parts = [part.casefold() for part in relative.parts]
    return len(parts) <= 2 and any(part in MANAGED_CONTAINER_NAMES for part in parts)


def _is_protected_empty_dir(item: Path, root: Path) -> bool:
    if not item.is_dir() or not _is_empty_dir(item):
        return False

    relative = _relative_path(item, root)
    parts = [part.casefold() for part in relative.parts]
    if not parts:
        return True

    if len(parts) == 1:
        return True

    if _is_managed_container(item, root):
        return True

    return len(parts) <= 2 and parts[-1] in PROTECTED_EMPTY_DIR_NAMES


def _is_project_dir(item: Path, root: Path) -> bool:
    if not item.is_dir():
        return False

    if _is_managed_container(item, root):
        return False

    try:
        children = list(item.iterdir())
    except OSError:
        return False

    child_names = {child.name.casefold() for child in children}
    if child_names & PROJECT_MARKER_FILES:
        return True

    return any(child.is_file() and child.suffix.casefold() in PROJECT_MARKER_EXTENSIONS for child in children)


def find_project_roots(root: Path) -> list[Path]:
    project_roots = []

    for item in root.rglob("*"):
        if item.is_dir() and _is_project_dir(item, root):
            project_roots.append(item)

    return project_roots


def _nearest_project_root(item: Path, project_roots: list[Path]) -> Path | None:
    matches = []

    for project_root in project_roots:
        try:
            item.relative_to(project_root)
            matches.append(project_root)
        except ValueError:
            continue

    if not matches:
        return None

    return max(matches, key=lambda path: len(path.parts))


def classify_cleanup_item(item: Path, root: Path, project_roots: list[Path]) -> tuple[str, str, str]:
    relative = _relative_path(item, root)
    parts_lower = _path_parts_lower(relative)

    git_root = _nearest_named_ancestor(item, root, GIT_DIR_NAMES)
    if git_root is not None:
        return "REVIEW_GIT_REPO", "Git repository metadata; keep unless repo history is intentionally disposable", str(git_root)

    dependency_root = _nearest_named_ancestor(item, root, DEPENDENCY_DIR_NAMES)
    if dependency_root is not None:
        return "REVIEW_DEPENDENCY_FOLDER", "Dependency environment; usually reinstallable but review before deleting", str(dependency_root)

    cache_root = _nearest_named_ancestor(item, root, GENERATED_CACHE_DIR_NAMES)
    if cache_root is not None:
        return "DELETE_GENERATED_CACHE", "Generated cache directory candidate", str(cache_root)

    build_root = _nearest_named_ancestor(item, root, BUILD_OUTPUT_DIR_NAMES)
    if build_root is not None and "onedrive" not in parts_lower:
        return "REVIEW_BUILD_OUTPUT", "Build output directory candidate; review if source project can rebuild it", str(build_root)

    if item.is_file():
        name_lower = item.name.casefold()
        suffix_lower = item.suffix.casefold()
        if name_lower in GENERATED_FILE_NAMES or suffix_lower in GENERATED_FILE_EXTENSIONS:
            return "DELETE_GENERATED_CACHE", "Generated file candidate", ""

    project_root = _nearest_project_root(item, project_roots)
    if project_root is not None:
        if item == project_root:
            return "REVIEW_PROJECT_FOLDER", "Project folder should be preserved or moved as a unit", str(project_root)
        return "KEEP_PROJECT_CONTENT", "Inside a detected project folder; do not flatten into document buckets", str(project_root)

    if _is_protected_empty_dir(item, root):
        return "KEEP_PROTECTED_EMPTY_DIR", "Protected structural empty directory", ""

    if item.is_dir() and _is_empty_dir(item):
        return "REVIEW_EMPTY_DIR", "Empty directory candidate", ""

    if item.is_dir():
        return "KEEP_FOLDER", "Ordinary folder", ""

    return "KEEP_PERSONAL_FILE", "Ordinary file", ""


def build_cleanup_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    project_roots = find_project_roots(root)

    for item in root.rglob("*"):
        try:
            action, reason, matched_root = classify_cleanup_item(item, root, project_roots)
            stat = item.stat()
            rows.append({
                "action": action,
                "reason": reason,
                "item_type": "directory" if item.is_dir() else "file",
                "source_path": str(item),
                "relative_path": str(_relative_path(item, root)),
                "matched_root": matched_root,
                "name": item.name,
                "extension": item.suffix.lower() if item.is_file() else "",
                "size_bytes": str(stat.st_size) if item.is_file() else "",
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(
                    sep=" ",
                    timespec="seconds",
                ),
            })
        except OSError as exc:
            rows.append({
                "action": "CLEANUP_AUDIT_ERROR",
                "reason": str(exc),
                "item_type": "unknown",
                "source_path": str(item),
                "relative_path": str(_relative_path(item, root)),
                "matched_root": "",
                "name": item.name,
                "extension": "",
                "size_bytes": "",
                "modified_time": "",
            })

    return rows


def write_cleanup_csv(rows: list[dict[str, str]], output_path: Path | None = None) -> Path | None:
    if not rows:
        return None

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = LOG_DIR / f"cleanup_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _unique_quarantine_path(quarantine_root: Path, relative_path: Path) -> Path:
    candidate = quarantine_root / relative_path
    if not candidate.exists():
        return candidate

    counter = 1
    while True:
        suffixed = candidate.with_name(f"{candidate.name}__{counter}")
        if not suffixed.exists():
            return suffixed
        counter += 1


def quarantine_generated_cache(root: Path, rows: list[dict[str, str]] | None = None) -> tuple[Path, Path, dict[str, int]]:
    """
    Remove generated-cache candidates from root by moving them to a quarantine.

    This is intentionally safer than permanent deletion. The report records every
    attempted move and the quarantine path used.
    """
    if rows is None:
        rows = build_cleanup_rows(root)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    quarantine_root = LOG_DIR / f"generated_cache_quarantine_{timestamp}"
    report_path = LOG_DIR / f"delete_generated_cache_report_{timestamp}.csv"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    quarantine_root.mkdir(parents=True, exist_ok=True)

    raw_candidates = [
        row for row in rows
        if row.get("action") == "DELETE_GENERATED_CACHE"
    ]
    raw_candidates.sort(key=lambda row: len(Path(row["relative_path"]).parts))

    candidates = []
    selected_paths: list[Path] = []
    for row in raw_candidates:
        source = Path(row["source_path"])
        if any(_is_within_root(source, selected_path) for selected_path in selected_paths):
            continue
        candidates.append(row)
        selected_paths.append(source)

    report_rows = []
    summary = {
        "quarantined": 0,
        "missing": 0,
        "skipped": 0,
        "failed": 0,
    }

    for row in candidates:
        source = Path(row["source_path"])
        relative_path = Path(row["relative_path"])
        destination = _unique_quarantine_path(quarantine_root, relative_path)

        if not _is_within_root(source, root):
            summary["skipped"] += 1
            report_rows.append({
                **row,
                "status": "SKIPPED",
                "quarantine_path": "",
                "delete_reason": "Source path is outside cleanup root",
            })
            continue

        if not source.exists():
            summary["missing"] += 1
            report_rows.append({
                **row,
                "status": "MISSING",
                "quarantine_path": "",
                "delete_reason": "Source no longer exists",
            })
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            summary["quarantined"] += 1
            report_rows.append({
                **row,
                "status": "QUARANTINED",
                "quarantine_path": str(destination),
                "delete_reason": "",
            })
        except OSError as exc:
            summary["failed"] += 1
            report_rows.append({
                **row,
                "status": "FAILED",
                "quarantine_path": str(destination),
                "delete_reason": str(exc),
            })

    fieldnames = [
        "action",
        "reason",
        "item_type",
        "source_path",
        "relative_path",
        "matched_root",
        "name",
        "extension",
        "size_bytes",
        "modified_time",
        "status",
        "quarantine_path",
        "delete_reason",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report_rows)

    return quarantine_root, report_path, summary


def quarantine_dependency_folders(root: Path, rows: list[dict[str, str]] | None = None) -> tuple[Path, Path, dict[str, int]]:
    """
    Move dependency folders to quarantine as whole directory trees.

    This targets REVIEW_DEPENDENCY_FOLDER rows and deduplicates by matched_root
    so each environment is moved once.
    """
    if rows is None:
        rows = build_cleanup_rows(root)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    quarantine_root = LOG_DIR / f"dependency_quarantine_{timestamp}"
    report_path = LOG_DIR / f"quarantine_dependency_report_{timestamp}.csv"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    quarantine_root.mkdir(parents=True, exist_ok=True)

    roots: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("action") != "REVIEW_DEPENDENCY_FOLDER":
            continue
        matched_root = row.get("matched_root")
        if matched_root:
            roots.setdefault(matched_root, row)

    candidates = sorted(
        roots.items(),
        key=lambda item: len(Path(item[0]).parts),
    )

    report_rows = []
    moved_roots: list[Path] = []
    summary = {
        "quarantined": 0,
        "missing": 0,
        "skipped_nested": 0,
        "skipped": 0,
        "failed": 0,
    }

    for matched_root, row in candidates:
        source = Path(matched_root)
        if any(_is_within_root(source, moved_root) for moved_root in moved_roots):
            summary["skipped_nested"] += 1
            report_rows.append({
                **row,
                "dependency_root": str(source),
                "status": "SKIPPED_NESTED",
                "quarantine_path": "",
                "quarantine_reason": "Nested inside an already quarantined dependency root",
            })
            continue

        if not _is_within_root(source, root):
            summary["skipped"] += 1
            report_rows.append({
                **row,
                "dependency_root": str(source),
                "status": "SKIPPED",
                "quarantine_path": "",
                "quarantine_reason": "Dependency root is outside cleanup root",
            })
            continue

        if not source.exists():
            summary["missing"] += 1
            report_rows.append({
                **row,
                "dependency_root": str(source),
                "status": "MISSING",
                "quarantine_path": "",
                "quarantine_reason": "Dependency root no longer exists",
            })
            continue

        relative_path = _relative_path(source, root)
        destination = _unique_quarantine_path(quarantine_root, relative_path)

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            moved_roots.append(source)
            summary["quarantined"] += 1
            report_rows.append({
                **row,
                "dependency_root": str(source),
                "status": "QUARANTINED",
                "quarantine_path": str(destination),
                "quarantine_reason": "",
            })
        except OSError as exc:
            summary["failed"] += 1
            report_rows.append({
                **row,
                "dependency_root": str(source),
                "status": "FAILED",
                "quarantine_path": str(destination),
                "quarantine_reason": str(exc),
            })

    fieldnames = [
        "action",
        "reason",
        "item_type",
        "source_path",
        "relative_path",
        "matched_root",
        "dependency_root",
        "name",
        "extension",
        "size_bytes",
        "modified_time",
        "status",
        "quarantine_path",
        "quarantine_reason",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report_rows)

    return quarantine_root, report_path, summary


def remove_empty_dirs(root: Path, rows: list[dict[str, str]] | None = None) -> tuple[Path, Path, dict[str, int]]:
    """
    Remove empty directories under root.

    The report records every attempted removal. The undo script recreates
    directories that were removed, but it cannot restore deleted contents
    because these candidates are empty by definition.
    """
    if rows is None:
        rows = build_cleanup_rows(root)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = LOG_DIR / f"delete_empty_dirs_report_{timestamp}.csv"
    undo_path = LOG_DIR / f"undo_empty_dirs_{timestamp}.ps1"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    candidates = [
        row for row in rows
        if row.get("action") == "REVIEW_EMPTY_DIR"
    ]
    candidates.sort(
        key=lambda row: len(Path(row["relative_path"]).parts),
        reverse=True,
    )

    report_rows = []
    removed_paths = []
    summary = {
        "removed": 0,
        "not_empty": 0,
        "missing": 0,
        "skipped": 0,
        "failed": 0,
    }

    for row in candidates:
        source = Path(row["source_path"])

        if not _is_within_root(source, root):
            summary["skipped"] += 1
            report_rows.append({
                **row,
                "status": "SKIPPED",
                "delete_reason": "Source path is outside cleanup root",
            })
            continue

        if not source.exists():
            summary["missing"] += 1
            report_rows.append({
                **row,
                "status": "MISSING",
                "delete_reason": "Source no longer exists",
            })
            continue

        if not source.is_dir() or not _is_empty_dir(source):
            summary["not_empty"] += 1
            report_rows.append({
                **row,
                "status": "NOT_EMPTY",
                "delete_reason": "Directory is no longer empty",
            })
            continue

        try:
            source.rmdir()
            removed_paths.append(source)
            summary["removed"] += 1
            report_rows.append({
                **row,
                "status": "REMOVED",
                "delete_reason": "",
            })
        except OSError as exc:
            summary["failed"] += 1
            report_rows.append({
                **row,
                "status": "FAILED",
                "delete_reason": str(exc),
            })

    fieldnames = [
        "action",
        "reason",
        "item_type",
        "source_path",
        "relative_path",
        "matched_root",
        "name",
        "extension",
        "size_bytes",
        "modified_time",
        "status",
        "delete_reason",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report_rows)

    with undo_path.open("w", encoding="utf-8") as f:
        f.write("# Recreate empty directories removed by cleanup\n")
        for path in sorted(removed_paths, key=lambda item: len(item.parts)):
            f.write(f'New-Item -ItemType Directory -Force -LiteralPath "{path}" | Out-Null\n')

    return report_path, undo_path, summary
