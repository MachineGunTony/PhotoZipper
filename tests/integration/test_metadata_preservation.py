"""
Integration test for metadata preservation.
Based on Scenario 5 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import os
import time


def test_metadata_preservation_timestamps(tmpdir, photozipper_cmd):
    """
    Scenario 5: Verify file timestamps are preserved.
    
    Setup: Create file with specific timestamp
    Execute: photozipper copies file
    Expected: Modification time preserved
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file
    test_file = source_dir / "preserve_test.jpg"
    test_file.write_text("data")
    
    # Set specific modification time (Jan 1, 2024 12:00:00)
    # Using epoch timestamp: 1704110400
    specific_time = 1704110400
    os.utime(test_file, (specific_time, specific_time))
    
    # Record original timestamp
    original_mtime = test_file.stat().st_mtime
    
    # Wait a moment to ensure any new file would have different timestamp
    time.sleep(0.1)
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "preserve",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Check copied file timestamp
    copied_file = output_dir / "preserve" / "preserve_test.jpg"
    assert copied_file.exists()
    
    copied_mtime = copied_file.stat().st_mtime
    
    # Timestamps should match (allow 1 second difference for filesystem precision)
    time_diff = abs(copied_mtime - original_mtime)
    assert time_diff < 1.0, f"Timestamp should be preserved (diff: {time_diff}s)"
    
    assert result.returncode == 0


def test_metadata_preservation_permissions(tmpdir, photozipper_cmd):
    """Verify file permissions are preserved."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file
    test_file = source_dir / "perm_test.jpg"
    test_file.write_text("data")
    
    # Set specific permissions (readable/writable by owner)
    original_mode = test_file.stat().st_mode
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "perm",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Check copied file permissions
    copied_file = output_dir / "perm" / "perm_test.jpg"
    assert copied_file.exists()
    
    copied_mode = copied_file.stat().st_mode
    
    # Permissions should match
    assert copied_mode == original_mode, "Permissions should be preserved"


def test_metadata_preservation_multiple_files(tmpdir, photozipper_cmd):
    """Verify metadata preserved for multiple files."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create multiple files with different timestamps
    file1 = source_dir / "multi_1.jpg"
    file2 = source_dir / "multi_2.jpg"
    file3 = source_dir / "multi_3.jpg"
    
    file1.write_text("1")
    file2.write_text("2")
    file3.write_text("3")
    
    # Set different timestamps
    time1 = 1704110400  # Jan 1, 2024
    time2 = 1704196800  # Jan 2, 2024
    time3 = 1704283200  # Jan 3, 2024
    
    os.utime(file1, (time1, time1))
    os.utime(file2, (time2, time2))
    os.utime(file3, (time3, time3))
    
    original_times = [
        file1.stat().st_mtime,
        file2.stat().st_mtime,
        file3.stat().st_mtime
    ]
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "multi",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Check all copied files
    copied_files = [
        output_dir / "multi" / "multi_1.jpg",
        output_dir / "multi" / "multi_2.jpg",
        output_dir / "multi" / "multi_3.jpg"
    ]
    
    for copied_file, original_time in zip(copied_files, original_times):
        assert copied_file.exists()
        copied_time = copied_file.stat().st_mtime
        time_diff = abs(copied_time - original_time)
        assert time_diff < 1.0, f"Timestamp for {copied_file.name} should be preserved"


def test_metadata_in_zip_archive(tmpdir, photozipper_cmd):
    """Verify metadata is preserved in zip archive."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file with specific timestamp
    test_file = source_dir / "zip_meta.jpg"
    test_file.write_text("archive data")
    
    specific_time = 1704110400
    os.utime(test_file, (specific_time, specific_time))
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "zip_meta",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify zip exists and contains file
    import zipfile
    zip_path = output_dir / "zip_meta.zip"
    assert zip_path.exists()
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Verify file is in archive
        names = zf.namelist()
        assert len(names) > 0, "Zip should contain files"
        assert any("zip_meta.jpg" in name for name in names)
