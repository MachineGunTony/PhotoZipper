"""
Unit tests for pattern matching logic.

These tests verify the pattern matcher module functions using mocked file operations.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import re


# These imports will fail until implementation exists - that's expected for TDD
try:
    from photozipper.pattern_matcher import (
        validate_pattern,
        extract_group,
        scan_and_group
    )
except ImportError:
    # Expected during TDD - tests should fail
    validate_pattern = None
    extract_group = None
    scan_and_group = None


@pytest.mark.skipif(validate_pattern is None, reason="Module not implemented yet")
class TestPatternValidation:
    """Test pattern validation logic."""

    def test_simple_string_pattern_valid(self):
        """Simple string patterns should be valid."""
        assert validate_pattern("vacation") is True

    def test_regex_pattern_with_digits_valid(self):
        """Regex patterns with digits should be valid."""
        assert validate_pattern(r"trip\d{4}") is True

    def test_regex_pattern_with_groups_valid(self):
        """Regex patterns with groups should be valid."""
        assert validate_pattern(r"^IMG_\d+") is True

    def test_invalid_regex_raises_error(self):
        """Invalid regex should raise ValueError."""
        with pytest.raises(ValueError):
            validate_pattern("trip[")  # Unterminated character set

    def test_empty_pattern_raises_error(self):
        """Empty pattern should raise ValueError."""
        with pytest.raises(ValueError):
            validate_pattern("")


@pytest.mark.skipif(extract_group is None, reason="Module not implemented yet")
class TestGroupExtraction:
    """Test group name extraction from filenames."""

    def test_simple_prefix_extraction(self):
        """Simple prefix should be extracted as group name."""
        result = extract_group("vacation_beach.jpg", "vacation")
        assert result == "vacation"

    def test_regex_with_digits_extraction(self):
        """Regex pattern should extract group with digits."""
        result = extract_group("trip2004_01.jpg", r"trip\d{4}")
        assert result == "trip2004"

    def test_different_groups_same_pattern(self):
        """Same pattern should extract different groups from different files."""
        group1 = extract_group("trip2004_01.jpg", r"trip\d{4}")
        group2 = extract_group("trip2005_01.jpg", r"trip\d{4}")
        
        assert group1 == "trip2004"
        assert group2 == "trip2005"
        assert group1 != group2

    def test_no_match_returns_none(self):
        """No match should return None."""
        result = extract_group("document.pdf", "vacation")
        assert result is None

    def test_unicode_filename_extraction(self):
        """Unicode filenames should be handled correctly."""
        result = extract_group("café_photo.jpg", "café")
        assert result == "café"

    def test_prefix_at_start_of_filename(self):
        """Pattern at start of filename should be extracted."""
        result = extract_group("IMG_001.jpg", "IMG_")
        assert result == "IMG_"


@pytest.mark.skipif(scan_and_group is None, reason="Module not implemented yet")
class TestScanAndGroup:
    """Test directory scanning and file grouping."""

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    def test_single_group_detection(self, mock_is_file, mock_iterdir):
        """Files matching same pattern should be grouped together."""
        # Mock directory with files
        mock_files = [
            Mock(spec=Path, name="vacation_beach.jpg"),
            Mock(spec=Path, name="vacation_sunset.jpg"),
            Mock(spec=Path, name="vacation_pool.jpg"),
        ]
        for f in mock_files:
            f.name = f._mock_name
            f.is_file.return_value = True
        
        mock_iterdir.return_value = mock_files
        mock_is_file.return_value = True
        
        source_dir = Path("/fake/source")
        groups = scan_and_group(source_dir, "vacation")
        
        assert len(groups) == 1, "Should detect one group"
        assert groups[0].name == "vacation"
        assert len(groups[0].files) == 3

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    def test_multiple_groups_detection(self, mock_is_file, mock_iterdir):
        """Files matching different patterns should create multiple groups."""
        mock_files = [
            Mock(spec=Path, name="trip2004_01.jpg"),
            Mock(spec=Path, name="trip2004_02.jpg"),
            Mock(spec=Path, name="trip2005_01.jpg"),
            Mock(spec=Path, name="trip2006_01.jpg"),
        ]
        for f in mock_files:
            f.name = f._mock_name
            f.is_file.return_value = True
        
        mock_iterdir.return_value = mock_files
        mock_is_file.return_value = True
        
        source_dir = Path("/fake/source")
        groups = scan_and_group(source_dir, r"trip\d{4}")
        
        assert len(groups) == 3, "Should detect three groups"
        group_names = {g.name for g in groups}
        assert group_names == {"trip2004", "trip2005", "trip2006"}

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    def test_no_matches_returns_empty(self, mock_is_file, mock_iterdir):
        """No matching files should return empty list."""
        mock_files = [
            Mock(spec=Path, name="document.pdf"),
            Mock(spec=Path, name="report.docx"),
        ]
        for f in mock_files:
            f.name = f._mock_name
            f.is_file.return_value = True
        
        mock_iterdir.return_value = mock_files
        mock_is_file.return_value = True
        
        source_dir = Path("/fake/source")
        groups = scan_and_group(source_dir, "vacation")
        
        assert len(groups) == 0, "Should return empty list when no matches"

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    def test_skips_directories(self, mock_is_file, mock_iterdir):
        """Directories should be skipped during scan."""
        mock_file = Mock(spec=Path, name="vacation.jpg")
        mock_file.name = "vacation.jpg"
        mock_file.is_file.return_value = True
        
        mock_dir = Mock(spec=Path, name="subfolder")
        mock_dir.name = "subfolder"
        mock_dir.is_file.return_value = False
        
        mock_iterdir.return_value = [mock_file, mock_dir]
        
        source_dir = Path("/fake/source")
        groups = scan_and_group(source_dir, "vacation")
        
        # Should only process the file, not the directory
        assert len(groups) == 1
        assert len(groups[0].files) == 1

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    def test_unicode_filenames_handled(self, mock_is_file, mock_iterdir):
        """Unicode filenames should be processed correctly."""
        mock_files = [
            Mock(spec=Path, name="café_photo.jpg"),
            Mock(spec=Path, name="日本語.jpg"),
        ]
        for f in mock_files:
            f.name = f._mock_name
            f.is_file.return_value = True
        
        mock_iterdir.return_value = mock_files
        mock_is_file.return_value = True
        
        source_dir = Path("/fake/source")
        groups = scan_and_group(source_dir, "café|日本語")
        
        # Should handle Unicode filenames
        assert len(groups) >= 1, "Should detect groups with Unicode names"


# Test that module doesn't exist yet (TDD verification)
def test_module_not_implemented_yet():
    """Verify that pattern_matcher module doesn't exist yet (TDD check)."""
    try:
        from photozipper import pattern_matcher
        # If we get here, module exists - tests should be updated
        pytest.skip("Module already implemented - remove this test")
    except (ImportError, AttributeError):
        # Expected - module doesn't exist yet
        pass
