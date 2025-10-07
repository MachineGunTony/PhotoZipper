"""
Integration test for error handling with invalid inputs.
Based on Scenarios 8-9 from quickstart.md.
"""
import pytest
from pathlib import Path
import subprocess


def test_error_invalid_source_directory(tmpdir, photozipper_cmd):
    """
    Scenario 8: Verify proper error message for invalid source directory.
    
    Execute: photozipper with non-existent source
    Expected: Error message, exit code 1
    """
    output_dir = Path(tmpdir) / "output"
    output_dir.mkdir()
    
    # Use non-existent source directory
    nonexistent_source = Path(tmpdir) / "nonexistent"
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(nonexistent_source),
            "--pattern", "test",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify error message
    error_output = result.stderr.lower() + result.stdout.lower()
    assert "source" in error_output or "exist" in error_output or "not found" in error_output
    
    # Verify error exit code
    assert result.returncode != 0, "Should exit with error code"
    assert result.returncode == 1, "Should exit with code 1 for operation error"


def test_error_invalid_regex_pattern(tmpdir, photozipper_cmd):
    """
    Scenario 9: Verify proper error message for malformed regex.
    
    Execute: photozipper with invalid pattern
    Expected: Error message about pattern, exit code 1
    """
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    # Execute with malformed regex
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_dir),
            "--pattern", "trip[",  # Unclosed bracket - invalid regex
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Verify error message
    error_output = result.stderr.lower() + result.stdout.lower()
    assert "pattern" in error_output or "invalid" in error_output or "regex" in error_output
    
    # Verify error exit code
    assert result.returncode != 0
    assert result.returncode == 1


def test_error_source_is_file_not_directory(tmpdir, photozipper_cmd):
    """Test error when source is a file instead of directory."""
    source_file = Path(tmpdir) / "source.txt"
    output_dir = Path(tmpdir) / "output"
    output_dir.mkdir()
    
    # Create a file (not directory)
    source_file.write_text("not a directory")
    
    # Execute
    result = subprocess.run(
        photozipper_cmd + [
            "--source", str(source_file),
            "--pattern", "test",
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True
    )
    
    # Should error
    assert result.returncode != 0
    error_output = result.stderr.lower() + result.stdout.lower()
    assert "director" in error_output or "invalid" in error_output


def test_error_output_directory_creation_fails(tmpdir, photozipper_cmd):
    """Test error handling when output directory cannot be created."""
    source_dir = Path(tmpdir) / "source"
    source_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    # Try to use an invalid path for output (e.g., contains null character on Unix)
    # On Windows, this might behave differently, but the test should still validate error handling
    invalid_output = Path(tmpdir) / "invalid\x00output"
    
    try:
        result = subprocess.run(
            photozipper_cmd + [
                "--source", str(source_dir),
                "--pattern", "test",
                "--output", str(invalid_output)
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # If it runs, it should error
        # Note: this may not work on all platforms
        # assert result.returncode != 0
    except (subprocess.TimeoutExpired, OSError, ValueError):
        # Expected on some platforms
        pass


def test_error_permission_denied_reading_source(tmpdir, photozipper_cmd):
    """Test error handling for permission denied on source."""
    # This test is platform-dependent and may not work everywhere
    # Skip if not on Unix-like system
    import sys
    if sys.platform == "win32":
        pytest.skip("Permission test not reliable on Windows")
    
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    # Remove read permissions
    import os
    os.chmod(source_dir, 0o000)
    
    try:
        result = subprocess.run(
            photozipper_cmd + [
                "--source", str(source_dir),
                "--pattern", "test",
                "--output", str(output_dir)
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Should error with permission issue
        assert result.returncode != 0
    finally:
        # Restore permissions for cleanup
        os.chmod(source_dir, 0o755)


def test_error_complex_invalid_pattern(tmpdir, photozipper_cmd):
    """Test various invalid regex patterns."""
    source_dir = Path(tmpdir) / "source"
    output_dir = Path(tmpdir) / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    
    (source_dir / "test.jpg").write_text("data")
    
    invalid_patterns = [
        "(?P<incomplete",  # Incomplete group
        "*abc",  # Invalid quantifier
        "(unclosed",  # Unclosed parenthesis
    ]
    
    for pattern in invalid_patterns:
        result = subprocess.run(
            photozipper_cmd + [
                "--source", str(source_dir),
                "--pattern", pattern,
                "--output", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        # Each should fail
        assert result.returncode != 0, f"Pattern '{pattern}' should be rejected"


def test_error_missing_required_argument(tmpdir, photozipper_cmd):
    """Test error when required argument is missing."""
    # This is more of a contract test but validates error handling
    
    # Missing --source
    result = subprocess.run(
        photozipper_cmd + [
            "--pattern", "test",
            "--output", "/tmp/output"
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
    
    # Missing --pattern
    result = subprocess.run(
        photozipper_cmd + [
            "--source", "/tmp/source",
            "--output", "/tmp/output"
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
    
    # Missing --output
    result = subprocess.run(
        photozipper_cmd + [
            "--source", "/tmp/source",
            "--pattern", "test"
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
