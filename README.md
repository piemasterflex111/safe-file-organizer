# File Intake / Versioning Tool

A Python tool for recursively scanning directories, previewing safe filename normalization, and detecting rename collisions before applying filesystem changes.

## Project background

This project started as a personal filesystem cleanup problem and is being developed into a safer Python tool for recursive file discovery, normalization preview, and structured file-organization workflows.

The current public focus is:
- recursive scanning
- extension filtering
- filename normalization
- rename preview
- collision detection
- summary reporting

## Problem

Large personal directories had become cluttered and inconsistent over time, especially in storage areas like OneDrive. Filenames, duplicates, and folder organization were difficult to review and clean up safely by hand.

## Current status

The active public workflow is:

`scan -> filter -> normalize -> rename preview`

The repository also includes early classification and move-planning modules for a later phase of the project, but those are not yet the primary CLI workflow.

## Current features

- recursive directory scanning
- extension filtering
- filename normalization
- safe rename preview
- collision detection
- summary reporting
- configurable input path via `--input`

## Project structure

- `data/sample_input/` - sample files for safe local runs
- `docs/` - build logs and project notes
- `src/file_tool/config.py` - default paths and allowed extensions
- `src/file_tool/scanner.py` - recursive scan logic
- `src/file_tool/normalize.py` - filename normalization rules
- `src/file_tool/renamer.py` - rename preview / apply logic
- `src/file_tool/classifier.py` - early classification logic for future organization work
- `src/file_tool/categories.py` - category and destination mappings
- `src/file_tool/plan_moves.py` - early move-planning logic
- `src/file_tool/main.py` - current command-line entry point
- `tests/` - test area, currently in progress

## Setup

- Python 3.11+ recommended
- No external runtime dependencies are currently required for the main CLI flow
- Optional: create and activate a virtual environment before running the tool

## How to run

From the repo root:

```bash
python -m src.file_tool.main
```

To scan a custom directory:

```bash
python -m src.file_tool.main --input "/path/to/folder"
```

Windows example:

```bash
python -m src.file_tool.main --input "C:\path\to\folder"
```

## Example summary from a real run

```text
Accepted files: 20927
Scan skips: 21086
Rename preview count: 89
Rename skips: 20838
```

## Safety behavior

- rename preview is used before applying changes
- collisions are skipped instead of overwriting files
- current runs use preview mode and do not apply bulk renames

## Current limitations

- no directory audit CSV export yet
- no published automated test coverage yet
- classification and move planning are not part of the main CLI flow
- bulk apply mode is intentionally limited until the audit/export layer is in place

## Next milestone

Generate a directory audit CSV with one row per file, including metadata such as:

- full path
- parent folder
- filename
- extension
- size
- modified time
