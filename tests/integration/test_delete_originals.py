"""
Integration test for delete originals functionality.
Based on Scenario 6 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess


def test_delete_originals_after_successful_copy(tmpdir, photozipper_cmd):
    """
    Scenario 6: Verify --delete-originals flag safely removes source files.
    
    Setup: Files in source directory
    Execute: photozipper with --delete-originals
    Expected: Files deleted from source, exist in output and zip
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (source_dir / "delete_test1.jpg").write_text("del1")
    (source_dir / "delete_test2.jpg").write_text("del2")
    
    # Verify source files exist
    assert (source_dir / "delete_test1.jpg").exists()
    assert (source_dir / "delete_test2.jpg").exists()
    
    # Execute with --delete-originals
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "delete",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # Verify source files deleted
    assert not (source_dir / "delete_test1.jpg").exists(), "Original should be deleted"
    assert not (source_dir / "delete_test2.jpg").exists(), "Original should be deleted"
    
    # Verify copied files exist
    assert (output_dir / "delete" / "delete_test1.jpg").exists()
    assert (output_dir / "delete" / "delete_test2.jpg").exists()
    
    # Verify zip exists
    assert (output_dir / "delete.zip").exists()
    
    # Verify output mentions deletion
    output = result.stdout.lower()
    assert "delete" in output or "removed" in output
    
    assert result.returncode == 0


def test_delete_originals_preserves_content(tmpdir, photozipper_cmd):
    """Verify content is preserved after delete."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file with specific content
    test_content = "Important data that must be preserved"
    (source_dir / "important.jpg").write_text(test_content)
    
    # Execute with --delete-originals
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "important",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # Verify original deleted
    assert not (source_dir / "important.jpg").exists()
    
    # Verify copy has correct content
    copied_file = output_dir / "important" / "important.jpg"
    assert copied_file.exists()
    assert copied_file.read_text() == test_content


def test_delete_originals_reports_count(tmpdir, photozipper_cmd):
    """Verify deletion count is reported."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create multiple files
    (source_dir / "count_1.jpg").write_text("1")
    (source_dir / "count_2.jpg").write_text("2")
    (source_dir / "count_3.jpg").write_text("3")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "count",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # Output should report number of deletions
    output = result.stdout.lower()
    assert "3" in output or "three" in output.lower()


def test_delete_originals_only_matched_files(tmpdir, photozipper_cmd):
    """Verify only matched files are deleted."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create matched and unmatched files
    (source_dir / "remove_a.jpg").write_text("a")
    (source_dir / "remove_b.jpg").write_text("b")
    (source_dir / "keep_this.jpg").write_text("keep")
    
    # Execute - only delete "remove" pattern
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "remove",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # Verify matched files deleted
    assert not (source_dir / "remove_a.jpg").exists()
    assert not (source_dir / "remove_b.jpg").exists()
    
    # Verify unmatched file preserved
    assert (source_dir / "keep_this.jpg").exists(), "Non-matched files should remain"


def test_delete_originals_multiple_groups(tmpdir, photozipper_cmd):
    """Verify delete works correctly with multiple groups."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files for multiple groups
    (source_dir / "set1_a.jpg").write_text("1a")
    (source_dir / "set1_b.jpg").write_text("1b")
    (source_dir / "set2_c.jpg").write_text("2c")
    (source_dir / "set2_d.jpg").write_text("2d")
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"set\d",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True
    )
    
    # All matched files should be deleted
    assert not (source_dir / "set1_a.jpg").exists()
    assert not (source_dir / "set1_b.jpg").exists()
    assert not (source_dir / "set2_c.jpg").exists()
    assert not (source_dir / "set2_d.jpg").exists()
    
    # All files should exist in output
    assert (output_dir / "set1" / "set1_a.jpg").exists()
    assert (output_dir / "set1" / "set1_b.jpg").exists()
    assert (output_dir / "set2" / "set2_c.jpg").exists()
    assert (output_dir / "set2" / "set2_d.jpg").exists()


def test_delete_originals_without_flag_preserves_files(tmpdir, photozipper_cmd):
    """Verify files are NOT deleted without --delete-originals flag."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "keep_me.jpg").write_text("data")
    
    # Execute WITHOUT --delete-originals
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "keep",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Original should still exist
    assert (source_dir / "keep_me.jpg").exists(), "Files should be preserved by default"
    
    # Copy should also exist
    assert (output_dir / "keep" / "keep_me.jpg").exists()
