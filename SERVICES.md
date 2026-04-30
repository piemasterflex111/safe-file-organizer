# Safe File Audit and Cleanup Automation

This repo demonstrates the kind of Python automation I can build for messy real-world file systems and operational folders.

## Problem This Solves

Many individuals and small teams have large synced folders, shared drives, or project directories that become risky to clean by hand:

- thousands of files across nested folders
- generated cache and dependency folders mixed with real work
- duplicate or collision-prone filenames
- project folders that should not be flattened
- unclear cleanup candidates
- fear of deleting something important

The goal is not blind deletion. The goal is a reviewable, evidence-driven cleanup workflow.

## Example Service Workflow

1. Scan a target folder tree.
2. Produce a CSV audit of files and directories.
3. Classify cleanup candidates.
4. Identify generated cache, dependency environments, Git repos, project folders, empty folders, and ordinary files.
5. Produce a safe cleanup plan.
6. Quarantine low-risk generated/dependency folders instead of permanently deleting them.
7. Generate undo or recreate scripts where appropriate.
8. Verify final state with repeatable reports.

## Example Deliverables

- full file and directory audit CSV
- cleanup candidate report
- generated-cache report
- dependency-environment report
- collision and review report
- directory move plan
- quarantine folder output
- undo/recovery script
- short summary of what was changed and what was intentionally left unresolved

## Who This Helps

- individuals with messy OneDrive, Dropbox, Google Drive, or Downloads folders
- small businesses with shared drives
- creators with mixed media/project folders
- engineering or operations teams with generated files mixed into project data
- anyone who needs cleanup evidence before making changes

## Safety Principles

- report before apply
- quarantine before delete
- skip collisions instead of overwriting
- preserve project folders and Git metadata
- require explicit confirmation for apply workflows
- leave unresolved or locked files visible instead of hiding them

## What This Repo Proves

This project is a working example of safety-first Python automation:

- CLI design
- recursive filesystem scanning
- CSV reporting
- classification logic
- safe move planning
- undo/recovery workflow design
- real-world validation against a 40,000+ file cleanup

## Possible Paid Project Shapes

Small audit:

- run a scan
- produce CSV reports
- identify risk areas
- no file changes

Cleanup plan:

- audit plus categorized cleanup plan
- collision/review reports
- recommended next actions

Assisted cleanup automation:

- audit
- quarantine generated/dependency folders
- apply approved safe moves
- produce verification report

Custom internal tool:

- adapt this workflow to a team-specific folder structure, naming convention, or reporting requirement
