"""
Integration test for large file collections.
Based on Scenario 11 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import zipfile
import time


def test_large_file_collection_500_files(tmpdir, photozipper_cmd):
    """
    Scenario 11: Verify performance with many files.
    
    Setup: Create 500 files
    Execute: photozipper organizes all files
    Expected: All files copied, zip created, completes in reasonable time
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 500 test files
    num_files = 500
    for i in range(1, num_files + 1):
        filename = f"bulk_{i:03d}.jpg"
        (source_dir / filename).write_text(f"test{i}")
    
    # Measure execution time
    start_time = time.time()
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "bulk",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=60  # 60 second timeout
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Verify all files copied
    bulk_folder = output_dir / "bulk"
    assert bulk_folder.exists()
    
    files_in_output = list(bulk_folder.glob("bulk_*.jpg"))
    assert len(files_in_output) == num_files, f"Should copy all {num_files} files"
    
    # Verify zip created
    zip_file = output_dir / "bulk.zip"
    assert zip_file.exists()
    
    # Verify zip contains all files
    with zipfile.ZipFile(zip_file, 'r') as zf:
        zip_contents = zf.namelist()
        jpg_files = [name for name in zip_contents if ".jpg" in name]
        assert len(jpg_files) == num_files, f"Zip should contain all {num_files} files"
    
    # Performance check - should complete in reasonable time (< 30 seconds)
    assert execution_time < 30.0, f"Should complete in < 30s (took {execution_time:.2f}s)"
    
    # Verify exit code
    assert result.returncode == 0


def test_large_collection_multiple_groups(tmpdir, photozipper_cmd):
    """Test large collection distributed across multiple groups."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 200 files across 4 groups (50 each)
    num_groups = 4
    files_per_group = 50
    
    for group_num in range(1, num_groups + 1):
        for file_num in range(1, files_per_group + 1):
            filename = f"group{group_num}_{file_num:03d}.jpg"
            (source_dir / filename).write_text(f"g{group_num}f{file_num}")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"group\d",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Verify all groups created
    for group_num in range(1, num_groups + 1):
        group_folder = output_dir / f"group{group_num}"
        assert group_folder.exists()
        
        files = list(group_folder.glob("*.jpg"))
        assert len(files) == files_per_group
    
    # Verify all zips created
    zip_files = list(output_dir.glob("*.zip"))
    assert len(zip_files) == num_groups
    
    assert result.returncode == 0


def test_large_files_with_progress_output(tmpdir, photozipper_cmd):
    """Verify progress updates shown during large operation."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 100 files
    for i in range(1, 101):
        (source_dir / f"progress_{i:03d}.jpg").write_text(str(i))
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "progress",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Output should show progress or completion message
    output = result.stdout.lower()
    # Look for progress indicators or file count
    assert "100" in output or "progress" in output or "complete" in output


def test_large_collection_with_delete_originals(tmpdir, photozipper_cmd):
    """Test large collection with --delete-originals flag."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 100 files
    num_files = 100
    for i in range(1, num_files + 1):
        (source_dir / f"del_{i:03d}.jpg").write_text(str(i))
    
    # Execute with delete flag
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "del",
            "--output", str(output_dir),
            "--delete-originals"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Verify all source files deleted
    remaining_files = list(source_dir.glob("del_*.jpg"))
    assert len(remaining_files) == 0, "All source files should be deleted"
    
    # Verify all copied to output
    output_folder = output_dir / "del"
    copied_files = list(output_folder.glob("del_*.jpg"))
    assert len(copied_files) == num_files
    
    assert result.returncode == 0


def test_large_collection_dry_run_performance(tmpdir, photozipper_cmd):
    """Test dry-run performance with large collection."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 200 files
    for i in range(1, 201):
        (source_dir / f"drytest_{i:03d}.jpg").write_text(str(i))
    
    start_time = time.time()
    
    # Execute dry-run
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "drytest",
            "--output", str(output_dir),
            "--dry-run"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    execution_time = time.time() - start_time
    
    # Dry-run should be fast (< 5 seconds for scan only)
    assert execution_time < 5.0, "Dry-run should be fast"
    
    # No files should be created
    folders = list(output_dir.iterdir())
    # Only log file might exist
    assert len(folders) <= 1
    
    assert result.returncode == 0


def test_large_collection_zip_compression(tmpdir, photozipper_cmd):
    """Verify zip compression with large collection."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 50 files with compressible content
    compressible_content = "A" * 1000  # Highly compressible
    for i in range(1, 51):
        (source_dir / f"compress_{i:03d}.jpg").write_text(compressible_content)
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "compress",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Check zip exists
    zip_file = output_dir / "compress.zip"
    assert zip_file.exists()
    
    # Verify compression was applied (zip should be smaller than raw files)
    raw_size = 50 * len(compressible_content.encode())
    zip_size = zip_file.stat().st_size
    
    # Zip should be significantly smaller due to compression
    assert zip_size < raw_size, "Zip should be compressed"


def test_very_large_collection_1000_files(tmpdir, photozipper_cmd):
    """Stress test with 1000 files (optional, may be slow)."""
    # This test is optional and may be skipped in CI
    pytest.skip("Stress test - enable manually for performance testing")
    
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create 1000 files
    num_files = 1000
    for i in range(1, num_files + 1):
        (source_dir / f"stress_{i:04d}.jpg").write_text(str(i))
    
    start_time = time.time()
    
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "stress",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=120  # 2 minute timeout for 1000 files
    )
    
    execution_time = time.time() - start_time
    
    # Verify completion
    assert result.returncode == 0
    
    # Verify file count
    output_folder = output_dir / "stress"
    copied_files = list(output_folder.glob("*.jpg"))
    assert len(copied_files) == num_files
    
    print(f"1000 files processed in {execution_time:.2f} seconds")
