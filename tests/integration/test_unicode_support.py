"""
Integration test for Unicode filename support.
Based on Scenario 10 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess
import zipfile
import sys


def test_unicode_filenames_basic(tmpdir, photozipper_cmd):
    """
    Scenario 10: Verify Unicode filenames work correctly.
    
    Setup: Files with Unicode names (café, 日本語, emoji)
    Execute: photozipper with pattern matching Unicode
    Expected: Files detected, copied, and zipped with correct names
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files with Unicode names
    (source_dir / "café_photo.jpg").write_text("test1")
    (source_dir / "日本語.jpg").write_text("test2")
    (source_dir / "emoji_😀.jpg").write_text("test3")
    
    # Execute with pattern matching Unicode
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "café|日本語|emoji",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'  # Handle decode errors gracefully on Windows
    )
    
    # Verify files detected and organized
    # Should create folders for each group
    folders_created = [d for d in output_dir.iterdir() if d.is_dir()]
    assert len(folders_created) >= 1, "Should create folders for Unicode groups"
    
    # Verify specific files exist in output
    # Files should be copied with correct names
    all_files = list(output_dir.rglob("*.jpg"))
    file_names = [f.name for f in all_files]
    
    assert any("café" in name for name in file_names), "Café file should be copied"
    assert any("日本語" in name for name in file_names), "Japanese file should be copied"
    assert any("😀" in name for name in file_names), "Emoji file should be copied"
    
    # Verify exit code
    assert result.returncode == 0


def test_unicode_in_folder_names(tmpdir, photozipper_cmd):
    """Test Unicode characters in group/folder names."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files where the pattern match creates Unicode folder
    (source_dir / "café_file1.jpg").write_text("a")
    (source_dir / "café_file2.jpg").write_text("b")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "café",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Folder should be created with Unicode name
    cafe_folder = output_dir / "café"
    assert cafe_folder.exists(), "Folder with Unicode name should be created"
    
    # Files should be in the Unicode-named folder
    files_in_folder = list(cafe_folder.glob("*.jpg"))
    assert len(files_in_folder) == 2


def test_unicode_in_zip_archives(tmpdir, photozipper_cmd):
    """Verify Unicode filenames preserved in zip archives."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create Unicode-named file
    unicode_name = "测试_test.jpg"
    (source_dir / unicode_name).write_text("data")
    
    # Execute
    subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "测试",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Find created zip
    zip_files = list(output_dir.glob("*.zip"))
    assert len(zip_files) > 0, "Zip should be created"
    
    # Verify zip contains file with Unicode name
    with zipfile.ZipFile(zip_files[0], 'r') as zf:
        names = zf.namelist()
        # Unicode name should be preserved
        assert any("测试" in name or unicode_name in name for name in names)


def test_unicode_mixed_scripts(tmpdir, photozipper_cmd):
    """Test files with mixed scripts (Latin, Cyrillic, Arabic, etc.)."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create files with various Unicode scripts
    files = [
        "Привет_russian.jpg",  # Cyrillic
        "مرحبا_arabic.jpg",    # Arabic
        "γειά_greek.jpg",      # Greek
        "שלום_hebrew.jpg",     # Hebrew
    ]
    
    for filename in files:
        try:
            (source_dir / filename).write_text("data")
        except (OSError, UnicodeEncodeError):
            # Skip if filesystem doesn't support this Unicode
            pytest.skip(f"Filesystem doesn't support Unicode: {filename}")
    
    # Execute with broad pattern
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", ".*",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'  # Handle decode errors gracefully on Windows
    )
    
    # Should handle all files
    assert result.returncode == 0


def test_unicode_emoji_sequences(tmpdir, photozipper_cmd):
    """Test complex emoji sequences in filenames."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file with emoji
    emoji_file = "photo_🎉🎊🎈.jpg"
    try:
        (source_dir / emoji_file).write_text("party")
    except (OSError, UnicodeEncodeError):
        pytest.skip("Filesystem doesn't support emoji in filenames")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "photo",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Should handle emoji
    copied_files = list(output_dir.rglob("*.jpg"))
    assert len(copied_files) > 0
    assert result.returncode == 0


def test_unicode_normalization(tmpdir, photozipper_cmd):
    """Test Unicode normalization (composed vs decomposed forms)."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Create file with composed Unicode (é as single character)
    composed = "résumé.jpg"
    try:
        (source_dir / composed).write_text("data")
    except (OSError, UnicodeEncodeError):
        pytest.skip("Filesystem Unicode issue")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "résumé",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Should find and copy the file
    copied_files = list(output_dir.rglob("*.jpg"))
    assert len(copied_files) > 0
    assert result.returncode == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Windows has filename restrictions")
def test_unicode_special_characters(tmpdir, photozipper_cmd):
    """Test Unicode with special/combining characters."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    # Files with combining diacritics
    special_files = [
        "test_ñ.jpg",
        "file_ü.jpg",
        "photo_ø.jpg",
    ]
    
    for filename in special_files:
        try:
            (source_dir / filename).write_text("data")
        except (OSError, UnicodeEncodeError):
            continue
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "test|file|photo",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # Should handle special characters
    assert result.returncode == 0
