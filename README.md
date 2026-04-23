# Safe File Organizer

A conservative Python CLI for auditing, planning, and safely organizing large local file trees such as synced cloud-drive folders.

The tool was built around one practical constraint: cleanup should be reviewable before it changes data. It favors CSV reports, explicit confirmations, quarantine folders, and undo scripts over blind deletion.

## What It Does

- recursively scans files and directories
- writes full path audits to CSV
- classifies generated cache, dependency environments, Git repos, projects, build output, empty folders, and ordinary files
- quarantines generated cache and dependency folders instead of permanently deleting them
- removes only directories that are empty at deletion time
- builds top-level directory move plans
- builds bucket/year/topic organization plans
- applies safe moves with collision checks and undo scripts
- keeps detected project folders from being flattened into document buckets

## Validated Use Case

The current workflow was validated against a real OneDrive cleanup with more than 40,000 files. The final verification pass showed no generated-cache candidates and no removable empty-directory candidates remaining. One locked OneDrive system metadata file was intentionally left unresolved.

See [CASE_STUDY.md](CASE_STUDY.md) for a sanitized write-up.

## Safety Model

- `--audit`, `--cleanup-audit`, `--directory-plan`, `--year-plan`, and `--remaining-work` are report-only.
- generated cache and dependency cleanup moves candidates into `logs/*_quarantine_*`.
- empty-folder cleanup writes a recreate script.
- move operations skip existing destinations unless a finish pass explicitly renames collisions.
- project folders and Git metadata are classified separately from ordinary personal files.
- every apply workflow requires typing `YES`.

## Setup

Python 3.11+ is recommended. The CLI has no required third-party runtime dependencies.

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m unittest
```

## Running The Tool

Use a small sample or test directory first:

```bash
python -m src.file_tool.main --input data/sample_files --scan
python -m src.file_tool.main --input data/sample_files --audit
python -m src.file_tool.main --input data/sample_files --cleanup-audit
```

Run against a real folder explicitly:

```bash
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --cleanup-audit
python -m src.file_tool.main --input "C:\Users\you\OneDrive" --year-plan
```

Optional environment override for the default OneDrive root:

```powershell
$env:FILE_TOOL_ONEDRIVE_ROOT = "C:\Users\you\OneDrive"
```

## Main Commands

```text
--scan                    scan files and print counts
--audit                   write a full file/directory audit CSV
--cleanup-audit           classify cleanup candidates without changing files
--delete-generated-cache  quarantine generated cache candidates
--quarantine-dependencies quarantine dependency environments
--delete-empty-dirs       remove directories still empty at deletion time
--directory-plan          plan top-level folder moves
--apply-directory-plan    apply safe whole-folder moves
--year-plan               plan bucket/year/topic organization
--apply-year-archive      move low-value generated/raw data into archive folders
--apply-year-topic        move safe categorized files into year/topic folders
--apply-year-finish       move review/collision rows with deterministic renames
--remaining-work          write reports for unresolved move-plan rows
```

## Repository Layout

```text
src/file_tool/
  audit.py              full path inventory
  cleanup.py            cache/dependency/empty-folder classification and cleanup
  classifier.py         keyword-based bucket routing
  directory_planner.py  top-level folder planning
  main.py               CLI entry point
  mover.py              safe move-plan apply workflow
  normalize.py          filename normalization
  planner.py            legacy bucket move planner
  review.py             unresolved collision/review reports
  scanner.py            recursive scanning
  year_planner.py       bucket/year/topic planning and apply workflows
tests/
  test_core_workflows.py
```

## Portfolio Note

This is an AI-assisted engineering project. The value is in the safety-first workflow design, verification loop, and practical handling of messy real-world filesystem state: locks, collisions, generated artifacts, dependency trees, empty parent cascades, and project folders that should not be flattened.
