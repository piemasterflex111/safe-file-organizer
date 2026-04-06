# File Intake / Versioning Tool

A Python tool for recursively scanning directories, previewing safe filename normalization, and detecting rename collisions before applying filesystem changes.

## Problem

My personal file storage had become cluttered and inconsistent, especially across large directories like OneDrive. Filenames, duplicates, and folder structure were difficult to manage safely by hand.

## Current solution

This project currently:
- recursively scans a target directory
- filters accepted vs skipped files by extension
- normalizes filenames in preview mode
- detects target-name collisions before renaming
- prints summary counts for large directory runs
- allows a custom input directory through a CLI argument

## Current features

- recursive directory scanning
- extension filtering
- filename normalization
- safe rename preview
- collision detection
- summary reporting
- configurable input path via `--input`

## Current repo layout

- `src/file_tool/config.py` - default paths and allowed extensions
- `src/file_tool/scanner.py` - recursive scan logic
- `src/file_tool/normalize.py` - filename normalization rules
- `src/file_tool/renamer.py` - rename preview / apply logic
- `src/file_tool/main.py` - command-line entry point

## How to run

From the repo root:

    python -m src.file_tool.main

To scan a custom directory:

    python -m src.file_tool.main --input "C:\Users\payam_vngz\OneDrive"

## Example summary from a real run

- Accepted files: 20927
- Scan skips: 21086
- Rename preview count: 89
- Rename skips: 20838

## Safety behavior

- rename preview is used before applying changes
- collisions are skipped instead of overwriting files
- current runs use preview mode and do not apply bulk renames

## Next milestone

Generate a directory audit CSV with one row per file, including metadata such as:

- full path
- parent folder
- filename
- extension
- size
- modified time