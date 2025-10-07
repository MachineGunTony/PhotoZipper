"""
Integration test for no matches scenario.
Based on Scenario 7 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess


def test_no_matches_graceful_handling(tmpdir, photozipper_cmd):
    """
    Scenario 7: Handle gracefully when pattern matches no files.
    
    Setup: Files that don't match the pattern
    Execute: photozipper with non-matching pattern
    Expected: No folders/zips created, success exit code, informative message
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files that won't match pattern
    (source_dir / "unmatched1.jpg").write_text("x")
    (source_dir / "unmatched2.jpg").write_text("y")
    
    # Count output files before
    count_before = len(list(output_dir.iterdir()))
    
    # Execute with pattern that doesn't match
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "nomatch",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify informative message
    output = result.stdout.lower()
    assert "no" in output or "match" in output or "found" in output
    
    # Verify no folders created
    assert not (output_dir / "nomatch").exists()
    
    # Verify no zip files created
    zip_files = list(output_dir.glob("*.zip"))
    assert len(zip_files) == 0
    
    # Verify no new files in output (except possibly log)
    count_after = len(list(output_dir.iterdir()))
    # Allow for log file
    assert count_after <= count_before + 1
    
    # Should exit successfully (no error, just no matches)
    assert result.returncode == 0


def test_no_matches_empty_source_directory(tmpdir, photozipper_cmd):
    """Test behavior when source directory is empty."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Source is empty - no files created
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "anything",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Should handle gracefully
    assert result.returncode == 0
    
    # No folders created
    folders = [d for d in output_dir.iterdir() if d.is_dir()]
    assert len(folders) == 0


def test_no_matches_with_specific_pattern(tmpdir, photozipper_cmd):
    """Test no matches with complex regex pattern."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files
    (source_dir / "photo123.jpg").write_text("a")
    (source_dir / "image456.jpg").write_text("b")
    
    # Pattern that won't match anything
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"trip\d{4}",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # No trip folders created
    assert not any("trip" in d.name for d in output_dir.iterdir() if d.is_dir())
    
    assert result.returncode == 0


def test_no_matches_log_file_still_created(tmpdir, photozipper_cmd):
    """Verify log file is created even when no matches."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    # Execute with non-matching pattern
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "nomatch",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Log file should exist
    log_file = output_dir / "photozipper.log"
    assert log_file.exists(), "Log file should be created even with no matches"
    
    # Log should mention no matches
    log_content = log_file.read_text().lower()
    assert "no" in log_content or "match" in log_content or "found" in log_content


def test_no_matches_different_file_extensions(tmpdir, photozipper_cmd):
    """Test no matches when files have different extensions."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files with various extensions
    (source_dir / "photo_test.txt").write_text("a")
    (source_dir / "photo_test.doc").write_text("b")
    (source_dir / "photo_test.pdf").write_text("c")
    
    # Look for jpg files
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"photo.*\.jpg",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # No matches because wrong extension
    assert not (output_dir / "photo").exists()
    assert result.returncode == 0
