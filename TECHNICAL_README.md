# PhotoZipper Technical README

This document is for contributors and maintainers. It explains architecture, design decisions, code layout, and contribution workflow so you can become productive quickly.

## 1. High-Level Architecture
```
+-------------------+        +------------------+        +------------------+
|      CLI          | -----> |  Pattern Matcher | -----> |   Group Model    |
| (argparse + flow) |        | (regex grouping) |        | (in-memory sets) |
+-------------------+        +------------------+        +------------------+
        |                               |                           |
        v                               v                           v
+-------------------+        +------------------+        +------------------+
|  File Organizer   | -----> |   Zip Creator    | -----> |  Logging System  |
| (copy / merge /   |        | (per-group .zip) |        |  (file + console)|
| verify / delete)  |        +------------------+        +------------------+
+-------------------+
```

### Execution Flow
1. Parse + validate CLI args (compatibility only → validation errors = exit 2).
2. Filesystem / pattern validation happens in main (operational errors = exit 1).
3. Scan source directory, apply regex/pattern extraction → produce `Group` objects.
4. For each group:
   - Create target folder (unless dry run)
   - Copy files (metadata preserved) + verify size match
   - Optionally delete source originals (`--delete-originals`)
   - Create ZIP archive
   - Optionally remove group folder (`--zip-only`)
5. Print summary + write log + return exit code.

### Exit Code Semantics
| Code | Meaning | Source of Failure |
|------|---------|------------------|
| 0 | Success | Completed full flow |
| 1 | Operational error | FS errors, invalid pattern, copy failure, zip error |
| 2 | Validation error | Incompatible flags at argument level |

## 2. Repository Layout
```
photozipper/
  cli.py              # CLI entry, orchestration, argument parsing
  file_organizer.py   # Copy, verify, delete, merge logic
  pattern_matcher.py  # Regex validation, scan + group building
  zip_creator.py      # ZIP archive creation
  logger.py           # Central logging setup
  models.py           # Data structures (Group, FileEntry, etc.)

tests/
  unit/               # Pure function + small surface tests
  integration/        # End-to-end CLI subprocess tests
  contract/           # CLI surface + exit code behavior
specs/                # (Optional) design / spec artifacts
pyproject.toml        # Build + dependency config
```

## 3. Key Modules
### `cli.py`
- Owns: argument parsing, high-level control flow, progress bars (`tqdm`), exit code policy.
- Windows UTF-8 handling: wraps `sys.stdout` / `stderr` to avoid encoding failures.
- Contains `validate_arguments()` (only flag compatibility, not side effects).

### `pattern_matcher.py`
- `validate_pattern(pattern: str) -> bool` (raises on bad regex)
- `extract_group(filename: str, pattern: str) -> Optional[str]`
- `scan_and_group(source_dir: Path, pattern: str) -> list[Group]`

### `file_organizer.py`
- `copy_file_with_metadata(src, dst)` returns `True/False` (never raises for expected errors)
- `verify_copy(src, dst)` size comparison
- `handle_merge(target_path)` decides whether to keep or skip if already exists
- `delete_original(path)` best-effort remove (returns bool)

### `zip_creator.py`
- `create_zip(folder: Path, zip_path: Path)` – always recreates ZIP state.
- Compression: `ZIP_DEFLATED`

### `logger.py`
- One logger per run, file + console handlers.
- Log file always named `photozipper.log` in output directory.

### `models.py`
- `Group`: name + list of `FileEntry`
- `FileEntry`: `path`, derived properties
- `OperationResult`, `FileOperation` (reserved for future richer reporting)

## 4. Adding Features – Design Guidelines
| Concern | Guideline |
|---------|-----------|
| New flags | Validate compatibility in `validate_arguments` only |
| Side-effect boundaries | All filesystem ops in `file_organizer` or new dedicated module |
| Pattern semantics | Preserve: *first capturing group defines folder/zip name* |
| Error handling | Return booleans from low-level ops; escalate/log in CLI |
| Logging | Use existing logger; do not print directly except final summary |
| Progress | Keep `tqdm` usage optional-friendly (disable in dry run) |
| Unicode | Avoid assumptions about filesystem encoding; rely on Python 3.11+ behavior |

## 5. Testing Strategy
### Layers
- Unit: Behavior of discrete functions (fast, no subprocess)
- Integration: Real filesystem with temp dirs (`tmp_path`), subprocess invocation of CLI
- Contract: CLI semantics (flags, required args, exit codes)

