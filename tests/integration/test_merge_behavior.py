"""
Integration test for merge behavior with existing folders.
Based on Scenario 4 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import zipfile


def test_merge_skips_duplicate_files(tmpdir, photozipper_cmd):
    """
    Scenario 4: Merge files into existing folder without overwriting.
    
    Setup: First run creates folder, second run tries to add files including duplicate
    Execute: Two photozipper runs with same pattern
    Expected: Duplicate skipped, new file added, original unchanged
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # First run - create initial files
    (source_dir / "merge_a.jpg").write_text("1")
    (source_dir / "merge_b.jpg").write_text("2")
    
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "merge",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify first run created files
    assert (output_dir / "merge" / "merge_a.jpg").exists()
    assert (output_dir / "merge" / "merge_b.jpg").exists()
    original_content_a = (output_dir / "merge" / "merge_a.jpg").read_text()
    
    # Modify source - add new file and change existing file
    (source_dir / "merge_c.jpg").write_text("3")
    (source_dir / "merge_a.jpg").write_text("DIFFERENT")  # Same name, different content
    
    # Second run - should merge
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "merge",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify new file added
    assert (output_dir / "merge" / "merge_c.jpg").exists()
    assert (output_dir / "merge" / "merge_c.jpg").read_text() == "3"
    
    # Verify original merge_a.jpg unchanged
    current_content_a = (output_dir / "merge" / "merge_a.jpg").read_text()
    assert current_content_a == original_content_a, "Original file should not be overwritten"
    assert current_content_a == "1", "Should still contain original content"
    
    # Verify warning about duplicate
    output = result.stdout.lower() + result.stderr.lower()
    assert "skip" in output or "duplicate" in output or "exists" in output
    
    assert result.returncode == 0


def test_merge_updates_zip_with_new_files(tmpdir, photozipper_cmd):
    """Verify zip is updated when new files are added."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # First run
    (source_dir / "data_x.jpg").write_text("x")
    
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "data",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Check initial zip
    zip_path = output_dir / "data.zip"
    with zipfile.ZipFile(zip_path, 'r') as zf:
        initial_files = zf.namelist()
        assert len(initial_files) == 1
    
    # Add new file
    (source_dir / "data_y.jpg").write_text("y")
    
    # Second run
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "data",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Check updated zip
    with zipfile.ZipFile(zip_path, 'r') as zf:
        updated_files = zf.namelist()
        # Should now contain both files
        assert len(updated_files) >= 1, "Zip should be updated with new files"
        assert any("data_y.jpg" in name for name in updated_files)


def test_merge_preserves_existing_file_count(tmpdir, photozipper_cmd):
    """Verify merge doesn't duplicate existing files."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 3 files
    (source_dir / "item_1.jpg").write_text("a")
    (source_dir / "item_2.jpg").write_text("b")
    (source_dir / "item_3.jpg").write_text("c")
    
    # First run
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "item",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    files_after_first = list((output_dir / "item").glob("*.jpg"))
    count_first = len(files_after_first)
    
    # Run again with same files (no changes)
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "item",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    files_after_second = list((output_dir / "item").glob("*.jpg"))
    count_second = len(files_after_second)
    
    # Should have same count (no duplicates)
    assert count_second == count_first == 3


def test_merge_with_empty_folder(tmpdir, photozipper_cmd):
    """Test merge behavior when output folder exists but is empty."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Pre-create empty folder
    (output_dir / "preset").mkdir()
    
    # Create source files
    (source_dir / "preset_file.jpg").write_text("data")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "preset",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Should successfully add file to existing empty folder
    assert (output_dir / "preset" / "preset_file.jpg").exists()
    assert result.returncode == 0
