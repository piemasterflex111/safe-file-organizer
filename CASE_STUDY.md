# Case Study: Safe Cleanup of a Large Personal File Tree

## Summary

This project was validated against a real OneDrive cleanup with tens of thousands of files. The goal was not to blindly delete clutter. The tool produced audit reports, move plans, quarantine folders, and undo scripts so each cleanup step could be reviewed and reversed where practical.

## Problem

The source tree contained years of mixed personal documents, career materials, engineering projects, media, duplicate snapshots, generated cache, dependency environments, and empty directory residue. Manual cleanup was risky because the same tree included both high-value documents and low-value generated artifacts.

## Approach

- Build read-only audits before applying moves.
- Classify generated cache, dependency environments, Git repositories, project folders, ordinary files, and empty folders separately.
- Move risky cleanup candidates to quarantine instead of permanently deleting them.
- Preserve project folders as units instead of flattening source trees.
- Use dated bucket/topic destinations for personal files.
- Write CSV reports and undo PowerShell scripts for applied moves.
- Iterate after each pass because moving files can expose newly empty parent folders.

## Result

The validated workflow organized the file tree into stable category/year/topic folders, moved dependency and cache artifacts out of the synced directory, removed empty-folder residue, and left only intentionally protected structural folders plus locked OneDrive system metadata.

Representative final checks:

- no generated-cache candidates remained
- no removable empty-directory candidates remained
- dependency folders were removed from the synced tree
- project folders and Git metadata were detected instead of flattened
- one locked OneDrive system file remained intentionally unresolved

## Engineering Notes

This was developed as an AI-assisted engineering workflow. The important engineering decisions were the safety model, audit-first design, quarantine strategy, collision handling, and verification loop. The implementation is intentionally conservative because filesystem cleanup can destroy valuable data if it is treated as a simple delete script.
