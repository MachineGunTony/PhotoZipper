"""File organization operations for PhotoZipper.

This module provides functions to:
- Create folders for organized files
- Copy files with metadata preservation
- Verify successful copies
- Handle merge scenarios
- Delete original files after successful operations
"""

import shutil
from pathlib import Path
from typing import Tuple


def create_folder(folder_path: Path) -> None:
    """Create a folder if it doesn't exist.
    
    Args:
        folder_path: Path to folder to create
    """
    folder_path.mkdir(parents=True, exist_ok=True)


def copy_file_with_metadata(source: Path, target: Path) -> bool:
    """Copy file preserving metadata (timestamps, permissions).
    
    Uses shutil.copy2() which preserves metadata.
    
    Args:
        source: Source file path
        target: Target file path
        
    Returns:
        True if copy succeeds, False if error occurs
    """
    try:
        shutil.copy2(source, target)
        return True
    except (PermissionError, OSError):
        return False


def verify_copy(source: Path, target: Path) -> bool:
    """Verify that a file was copied successfully.
    
    Verifies by comparing file sizes.
    
    Args:
        source: Source file path
        target: Target file path
        
    Returns:
        True if verification succeeds, False otherwise
    """
    # Check if target exists
    if not target.exists():
        return False
    
    # Compare file sizes
    source_size = source.stat().st_size
    target_size = target.stat().st_size
    
    return source_size == target_size


def handle_merge(target: Path) -> Tuple[bool, str]:
    """Handle merge scenario where target file already exists.
    
    If file exists with same name, skip copying (no overwrite).
    
    Args:
        target: Target file path
        
    Returns:
        Tuple of (should_copy, action_taken)
        - should_copy: True if file should be copied, False to skip
        - action_taken: Description of action ('skip' or 'copy')
    """
    if target.exists():
        return (False, 'skip')
    return (True, 'copy')


def delete_original(file_path: Path) -> bool:
    """Delete original file after successful copy.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if delete succeeds, False if error occurs
    """
    try:
        file_path.unlink()
        return True
    except (PermissionError, FileNotFoundError):
        return False
