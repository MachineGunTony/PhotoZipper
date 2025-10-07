# PhotoZipper

Organize chaotic photo dumps into clean, compressed, share‑ready collections in one command.

## Why PhotoZipper?
Bulk photo exports (from cameras, editors, events, shared drives) are usually flat folders with cryptic names. Manually sorting them into people / events / shoots and then zipping each group easily burns 30–60 minutes for a medium batch.

PhotoZipper automates that workflow:
- Detects logical groups from filename patterns (via regex or plain prefixes)
- Creates one folder per group
- Copies files (with metadata preserved)
- (Optional) Deletes the originals once safely copied
- Compresses each group into a tidy ZIP
- (Optional) Removes the uncompressed folders (keep only archives)
- Gives you a clear log + success summary

Typical time savings: A 500–1000 photo session can drop from ~45 minutes of manual effort to under a minute of unattended CLI time.

## Key Features
- Pattern-based grouping (`--pattern` accepts full regex)
- Progress bars for large collections
- Per-group ZIP archives with compression
- `--zip-only` to keep only compressed artifacts
- `--delete-originals` to reclaim source disk space
- Dry run mode to preview actions (`--dry-run`)
- Unicode-safe (filenames & output)
- Merge-safe: skips duplicates if re-run into same output
- Metadata preservation via `shutil.copy2`
- Clear exit codes (0 success, 1 operation error, 2 validation error)
- Detailed log file (`photozipper.log`) in the output directory

## Installation
You can run it directly from source (editable dev install). Two common approaches are shown below: traditional virtual environment and the faster `uv` workflow.

### Option 1: Standard virtual environment (familiar & explicit)
Recommended if you are new to Python tooling or want the most widely documented approach.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### Option 2: Using `uv` (fast dependency solver & ephemeral runs)
Great for speed and avoiding manual venv management. All commands below work without pre-creating a venv.

Quick one‑off run (no permanent install):
```bash
uv run photozipper --help
uv run photozipper --source ./dump --pattern '^([^_]+)' --output ./out
```

Editable dev install (creates a managed environment under `.venv` automatically):
```bash
uv sync --all-extras --dev
uv run photozipper --help
```

Add a new dependency during development:
```bash
uv add tqdm
```

Run tests with coverage:
```bash
uv run pytest -q
```

Global tool style install (similar to pipx):
```bash
uv tool install .
photozipper --help
```

#### Which should I use?
| Goal | Prefer |
|------|--------|
| Consistent, widely-known workflow | Standard venv |
| Fast cold start / fewer steps | `uv run` |
| Multiple CLI tools isolated | `uv tool install` or `pipx` |
| CI reproducibility | Either (lock file strategy pending) |

Both approaches are fully supported; choose based on team familiarity and speed needs. For contributors already using `uv`, there is no disadvantage—tests and runtime behave the same.

Or (future) from PyPI once published:
```bash
pip install photozipper
```

Then invoke via:
```bash
photozipper --help
# or
python -m photozipper --help
```

## Basic Usage
```bash
photozipper \
  --source /photos/raw_dump \
  --pattern '^([^_]+)' \
  --output /photos/organized
```
This groups files by the leading token before the first underscore.

Example filename set:
```
person1__IMG001_FullRez.jpg
person1__IMG001_sq500px.jpg
person2__IMG777_FullRez.jpg
```
Produces:
```
/organized/
  person1/
  person1.zip
  person2/
  person2.zip
  photozipper.log
```

## Common Pattern Recipes
| Goal                          | Pattern Example            | Notes |
|-------------------------------|----------------------------|-------|
| Prefix before first underscore| `^([^_]+)`                 | Most common person prefix |
| Date like 2024-12-31          | `^(\d{4}-\d{2}-\d{2})`    | Group by ISO date |
| Camera model (e.g. X-T5_)     | `^(XT5|XT4|A7IV)`          | Alternatives | 
| Event code in square brackets | `\[(.+?)\]`               | Captures inside `[...]` |
| First two tokens              | `^([^_]+_[^_]+)`           | Combine person + session |

The first *capturing group* determines the folder/zip name.

## Safety Options
- Preview first: `--dry-run`
- Keep originals (default) or remove them: add `--delete-originals`
- Keep only zips: add `--zip-only`
- Combine? `--delete-originals --zip-only` (source removed, only archives preserved)
- Not allowed: `--dry-run` with deletion flags (prevent accidents)

## Examples
Group by date:
```bash
photozipper --source ./dump --pattern '^(\d{4}-\d{2}-\d{2})' --output ./by-date
```
Only keep ZIPs:
```bash
photozipper --source ./dump --pattern '^([^_]+)' --output ./out --zip-only
```
Archive and remove source:
```bash
photozipper --source ./session --pattern '^([^_]+)' --output ./archive --delete-originals --zip-only
```
Dry run planning:
```bash
photozipper --source ./session --pattern '^([^_]+)' --output ./archive --dry-run
```

## Exit Codes
| Code | Meaning                         |
|------|----------------------------------|
| 0    | Success                         |
| 1    | Operational error (I/O, pattern, FS) |
| 2    | Argument validation error       |

## Log File
Each run writes `photozipper.log` into the output directory. It contains:
- Start/end timestamps
- Detected groups
- Copy + zip operations
- Any skipped duplicates
- Errors (if any)

## Unicode Support
Configured to force UTF-8 on Windows consoles to avoid `charmap` errors. Filenames in multiple scripts are supported end-to-end.

## Roadmap (Potential Enhancements)
- Recursive traversal option (`--recursive`)
- Ignore patterns / glob filters
- Parallel zip creation for very large sets
- Progress bar quiet mode (`--no-progress`)
- Pluggable grouping strategies (EXIF, date taken)
- PyPI distribution & binary packaging

## Contributing
For in-depth technical onboarding see `TECHNICAL_README.md`.

Issues / ideas welcome!

## License
MIT
