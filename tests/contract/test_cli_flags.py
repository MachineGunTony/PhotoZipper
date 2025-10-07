"""
Contract tests for CLI optional flags behavior.

These tests verify that optional flags (--dry-run, --delete-originals, --log-level, etc.)
work correctly and follow the documented contract.
"""
import pytest
import subprocess
import sys
from pathlib import Path


def run_photozipper(args: list[str]) -> subprocess.CompletedProcess:
    """Run photozipper CLI with given arguments."""
    cmd = [sys.executable, "-m", "photozipper"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIOptionalFlags:
    """Test optional flag behavior."""

    def test_dry_run_flag_accepted(self, tmp_path):
        """--dry-run flag should be accepted without error."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--dry-run"
        ])
        
        # Should not fail with validation error
        assert result.returncode != 2, "Dry-run flag should be valid"

    def test_delete_originals_flag_accepted(self, tmp_path):
        """--delete-originals flag should be accepted without error."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--delete-originals"
        ])
        
        # Should not fail with validation error
        assert result.returncode != 2, "Delete-originals flag should be valid"

    def test_delete_originals_with_dry_run_error(self, tmp_path):
        """--delete-originals with --dry-run should return error."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--dry-run",
            "--delete-originals"
        ])
        
        assert result.returncode == 1, "Should error when combining --dry-run with --delete-originals"
        assert "dry-run" in result.stderr.lower() or "delete" in result.stderr.lower(), \
            "Error message should explain incompatible flags"

    def test_log_level_debug_accepted(self, tmp_path):
        """--log-level DEBUG should be accepted."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--log-level", "DEBUG"
        ])
        
        assert result.returncode != 2, "DEBUG log level should be valid"

    def test_log_level_info_accepted(self, tmp_path):
        """--log-level INFO should be accepted."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--log-level", "INFO"
        ])
        
        assert result.returncode != 2, "INFO log level should be valid"

    def test_log_level_warning_accepted(self, tmp_path):
        """--log-level WARNING should be accepted."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--log-level", "WARNING"
        ])
        
        assert result.returncode != 2, "WARNING log level should be valid"

    def test_log_level_error_accepted(self, tmp_path):
        """--log-level ERROR should be accepted."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--log-level", "ERROR"
        ])
        
        assert result.returncode != 2, "ERROR log level should be valid"

    def test_help_flag_exits_successfully(self):
        """--help should show help and exit with code 0."""
        result = run_photozipper(["--help"])
        
        assert result.returncode == 0, "Help should exit with code 0"
        assert len(result.stdout) > 0, "Help should print usage information"
        assert "photozipper" in result.stdout.lower(), "Help should mention program name"

    def test_version_flag_exits_successfully(self):
        """--version should show version and exit with code 0."""
        result = run_photozipper(["--version"])
        
        assert result.returncode == 0, "Version should exit with code 0"
        assert len(result.stdout) > 0, "Version should print version information"
        # Should contain version number (e.g., "1.0.0")
        assert any(char.isdigit() for char in result.stdout), \
            "Version output should contain version number"

    def test_invalid_log_level_rejected(self, tmp_path):
        """Invalid log level should return error."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--log-level", "INVALID"
        ])
        
        assert result.returncode != 0, "Invalid log level should be rejected"
