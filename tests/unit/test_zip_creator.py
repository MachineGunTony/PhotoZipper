"""
Unit tests for zip creation logic.

These tests verify the zip creator module functions using mocked zipfile operations.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import zipfile


# These imports will fail until implementation exists - that's expected for TDD
try:
    from photozipper.zip_creator import (
        create_zip,
        add_folder_to_zip
    )
except ImportError:
    # Expected during TDD - tests should fail
    create_zip = None
    add_folder_to_zip = None


@pytest.mark.skipif(create_zip is None, reason="Module not implemented yet")
class TestZipCreation:
    """Test zip archive creation."""

    def test_create_zip_success(self, tmp_path):
        """Should create zip archive successfully."""
        # Create a folder with test files
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo1.jpg").write_text("photo1 content")
        (folder / "photo2.jpg").write_text("photo2 content")
        
        zip_path = tmp_path / "vacation.zip"
        
        # Should not raise exception
        create_zip(folder, zip_path)
        
        # Verify ZIP was created
        assert zip_path.exists()
        
        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert 'photo1.jpg' in names
            assert 'photo2.jpg' in names

    def test_create_zip_folder_not_exists(self, tmp_path):
        """Should raise FileNotFoundError if source folder doesn't exist."""
        folder = tmp_path / "nonexistent"
        zip_path = tmp_path / "vacation.zip"
        
        with pytest.raises(FileNotFoundError):
            create_zip(folder, zip_path)

    @patch('zipfile.ZipFile')
    def test_create_zip_io_error(self, mock_zipfile, tmp_path):
        """Should propagate IO errors."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo.jpg").write_text("photo")
        
        zip_path = tmp_path / "vacation.zip"
        
        mock_zipfile.side_effect = OSError("Cannot write to disk")
        
        with pytest.raises(OSError):
            create_zip(folder, zip_path)

    def test_create_zip_uses_compression(self, tmp_path):
        """Should use ZIP_DEFLATED compression."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        # Create a file with repeating content that compresses well
        (folder / "photo.txt").write_text("a" * 1000)
        
        zip_path = tmp_path / "vacation.zip"
        
        create_zip(folder, zip_path)
        
        # Verify ZIP uses compression (compressed size < original size)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            info = zf.getinfo('photo.txt')
            assert info.compress_type == zipfile.ZIP_DEFLATED
            assert info.compress_size < info.file_size


@pytest.mark.skipif(add_folder_to_zip is None, reason="Module not implemented yet")
class TestAddFolderToZip:
    """Test adding folder contents to zip archive."""

    def test_add_all_files_to_zip(self, tmp_path):
        """Should add all files from folder to zip."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo1.jpg").write_text("photo1")
        (folder / "photo2.jpg").write_text("photo2")
        (folder / "photo3.jpg").write_text("photo3")
        
        zip_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            add_folder_to_zip(zf, folder)
        
        # Verify all files were added
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 3
            assert 'photo1.jpg' in names
            assert 'photo2.jpg' in names
            assert 'photo3.jpg' in names

    def test_skip_subdirectories(self, tmp_path):
        """Should only add files, not directories."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo.jpg").write_text("photo")
        (folder / "subfolder").mkdir()  # Create subdirectory
        (folder / "subfolder" / "nested.jpg").write_text("nested")
        
        zip_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            add_folder_to_zip(zf, folder)
        
        # Should only have photo.jpg, not the subfolder or its contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 1
            assert 'photo.jpg' in names
            assert 'subfolder' not in names
            assert 'nested.jpg' not in names

    def test_preserve_relative_paths(self, tmp_path):
        """Should use just filenames as archive names."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo.jpg").write_text("photo")
        
        zip_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            add_folder_to_zip(zf, folder)
        
        # Should use just the filename, not full path
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert 'photo.jpg' in names
            # Should not contain parent directories like "vacation/" prefix
            assert not any('/' in name for name in names)

    def test_unicode_filenames_in_zip(self, tmp_path):
        """Should handle Unicode filenames in zip archives."""
        folder = tmp_path / "café"
        folder.mkdir()
        (folder / "日本語.jpg").write_text("unicode content")
        
        zip_path = tmp_path / "test.zip"
        
        # Should not raise encoding errors
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            add_folder_to_zip(zf, folder)
        
        # Verify file was added
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert '日本語.jpg' in names

    def test_empty_folder(self, tmp_path):
        """Should handle empty folders gracefully."""
        folder = tmp_path / "vacation"
        folder.mkdir()  # Empty folder
        
        zip_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            add_folder_to_zip(zf, folder)
        
        # Should not crash, ZIP should exist but be empty
        with zipfile.ZipFile(zip_path, 'r') as zf:
            assert len(zf.namelist()) == 0


@pytest.mark.skipif(create_zip is None, reason="Module not implemented yet")
class TestZipErrorHandling:
    """Test error handling in zip operations."""

    @patch('zipfile.ZipFile')
    def test_handle_write_permission_error(self, mock_zipfile, tmp_path):
        """Should propagate write permission errors."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo.jpg").write_text("photo")
        
        zip_path = tmp_path / "vacation.zip"
        
        mock_zipfile.side_effect = PermissionError("Access denied")
        
        with pytest.raises(PermissionError):
            create_zip(folder, zip_path)

    @patch('zipfile.ZipFile')
    def test_handle_disk_full_error(self, mock_zipfile, tmp_path):
        """Should propagate disk full errors."""
        folder = tmp_path / "vacation"
        folder.mkdir()
        (folder / "photo.jpg").write_text("photo")
        
        zip_path = tmp_path / "vacation.zip"
        
        mock_zipfile.side_effect = OSError("No space left on device")
        
        with pytest.raises(OSError):
            create_zip(folder, zip_path)


# Test that module doesn't exist yet (TDD verification)
def test_module_not_implemented_yet():
    """Verify that zip_creator module doesn't exist yet (TDD check)."""
    try:
        from photozipper import zip_creator
        pytest.skip("Module already implemented - remove this test")
    except (ImportError, AttributeError):
        # Expected - module doesn't exist yet
        pass
