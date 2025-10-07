"""Pattern matching and file grouping logic for PhotoZipper.

This module provides functions to:
- Validate regex patterns
- Extract group identifiers from filenames
- Scan directories and organize files into groups
"""

import re
from pathlib import Path
from typing import Dict, Optional

from photozipper.models import FileGroup, SourceFile


def validate_pattern(pattern: str) -> bool:
    """Validate that a pattern is a valid regex.
    
    Args:
        pattern: Pattern string to validate
        
    Returns:
        True if pattern is valid
        
    Raises:
        ValueError: If pattern is empty or invalid regex
    """
    if not pattern or not pattern.strip():
        raise ValueError("Pattern cannot be empty")
    
    try:
        re.compile(pattern)
        return True
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")


def extract_group(filename: str, pattern: str) -> Optional[str]:
    """Extract group identifier from filename using pattern.
    
    The function searches for the pattern in the filename and returns
    the matched portion as the group identifier.
    
    Args:
        filename: Filename to extract group from
        pattern: Regex pattern to match
        
    Returns:
        Group identifier if match found, None otherwise
    """
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return None


def scan_and_group(source_dir: Path, pattern: str) -> list[FileGroup]:
    """Scan directory and group files by pattern matches.
    
    Args:
        source_dir: Directory to scan
        pattern: Regex pattern to match filenames
        
    Returns:
        List of FileGroup objects
    """
    groups_dict: Dict[str, FileGroup] = {}
    
    # Iterate through all items in source directory
    for item in source_dir.iterdir():
        # Skip directories - only process files
        if not item.is_file():
            continue
            
        # Try to extract group from filename
        group_name = extract_group(item.name, pattern)
        
        # Skip files that don't match pattern
        if group_name is None:
            continue
            
        # Create group if it doesn't exist
        if group_name not in groups_dict:
            groups_dict[group_name] = FileGroup(name=group_name)
            
        # Create SourceFile and add to group
        source_file = SourceFile.from_path(item, group_name)
        groups_dict[group_name].add_file(source_file)
    
    # Return as list
    return list(groups_dict.values())
