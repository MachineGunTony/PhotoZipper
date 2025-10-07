"""
Integration test for dry-run mode.
Based on Scenario 3 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess


def test_dry_run_no_modifications(tmpdir, photozipper_cmd):
    """
    Scenario 3: Preview operations without executing them.
    
    Setup: Files with test_ prefix
    Execute: photozipper --source ./source --pattern "test_" --output ./output --dry-run
    Expected: Shows operations but doesn't create files/folders
    """
    # Setup
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (source_dir / "test_file1.jpg").write_text("x")
    (source_dir / "test_file2.jpg").write_text("y")
    
    # Count files in output before
    files_before = list(output_dir.iterdir())
    count_before = len(files_before)
    
    # Execute with --dry-run
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "test_",
            "--output", str(output_dir),
            "--dry-run"
        ],
        capture_output=True,
        text=True
    )
    
    # Verify dry-run marker in output
    assert "[DRY RUN]" in result.stdout or "dry run" in result.stdout.lower()
    
    # Count files in output after (excluding log file which is always created)
    files_after = [f for f in output_dir.iterdir() if f.name != "photozipper.log"]
    count_after = len(files_after)
    
    # Verify no new files created (log file is expected)
    assert count_after == count_before, "Dry-run should not create any files except log"
    
    # Verify no folder created
    assert not (output_dir / "test_").exists()
    
    # Verify no zip created
    zip_files = list(output_dir.glob("*.zip"))
    assert len(zip_files) == 0, "Dry-run should not create zip files"
    
    # Verify exit code
    assert result.returncode == 0


def test_dry_run_shows_operations(tmpdir, photozipper_cmd):
    """Verify dry-run shows what would be done."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "demo_a.jpg").write_text("1")
    (source_dir / "demo_b.jpg").write_text("2")
    
    # Execute dry-run
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "demo",
            "--output", str(output_dir),
            "--dry-run"
        ],
        capture_output=True,
        text=True
    )
    
    output = result.stdout.lower()
    
    # Should mention what would be created
    assert "demo" in output, "Should mention the group name"
    assert "would" in output or "dry run" in output, "Should indicate simulation"


def test_dry_run_with_multiple_groups(tmpdir, photozipper_cmd):
    """Verify dry-run with multiple groups doesn't create anything."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files for multiple groups
    (source_dir / "cat1_a.jpg").write_text("1")
    (source_dir / "cat2_b.jpg").write_text("2")
    (source_dir / "cat3_c.jpg").write_text("3")
    
    count_before = len([f for f in output_dir.iterdir() if f.name != "photozipper.log"])
    
    # Execute dry-run
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"cat\d",
            "--output", str(output_dir),
            "--dry-run"
        ],
        capture_output=True,
        text=True
    )
    
    count_after = len([f for f in output_dir.iterdir() if f.name != "photozipper.log"])
    
    # No folders or zips should be created (log file is expected)
    assert count_after == count_before
    assert not (output_dir / "cat1").exists()
    assert not (output_dir / "cat2").exists()
    assert not (output_dir / "cat3").exists()
    
    assert result.returncode == 0


def test_dry_run_with_delete_flag_error(tmpdir, photozipper_cmd):
    """Verify dry-run with --delete-originals is rejected."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    # Execute with conflicting flags
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--dry-run",
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # Should error (can't combine dry-run with delete)
    assert result.returncode != 0, "Should reject incompatible flags"
    error_output = result.stderr.lower()
    assert "error" in error_output or "conflict" in error_output
