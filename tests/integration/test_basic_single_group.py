"""
Integration test for basic organization with single group.
Based on Scenario 1 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import zipfile


def test_basic_single_group_organization(tmpdir, photozipper_cmd):
    """
    Scenario 1: Organize photos with a simple prefix pattern into one folder and zip it.
    
    Setup: 3 files with 'vacation' prefix, 1 file without
    Execute: photozipper --source ./source --pattern "vacation" --output ./output
    Expected: 1 group detected, 1 folder created, 3 files copied, 1 zip created
    """
    # Setup directories
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (source_dir / "vacation_beach.jpg").write_text("test1")
    (source_dir / "vacation_sunset.jpg").write_text("test2")
    (source_dir / "vacation_pool.jpg").write_text("test3")
    (source_dir / "work_meeting.jpg").write_text("test4")
    
    # Execute photozipper
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "vacation",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify output message
    assert "vacation" in result.stdout.lower(), "Should detect vacation group"
    
    # Verify folder created
    vacation_folder = output_dir / "vacation"
    assert vacation_folder.exists(), "vacation folder should be created"
    assert vacation_folder.is_dir(), "vacation should be a directory"
    
    # Verify files copied
    files_in_folder = list(vacation_folder.glob("*.jpg"))
    assert len(files_in_folder) == 3, "Should copy 3 vacation files"
    
    # Verify specific files exist
    assert (vacation_folder / "vacation_beach.jpg").exists()
    assert (vacation_folder / "vacation_sunset.jpg").exists()
    assert (vacation_folder / "vacation_pool.jpg").exists()
    
    # Verify work file NOT included
    assert not (vacation_folder / "work_meeting.jpg").exists()
    
    # Verify zip created
    zip_file = output_dir / "vacation.zip"
    assert zip_file.exists(), "vacation.zip should be created"
    
    # Verify zip contents
    with zipfile.ZipFile(zip_file, 'r') as zf:
        zip_contents = zf.namelist()
        assert len(zip_contents) == 3, "Zip should contain 3 files"
        assert any("vacation_beach.jpg" in name for name in zip_contents)
        assert any("vacation_sunset.jpg" in name for name in zip_contents)
        assert any("vacation_pool.jpg" in name for name in zip_contents)
    
    # Verify log file created
    log_file = output_dir / "photozipper.log"
    assert log_file.exists(), "Log file should be created"
    
    # Verify exit code
    assert result.returncode == 0, "Should exit with code 0"


def test_single_group_file_contents_preserved(tmpdir, photozipper_cmd):
    """Verify file contents are preserved during copy."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create test file with specific content
    test_content = "This is important photo data"
    (source_dir / "vacation_test.jpg").write_text(test_content)
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "vacation",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify content preserved
    copied_file = output_dir / "vacation" / "vacation_test.jpg"
    assert copied_file.exists()
    assert copied_file.read_text() == test_content


def test_single_group_log_file_contents(tmpdir, photozipper_cmd):
    """Verify log file contains operation details."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test_file.jpg").write_text("data")
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify log file has content
    log_file = output_dir / "photozipper.log"
    log_content = log_file.read_text()
    
    assert len(log_content) > 0, "Log file should have content"
    assert "test" in log_content.lower(), "Log should mention the group"
