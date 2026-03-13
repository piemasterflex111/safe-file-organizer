
# Build Log

## Date
2026-03-12

## Session Focus
Set up Python project environment, initialize Git, and start Stage 1 scanner logic for the file-intake/versioning project.

---

## What I worked on
- Created the repo structure for `file-intake-versioning-tool`
- Set up a repo-local virtual environment `.venv`
- Fixed Git config and made the first commits
- Created `config.py`
- Started building the scanner logic
- Practiced a toy version of accepted vs skipped classification before tying it to the real folder path
- Started learning how to inspect real directory items and choose methods based on the object type

---

## What I struggled with

### 1. Python environment confusion
I mixed up:
- the Python interpreter
- the `python` command in PowerShell
- the `py` launcher
- the VS Code interpreter picker

I did not understand that:
- VS Code can detect a Python interpreter even when PowerShell cannot run `python`
- a base interpreter is different from the repo `.venv` interpreter
- the project should ultimately use `.venv\Scripts\python.exe`

### 2. PATH vs actual interpreter confusion
I thought “Python not found” meant Python was not installed at all.

What was actually happening:
- the shell command `python` was not wired correctly
- the `py` launcher also did not know about the runtime
- the interpreter still existed on disk and could be used directly by full path

### 3. Confusing config, input data, and current loop item
I kept mixing up:
- config constants
- the folder path being scanned
- the items inside the folder
- the allowed extensions set

I was not keeping these concepts separate enough.

### 4. Using the wrong mental model for the scanner
I kept drifting into:
- counting problems
- nested loops
- comparing the wrong objects
- returning too early

I reused patterns like:
- `counts.get(..., 0) + 1`
even though the scanner problem is not a counting problem.

### 5. Comparing the wrong things
I repeatedly compared:
- the whole file to the extension set
- the accepted list to the extension set
- items to `True`
- items to `str`

Instead of comparing:
- the current file’s suffix
to
- `ALLOWED_EXTENSIONS`

### 6. Not knowing how to detect whether something is a file
I got stuck because I did not know the method name ahead of time and felt like I was supposed to magically know it.

### 7. Returning too early
I kept putting `return` inside the loop, which stopped the scan after the first item.

### 8. Data shape confusion
I kept creating the wrong shapes, like:
- a list containing a set
- global lists instead of local lists
- skipped items with no reason
- nested loops over copied containers

### 9. Toy version vs real version confusion
I mixed up:
- toy version: list of extension strings
- real version: directory path and real filesystem items

I needed to understand that the logic pattern is similar, but the current item is different.

### 10. Method discovery frustration
I did not know how to choose the right method and felt blocked because I was trying to remember APIs instead of discovering them from the object.

---

## What I learned

### 1. Base interpreter vs project interpreter
I learned:
- the base interpreter is used to create the venv
- the repo `.venv` interpreter is the one I should use for daily work
- once the venv is activated, `python` should point to `.venv\Scripts\python.exe`

### 2. The working venv flow
For a new repo:
- create `.venv` from a real base interpreter path

For an existing repo:
- activate `.venv`
- confirm `python` resolves to the repo-local interpreter

### 3. Config file purpose
`config.py` should hold only fixed project settings for this stage:
- inbox directory path
- allowed extensions

It should not contain scanner logic.

### 4. The right object model for Stage 1
Real scanner version:
- `INBOX_DIR` = one folder path
- loop item = one directory item/path object
- first check = file or not-file
- second check = suffix allowed or not

### 5. The toy version logic
Toy version:
- input is a list of extension strings
- loop over each string
- check membership in `ALLOWED_EXTENSIONS`
- append to accepted or skipped
- return both lists after the loop

This helped me isolate the logic before tying it to the real filesystem.

### 6. The real scanner logic order
Correct order:
1. iterate over directory contents
2. check if current item is a file
3. if not a file, skip it
4. if it is a file, inspect suffix
5. compare suffix to `ALLOWED_EXTENSIONS`
6. append to accepted or skipped
7. return results after the loop

### 7. Sets are for membership, not indexing
I learned:
- sets do not have indexes
- sets are for membership checks and uniqueness
- lists are for ordered collections and buckets
- dicts are for named fields or counts

### 8. `in` solves membership, not file detection
I learned that:
- `in` is for asking whether something belongs to a collection
- it does not tell me whether something is a file
- file detection is a separate question from extension membership

### 9. Method selection process
When I do not know the method:
1. identify the object type
2. identify the question I need answered
3. type `object.`
4. use autocomplete to discover the method

This is how I should have found methods like:
- `iterdir()`
- `is_file()`
- `suffix`

### 10. `iterdir()` mental model
I learned:
- the folder path is not the same as its contents
- I need the directory-contents method to get each item inside the folder
- I should not slice the path or loop over the path string itself

### 11. Return placement
I learned that if I return inside the loop, I kill the scan early.
For a classifier, return should usually happen after the loop is complete.

### 12. Better naming matters
I learned that names like:
- `files`
- `container`
- `test`
can blur what the current item really is

Better naming reduces confusion.

---

## Concrete wins from today
- Created and activated `.venv`
- Verified `python` resolves to the repo-local interpreter
- Initialized Git and made the first commits
- Fixed repo layout
- Built a correct toy classifier version with:
  - input parameter
  - accepted list
  - skipped list
  - one loop
  - one membership check
  - return at the end
- Reached the real scanner stage and understood the next required check is:
  - current item is a file or not

---

## Key mental models I should remember

### Model 1
Object → question → method

### Model 2
Set = membership  
List = ordered buckets  
Dict = named fields or counts

### Model 3
Toy version:
- compare current extension string to allowed set

Real version:
- compare current file’s suffix to allowed set

### Model 4
Real scanner order:
- directory contents
- file check
- suffix check
- accepted/skipped classification

---

## Mistakes I should avoid next session
- do not use mutable default arguments like `test=[]`
- do not compare items to `True` or `str`
- do not use nested loops unless I can explain why both are needed
- do not return inside the loop for a full-folder scan
- do not compare the wrong data shapes
- do not guess methods blindly; use autocomplete on the object
- do not collapse too much logic into one line before I understand the steps

---

## Next step for the project
Finish Stage 1 properly:

- import `INBOX_DIR` and `ALLOWED_EXTENSIONS`
- loop over `INBOX_DIR` contents
- first check whether each current item is a file
- skip non-files with reason
- then inspect suffix
- compare suffix to `ALLOWED_EXTENSIONS`
- build accepted and skipped results
- return both

---

## One-sentence takeaway
Today I learned that my main blocker is not syntax; it is keeping the data shape, object type, and question separate so I can choose the right operation instead of guessing.


### python commands

python -m venv /path/to/new/virtual/environment
	
$ <venv>/bin/Activate.ps1

Set-Alias pybase "$HOME\.local\bin\python3.14.exe"

& "$HOME\.local\bin\python3.14.exe" -m venv .venv
.venv\Scripts\Activate.ps1


python -m pip install pytest

python -m pip install pytest
mkdir src, tests, docs, data


## git commands
Initialize repo
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