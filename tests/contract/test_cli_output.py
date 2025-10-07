"""
Contract tests for CLI output format validation.

These tests verify that output goes to the correct streams (stdout/stderr),
log files are created correctly, and exit codes match the specification.
"""
import pytest
import subprocess
import sys
from pathlib import Path


def run_photozipper(args: list[str]) -> subprocess.CompletedProcess:
    """Run photozipper CLI with given arguments."""
    cmd = [sys.executable, "-m", "photozipper"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIOutputFormat:
    """Test output format and destination."""

    def test_success_messages_to_stdout(self, tmp_path):
        """Success/progress messages should go to stdout."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create a test file
        test_file = source_dir / "test_file.jpg"
        test_file.write_text("test content")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        # If operation succeeds, output should be on stdout
        if result.returncode == 0:
            assert len(result.stdout) > 0, "Success messages should be on stdout"

    def test_error_messages_to_stderr(self, tmp_path):
        """Error messages should go to stderr."""
        # Use nonexistent source directory to trigger error
        source_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        assert result.returncode != 0, "Should fail with nonexistent source"
        assert len(result.stderr) > 0, "Error message should be on stderr"

    def test_log_file_created_in_output_dir(self, tmp_path):
        """Log file should be created in output directory."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create a test file
        test_file = source_dir / "test_file.jpg"
        test_file.write_text("test content")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        # Check if log file exists
        log_file = output_dir / "photozipper.log"
        assert log_file.exists(), "Log file should be created in output directory"

    def test_exit_code_0_on_success(self, tmp_path):
        """Exit code should be 0 when operation succeeds."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create a test file that matches pattern
        test_file = source_dir / "test_file.jpg"
        test_file.write_text("test content")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        assert result.returncode == 0, "Should return exit code 0 on success"

    def test_exit_code_1_on_operation_error(self, tmp_path):
        """Exit code should be 1 on operation errors (e.g., nonexistent source)."""
        source_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        assert result.returncode == 1, "Should return exit code 1 on operation error"

    def test_exit_code_2_on_validation_error(self):
        """Exit code should be 2 on validation errors (e.g., missing arguments)."""
        result = run_photozipper(["--pattern", "test"])
        
        assert result.returncode == 2, "Should return exit code 2 on validation error"

    def test_dry_run_output_includes_marker(self, tmp_path):
        """Dry-run output should include [DRY RUN] markers."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create a test file
        test_file = source_dir / "test_file.jpg"
        test_file.write_text("test content")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir),
            "--dry-run"
        ])
        
        # Dry-run output should contain marker
        output = result.stdout + result.stderr
        assert "[DRY RUN]" in output.upper() or "dry run" in output.lower(), \
            "Dry-run output should include marker"

    def test_progress_output_for_multiple_files(self, tmp_path):
        """Progress messages should be shown when processing multiple files."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create multiple test files
        for i in range(5):
            test_file = source_dir / f"test_{i}.jpg"
            test_file.write_text(f"test content {i}")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        if result.returncode == 0:
            # Should have some progress output
            assert len(result.stdout) > 0, "Should show progress for multiple files"

    def test_summary_output_includes_counts(self, tmp_path):
        """Summary output should include file counts."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create test files
        for i in range(3):
            test_file = source_dir / f"test_{i}.jpg"
            test_file.write_text(f"test content {i}")
        
        output_dir = tmp_path / "output"
        
        result = run_photozipper([
            "--source", str(source_dir),
            "--pattern", "test",
            "--output", str(output_dir)
        ])
        
        if result.returncode == 0:
            output = result.stdout
            # Should mention files scanned or copied
            assert any(word in output.lower() for word in ["files", "scanned", "copied"]), \
                "Summary should include file counts"
