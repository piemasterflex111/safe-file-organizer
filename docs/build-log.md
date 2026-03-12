# Build Log

## 2026-03-12 Session 1
### Goal
Build scanner + extension filter

### What I wrote
- Added `list_files`
- Added extension allowlist

### What broke
- Forgot `.lower()` on suffix

### Why it broke
- `.ZIP` did not match `.zip`

### Fix
- Normalized suffix with `.lower()`

### What I learned
- Set membership is clean for extension filtering
- Path objects expose suffix directly

### Next step
- Build `slugify`


### python commands

python -m venv /path/to/new/virtual/environment
	
$ <venv>/bin/Activate.ps1