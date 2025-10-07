"""
Integration test for multiple groups auto-detection.
Based on Scenario 2 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import zipfile


def test_multiple_groups_auto_detection(tmpdir, photozipper_cmd):
    """
    Scenario 2: Automatically detect and organize multiple groups in one command.
    
    Setup: Files with patterns trip2004, trip2005, trip2006
    Execute: photozipper --source ./source --pattern "trip\d{4}" --output ./output
    Expected: 3 groups detected, 3 folders created, 3 zips created
    """
    # Setup
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (source_dir / "trip2004_01.jpg").write_text("a")
    (source_dir / "trip2004_02.jpg").write_text("b")
    (source_dir / "trip2004_03.jpg").write_text("c")
    (source_dir / "trip2005_01.jpg").write_text("d")
    (source_dir / "trip2005_02.jpg").write_text("e")
    (source_dir / "trip2006_01.jpg").write_text("f")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"trip\d{4}",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify output message mentions all groups
    output_lower = result.stdout.lower()
    assert "trip2004" in output_lower
    assert "trip2005" in output_lower
    assert "trip2006" in output_lower
    
    # Verify folders created
    trip2004_folder = output_dir / "trip2004"
    trip2005_folder = output_dir / "trip2005"
    trip2006_folder = output_dir / "trip2006"
    
    assert trip2004_folder.exists() and trip2004_folder.is_dir()
    assert trip2005_folder.exists() and trip2005_folder.is_dir()
    assert trip2006_folder.exists() and trip2006_folder.is_dir()
    
    # Verify file counts per folder
    assert len(list(trip2004_folder.glob("*.jpg"))) == 3, "trip2004 should have 3 files"
    assert len(list(trip2005_folder.glob("*.jpg"))) == 2, "trip2005 should have 2 files"
    assert len(list(trip2006_folder.glob("*.jpg"))) == 1, "trip2006 should have 1 file"
    
    # Verify specific files exist
    assert (trip2004_folder / "trip2004_01.jpg").exists()
    assert (trip2004_folder / "trip2004_02.jpg").exists()
    assert (trip2004_folder / "trip2004_03.jpg").exists()
    assert (trip2005_folder / "trip2005_01.jpg").exists()
    assert (trip2005_folder / "trip2005_02.jpg").exists()
    assert (trip2006_folder / "trip2006_01.jpg").exists()
    
    # Verify zips created
    zip2004 = output_dir / "trip2004.zip"
    zip2005 = output_dir / "trip2005.zip"
    zip2006 = output_dir / "trip2006.zip"
    
    assert zip2004.exists(), "trip2004.zip should be created"
    assert zip2005.exists(), "trip2005.zip should be created"
    assert zip2006.exists(), "trip2006.zip should be created"
    
    # Verify zip contents
    with zipfile.ZipFile(zip2004, 'r') as zf:
        assert len(zf.namelist()) == 3, "trip2004.zip should contain 3 files"
    
    with zipfile.ZipFile(zip2005, 'r') as zf:
        assert len(zf.namelist()) == 2, "trip2005.zip should contain 2 files"
    
    with zipfile.ZipFile(zip2006, 'r') as zf:
        assert len(zf.namelist()) == 1, "trip2006.zip should contain 1 file"
    
    # Verify exit code
    assert result.returncode == 0


def test_multiple_groups_with_mixed_patterns(tmpdir, photozipper_cmd):
    """Test multiple groups with different year lengths."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files with various year patterns
    (source_dir / "event2020_a.jpg").write_text("1")
    (source_dir / "event2021_b.jpg").write_text("2")
    (source_dir / "event2022_c.jpg").write_text("3")
    (source_dir / "event2023_d.jpg").write_text("4")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"event\d{4}",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify all groups detected
    assert (output_dir / "event2020").exists()
    assert (output_dir / "event2021").exists()
    assert (output_dir / "event2022").exists()
    assert (output_dir / "event2023").exists()
    
    assert result.returncode == 0


def test_multiple_groups_file_contents_preserved(tmpdir, photozipper_cmd):
    """Verify file contents preserved across multiple groups."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files with specific content
    (source_dir / "group1_file.jpg").write_text("content1")
    (source_dir / "group2_file.jpg").write_text("content2")
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", r"group\d",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify contents
    assert (output_dir / "group1" / "group1_file.jpg").read_text() == "content1"
    assert (output_dir / "group2" / "group2_file.jpg").read_text() == "content2"
