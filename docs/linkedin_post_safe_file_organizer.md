# LinkedIn Post Draft

I built a Python CLI for safely auditing and organizing large messy file trees.

The problem:
Cleaning folders by hand is risky. Bulk deletes and blind moves can cause data loss, especially in synced folders like OneDrive, Google Drive, or Dropbox.

What the tool does:

- recursively scans files and directories
- writes CSV audit reports
- classifies cleanup candidates
- quarantines generated/cache/dependency folders
- handles filename collisions
- writes undo/recovery scripts
- requires explicit confirmation before apply steps

The design goal was safety first: review before change, quarantine before delete, and evidence before action.

I validated the workflow against a real OneDrive cleanup with more than 40,000 files. The tool helped separate generated artifacts, dependency folders, project folders, and ordinary files without flattening important work.

This project helped me practice Python CLI design, filesystem automation, CSV reporting, safety-first workflows, and testable internal tooling.

Repo:
https://github.com/piemasterflex111/safe-file-organizer
