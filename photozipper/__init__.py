"""
PhotoZipper - Organize photos into folders by filename pattern and zip them.

A CLI tool that helps organize files by automatically detecting groups based on
filename pattern matching. Files are copied into folders named after detected
groups, preserving metadata, and zip archives are created for each folder.
"""

__version__ = "1.0.0"
__author__ = "PhotoZipper Team"

# Expose main components
from photozipper.cli import main

__all__ = ["main", "__version__"]
