"""
Contract tests for CLI required arguments validation.

These tests verify that the CLI enforces required arguments (--source, --pattern, --output)
and returns appropriate error codes when arguments are missing.
"""
import pytest
import subprocess
import sys
from pathlib import Path


def run_photozipper(args: list[str]) -> subprocess.CompletedProcess:
    """Run photozipper CLI with given arguments."""
    cmd = [sys.executable, "-m", "photozipper"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIRequiredArguments:
    """Test required argument validation."""

    def test_missing_source_argument(self):
        """Missing --source should return exit code 2 with error message."""
        result = run_photozipper(["--pattern", "test", "--output", "/tmp/out"])
        
        assert result.returncode == 2, "Should return exit code 2 for missing required argument"
        assert "--source" in result.stderr or "source" in result.stderr.lower(), \
            "Error message should mention missing --source"

    def test_missing_pattern_argument(self):
        """Missing --pattern should return exit code 2 with error message."""
        result = run_photozipper(["--source", "/tmp/src", "--output", "/tmp/out"])
        
        assert result.returncode == 2, "Should return exit code 2 for missing required argument"
        assert "--pattern" in result.stderr or "pattern" in result.stderr.lower(), \
            "Error message should mention missing --pattern"

    def test_missing_output_argument(self):
        """Missing --output should return exit code 2 with error message."""
        result = run_photozipper(["--source", "/tmp/src", "--pattern", "test"])
        
        assert result.returncode == 2, "Should return exit code 2 for missing required argument"
        assert "--output" in result.stderr or "output" in result.stderr.lower(), \
            "Error message should mention missing --output"

    def test_all_required_arguments_provided(self, tmp_path):
        """When all required arguments provided, should attempt to run (not return code 2)."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        # Should not return code 2 (validation error)
        # May return 0 (success) or 1 (operation error like no matches)
        assert result.returncode != 2, \
            "Should not return validation error when all required arguments provided"

    def test_help_flag_shows_required_arguments(self):
        """Help message should document required arguments."""
        result = run_photozipper(["--help"])
        
        assert result.returncode == 0, "Help should exit with code 0"
        assert "--source" in result.stdout, "Help should mention --source"
        assert "--pattern" in result.stdout, "Help should mention --pattern"
        assert "--output" in result.stdout, "Help should mention --output"
