# File Intake and Versioning Utility

## Problem
Manual file naming and versioning became inconsistent and hard to trace.

## Solution
This tool scans an inbox directory, normalizes filenames, computes version numbers based on existing files, and safely moves files while logging each action.

## Features
- extension filtering
- deterministic naming
- version tracking
- dry-run mode
- CSV logging
- pytest coverage

## Repo layout
- scanner
- naming
- versioning
- mover
- logger
- tests

## How to run
## How to test
## Future improvements

git init
git status
git add .
git commit -m "Initialize project structure"
git add .
git commit -m "Add scanner and extension filtering"
git add .
git commit -m "Add naming and date extraction"
git add .
git commit -m "Add versioning and dry-run pipeline"
git add .
git commit -m "Add CSV logging and tests"