### Coverage Notes
- `cli.py` line coverage appears low due to subprocess + progress output; logic is tested behaviorally.
- No mocking for `pathlib.Path.iterdir()` in integration tests—real files used to avoid brittle mocks.

### Adding Tests
1. Favor realistic temp filesystem over heavy mocking (reduces false positives).
2. If adding CLI flags, create:
   - Contract test for help + validation
   - Integration test exercising the new flow
3. For performance scenarios, mark with `@pytest.mark.skip` if >5s locally.

## 6. Contributing Workflow
1. Fork / branch (`feature/<short-description>`)
2. Create or update spec in `specs/` if feature is non-trivial
3. Add/adjust tests FIRST (TDD preferred)
4. Implement feature (small, focused commits)
5. Run full suite:
   ```bash
   pytest -q
   ```
6. Update `README.md` (user-facing) + `TECHNICAL_README.md` if architecture impacts
7. Bump version in `pyproject.toml` if releasing (follow semver)
8. Open PR with:
   - Summary
   - Motivation / problem statement
   - Before/after examples
   - Test evidence

### Commit Message Conventions
Format: `<type>: <summary>`
Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.

Examples:
- `feat: add --zip-only flag to remove extracted folders`
- `fix: correct exit code on invalid pattern`

## 7. Error Handling Philosophy
- Avoid raising in deep file operations unless truly unexpected (corruption / program bug)
- Collect context (filenames, sizes) in logs
- Fail fast on verification mismatch (integrity is more important than continuing silently)

## 8. Performance Characteristics
| Factor | Current Behavior |
|--------|------------------|
| Copy speed | Single-threaded, dominated by disk I/O |
| ZIP creation | Sequential per group |
| Large sets (1000 files) | Tested (skipped for runtime in CI) |
| Memory usage | Only holds lightweight `FileEntry` metadata |

### Potential Performance Enhancements
- Threaded copy pipeline (careful with GIL vs I/O bound nature)
- Parallel ZIP creation using `concurrent.futures`
- Streaming log flushes for very large runs

## 9. Windows-Specific Notes
- UTF-8 wrapping of stdio in CLI to survive CP1252 consoles
- Paths use `pathlib` (safe for mixed separators)
- Avoid reserved names (no direct creation of `CON`, `PRN`, etc.)

## 10. Adding a New Grouping Strategy (Example Playbook)
Suppose you want EXIF date grouping:
1. Dependency: add optional `exifread` under `[project.optional-dependencies]`.
2. New module: `exif_grouping.py` with `extract_date_taken(path: Path) -> Optional[str]`.
3. Add flag `--group-by exif-date` (mutually exclusive with `--pattern`).
4. Refactor `scan_and_group` to delegate to a strategy selected at runtime.
5. Tests:
   - Unit for date extraction (mock EXIF)
   - Integration for mixed files (some missing EXIF)

## 11. Logging Conventions
| Level | Used For |
|-------|----------|
| DEBUG | Fine-grained operations (copy success, verification) |
| INFO  | High-level phase messages, group boundaries, summary |
| WARNING | Non-fatal anomalies (no matches) |
| ERROR | Operation abort causes |

## 12. Security / Safety Considerations
- No network access; purely local filesystem manipulations.
- Avoid shelling out—everything is Python standard library.
- User-provided regex compiled in a try/except block.
- Potential future hardening: path traversal guards if supporting input manifests.

## 13. Release Process
1. Ensure `main` green (CI passing + manual large set sanity run)
2. Update `CHANGELOG.md` (add if missing)
3. Bump version in `pyproject.toml`
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Build & publish (future):
   ```bash
   python -m build
   twine upload dist/*
   ```

## 14. Known Gaps / TODO Seeds
- Lack of quiet mode (`--quiet` to suppress progress)
- Potential race on re-running while zips exist (currently replaced)
- No checksum verification (size-only integrity check)
- Coverage for CLI control flow (behavioral only via subprocess tests)

## 15. Quick Start for Contributors
```bash
git clone <fork-url>
cd PhotoZipper
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .[dev]
pytest -q
python -m photozipper --source ./example --pattern '^([^_]+)' --output ./out
```

## 16. Contact / Support
Open an issue or start a discussion in the repository. PRs welcome.

---
Happy automating! 🚀
