"""
Shared pytest configuration and fixtures for all tests.
"""
import sys
import pytest
from pathlib import Path


@pytest.fixture
def photozipper_cmd():
    """
    Returns the command to run photozipper.
    
    On Windows, subprocess.run() doesn't automatically find executables
    in the venv's Scripts directory, so we use 'python -m photozipper'
    which works reliably across all platforms.
    """
    return [sys.executable, '-m', 'photozipper']
