# Traceability And Reproduction Guide

This document explains what the repository does now, what was changed, how the GitHub branch was finalized, and how to reproduce the workflow later.

The goal is auditability: every risky action should have a review step, a report, and a verification step.

## Repository Purpose

This repo is a Python command-line tool for safely auditing, cleaning, and organizing messy local file trees such as synced cloud-drive folders.

It is designed around this rule:

```text
Look first. Plan second. Apply only after explicit confirmation.
```

The tool can:

- scan files recursively
- audit every file and directory
- detect generated cache
- detect dependency folders
- detect Git repositories and project folders
- find empty folders
- create CSV reports
- create move plans
- organize files into category/year/topic folders
- quarantine cleanup candidates
- avoid overwriting collisions
- write undo scripts for applied moves
- verify what remains after cleanup

## Current Public Branch State

The finalized work was first committed on `production-upgrade`, then merged into `master`.

Final commit:

```text
4fec621 Finalize safe file organization workflow
```

Current branch state after finalization:

```text
master == origin/master == production-upgrade == origin/production-upgrade
```

That means the default GitHub page now shows the finalized version.

## Important Repo Files

### `README.md`

Public project overview.

It explains:

- what the tool does
- how to run it
- safety behavior
- main commands
- repository layout
- portfolio framing

### `CASE_STUDY.md`

Sanitized case study.

It explains that the tool was validated on a real large OneDrive cleanup without publishing private filenames or full inventories.

### `.gitignore`

Prevents generated and private cleanup output from being committed.

Important ignored paths:

```text
.venv/
logs/
artifacts/
*.csv
__pycache__/
.pytest_cache/
```

### `data/sample_files/`

Small safe sample data for testing the CLI without touching real files.

### `tests/test_core_workflows.py`

Read-only unit tests for core behavior.

Run them with:

```bash
python -m unittest
```

Expected output:

```text
Ran 4 tests
OK
```

## Source Module Map

### `src/file_tool/main.py`

CLI entry point.

This is what runs when you use:

```bash
python -m src.file_tool.main
```

It parses command-line options and dispatches to the right workflow.

### `src/file_tool/config.py`

Central settings.

Contains:

- project paths
- sample input path
- log output path
- bucket names
- allowed extensions
- classification keywords

The default OneDrive-style root is portable:

```text
FILE_TOOL_ONEDRIVE_ROOT
```

Example:

```powershell
$env:FILE_TOOL_ONEDRIVE_ROOT = "C:\Users\you\OneDrive"
```

### `src/file_tool/scanner.py`

Recursively finds files.

Used by:

```text
--scan
--plan
```

### `src/file_tool/normalize.py`

Cleans filenames while preserving extensions.

Example:

```text
Resume Final Copy V2.PDF -> resume.pdf
```

### `src/file_tool/classifier.py`

Routes files or folders into broad categories.

Examples:

```text
resume, interview, job -> career
tax, bill, pay stub -> finance
photo, video, screenshot -> media
python, firmware, kicad -> engineering
unknown -> inbox review
```

### `src/file_tool/audit.py`

Creates a full path inventory report.

It records:

- item type
- source path
- relative path
- parent folder
- top-level folder
- filename
- extension
- size
- modified time
- depth
- empty-folder status
- normalized filename
- proposed destination
- action

### `src/file_tool/cleanup.py`

Classifies and applies safe cleanup operations.

Important actions:

```text
KEEP_PERSONAL_FILE
KEEP_PROJECT_CONTENT
REVIEW_GIT_REPO
REVIEW_DEPENDENCY_FOLDER
DELETE_GENERATED_CACHE
REVIEW_EMPTY_DIR
KEEP_PROTECTED_EMPTY_DIR
REVIEW_PROJECT_FOLDER
REVIEW_BUILD_OUTPUT
```

Cleanup operations:

```text
--cleanup-audit
--delete-generated-cache
--quarantine-dependencies
--delete-empty-dirs
```

Generated cache and dependency folders are moved to quarantine instead of being permanently deleted.

### `src/file_tool/directory_planner.py`

Plans whole-folder top-level moves.

Used by:

```text
--directory-plan
--apply-directory-plan
```

### `src/file_tool/year_planner.py`

Main organization planner.

Routes files into:

```text
bucket / year / topic / file
```

Examples:

```text
06_MEDIA/2025/Photos_Video_Audio/photo.png
02_CAREER/2026/Resume_And_Applications/resume.pdf
01_FINANCE/2025/Taxes_Pay_Bills/tax_form.pdf
03_ENGINEERING/2026/Projects_And_Technical/script.py
```

Used by:

```text
--year-plan
--apply-year-topic
--apply-year-finish
--apply-year-archive
```

### `src/file_tool/mover.py`

Applies legacy move plans safely.

Checks:

- source exists
- destination does not already exist
- action is supported
- collisions are skipped

### `src/file_tool/planner.py`

Builds older-style move plans based on normalized filenames and broad categories.

### `src/file_tool/review.py`

Creates review reports for unresolved move-plan rows.

Useful for:

- collisions
- many sources targeting one destination
- missing source files
- same-size duplicate candidates

## Main CLI Commands

### Scan

```bash
python -m src.file_tool.main --input data/sample_files --scan
```

Purpose:

```text
Count accepted and skipped files.
```

### Full Audit

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --audit
```

Purpose:

```text
Write a CSV inventory of every file and folder.
```

### Cleanup Audit

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --cleanup-audit
```

Purpose:

```text
Classify cleanup candidates without changing files.
```

### Quarantine Generated Cache

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --delete-generated-cache
```

Purpose:

```text
Move generated cache candidates into logs/generated_cache_quarantine_*.
```

This requires typing:

```text
YES
```

### Quarantine Dependencies

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --quarantine-dependencies
```

