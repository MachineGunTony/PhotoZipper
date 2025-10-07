"""ZIP archive creation for PhotoZipper.

This module provides functions to:
- Create ZIP archives from folders
- Add files to ZIP with proper compression
- Handle Unicode filenames in ZIP archives
"""

import zipfile
from pathlib import Path


def create_zip(folder_path: Path, zip_path: Path) -> None:
    """Create a ZIP archive from a folder.
    
    Creates a ZIP archive containing all files in the folder (non-recursive).
    Uses ZIP_DEFLATED compression.
    
    Args:
        folder_path: Path to folder to zip
        zip_path: Path for output ZIP file
        
    Raises:
        FileNotFoundError: If folder doesn't exist
        OSError: If IO error occurs
    """
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        add_folder_to_zip(zf, folder_path)


def add_folder_to_zip(zip_file: zipfile.ZipFile, folder_path: Path) -> None:
    """Add all files from folder to ZIP archive.
    
    Only adds files directly in the folder (non-recursive).
    Preserves relative paths within the ZIP.
    
    Args:
        zip_file: Open ZipFile object
        folder_path: Path to folder containing files to add
    """
    for item in folder_path.iterdir():
        # Skip subdirectories - only add files
        if item.is_file():
            # Add file with relative path (just the filename)
            zip_file.write(item, arcname=item.name)