Purpose:

```text
Move dependency folders such as .venv, venv, node_modules, and site-packages into quarantine.
```

This requires typing:

```text
YES
```

### Delete Empty Directories

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --delete-empty-dirs
```

Purpose:

```text
Remove directories that are still empty at deletion time.
```

This writes an undo/recreate script.

This requires typing:

```text
YES
```

### Directory Plan

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --directory-plan
```

Purpose:

```text
Plan top-level folder organization.
```

### Apply Directory Plan

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-directory-plan
```

Purpose:

```text
Move safe whole-folder plan rows.
```

This requires typing:

```text
YES
```

### Year Plan

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --year-plan
```

Purpose:

```text
Plan bucket/year/topic organization for files.
```

This is report-only.

### Apply Year Topic

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-topic
```

Purpose:

```text
Move safe categorized files into bucket/year/topic folders.
```

This requires typing:

```text
YES
```

### Apply Year Finish

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-finish
```

Purpose:

```text
Move review/collision rows into dated folders and rename collisions deterministically.
```

This requires typing:

```text
YES
```

### Apply Year Archive

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-archive
```

Purpose:

```text
Move low-value generated/raw data into archive folders.
```

This requires typing:

```text
YES
```

## Reproduction Workflow For A Future Cleanup

Use this sequence when cleaning a new folder.

### Step 1: Start With A Small Test

```bash
python -m unittest
python -m src.file_tool.main --input data/sample_files --scan
python -m src.file_tool.main --input data/sample_files --cleanup-audit
```

Expected:

```text
tests pass
sample scan works
sample cleanup audit works
```

### Step 2: Audit The Real Folder

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --audit
```

Review the generated CSV under:

```text
logs/
```

### Step 3: Run Cleanup Audit

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --cleanup-audit
```

Review counts before applying anything.

Look for:

```text
DELETE_GENERATED_CACHE
REVIEW_DEPENDENCY_FOLDER
REVIEW_EMPTY_DIR
REVIEW_PROJECT_FOLDER
REVIEW_GIT_REPO
```

### Step 4: Quarantine Generated Cache

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --delete-generated-cache
```

Type:

```text
YES
```

Then rerun:

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --cleanup-audit
```

### Step 5: Quarantine Dependency Folders

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --quarantine-dependencies
```

Type:

```text
YES
```

Then rerun cleanup audit.

### Step 6: Remove Empty Directories

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --delete-empty-dirs
```

Type:

```text
YES
```

Then rerun cleanup audit.

Repeat this step if new parent folders become empty.

### Step 7: Plan Folder Organization

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --directory-plan
```

Review the CSV before applying.

### Step 8: Apply Safe Directory Moves

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-directory-plan
```

Type:

```text
YES
```

### Step 9: Plan Year/Topic Organization

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --year-plan
```

Review the generated plan.

Important actions:

```text
NO_CHANGE
MOVE_TO_YEAR_TOPIC
REVIEW_CLASSIFY_TO_YEAR
REVIEW_YEAR_COLLISION
REVIEW_ARCHIVE_LOW_VALUE_DATA
```

### Step 10: Apply Safe Year/Topic Moves

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-topic
```

Type:

```text
YES
```

### Step 11: Finish Review/Collision Rows

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-finish
```

Type:

```text
YES
```

### Step 12: Archive Low-Value Data

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --apply-year-archive
```

Type:

```text
YES
```

### Step 13: Final Verification

Run:

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --cleanup-audit
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --year-plan
```

Good final state:

```text
DELETE_GENERATED_CACHE: 0
REVIEW_EMPTY_DIR: 0
REVIEW_DEPENDENCY_FOLDER: 0
Year plan mostly NO_CHANGE
Only known locked/system files remain
```

## GitHub Finalization Workflow

This is what was done to make the GitHub default page show the updated repo.

### Step 1: Check Branches

```bash
git status -sb
git log --oneline --decorate --graph --all -5
```

This showed that:

```text
production-upgrade had the new work
master was still older
```

### Step 2: Switch To Default Branch

```bash
git switch master
```

### Step 3: Merge The Upgrade Branch

```bash
git merge production-upgrade --no-edit
```

This was a fast-forward merge.

Meaning:

```text
master simply moved forward to the same commit as production-upgrade
```

### Step 4: Run Tests

```bash
python -m unittest
```

Expected:

```text
Ran 4 tests
OK
```

### Step 5: Push Master

```bash
git push origin master
```

### Step 6: Verify Sync

```bash
git status -sb
git log -1 --oneline --decorate
```

Expected:

```text
master...origin/master
4fec621 (HEAD -> master, origin/master, origin/production-upgrade, production-upgrade)
```

## Why `python -m unittest` Was Used

`python -m unittest` runs the automated tests.

It is a quick safety check before pushing code.

The simple engineering habit is:

```text
change code
run tests
push only if tests pass
```

## Safety Notes

Do not commit:

- real cleanup logs
- full file inventories
- quarantine folders
- private OneDrive paths
- private personal filenames
- generated CSV reports

These belong in local `logs/` or ignored `artifacts/`, not GitHub.

## Portfolio Explanation

Simple version:

```text
I built an AI-assisted Python CLI that safely audits, cleans, and organizes messy file trees. It avoids blind deletion by using reports, quarantine folders, explicit confirmations, collision handling, undo scripts, and verification passes.
```

Humble version:

```text
This was built with AI assistance, but I used it to practice practical engineering habits: safety-first automation, audit trails, test checks, Git branching, documentation, and reproducible cleanup workflows.
```

Technical version:

```text
The project demonstrates recursive filesystem scanning, report generation, classification rules, reversible cleanup workflows, collision-safe moves, protected project-folder handling, and GitHub-ready documentation.
```
