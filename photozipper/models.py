"""Data models for PhotoZipper.

This module defines the core data structures used throughout the application:
- SourceFile: Represents a file to be organized
- FileGroup: Collection of files with the same group identifier
- OrganizeOperation: Configuration for an organization operation
- OperationResult: Results from an organization operation
- FileOperation: Individual file operation record
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class SourceFile:
    """Represents a source file to be organized.
    
    Attributes:
        path: Full path to the file
        name: Filename (basename)
        size: File size in bytes
        modified_time: Last modification time (Unix timestamp)
        group: Group identifier extracted from filename
    """
    path: Path
    name: str
    size: int
    modified_time: float
    group: str
    
    @classmethod
    def from_path(cls, file_path: Path, group: str) -> "SourceFile":
        """Create a SourceFile instance from a file path.
        
        Args:
            file_path: Path to the file
            group: Group identifier for this file
            
        Returns:
            SourceFile instance with metadata populated
        """
        stat = file_path.stat()
        return cls(
            path=file_path,
            name=file_path.name,
            size=stat.st_size,
            modified_time=stat.st_mtime,
            group=group
        )


@dataclass
class FileGroup:
    """Collection of files belonging to the same group.
    
    Attributes:
        name: Group identifier (e.g., 'trip2004')
        files: List of source files in this group
    """
    name: str
    files: List[SourceFile] = field(default_factory=list)
    
    def add_file(self, file: SourceFile) -> None:
        """Add a file to this group.
        
        Args:
            file: SourceFile to add
        """
        self.files.append(file)
    
    def file_count(self) -> int:
        """Get the number of files in this group.
        
        Returns:
            Count of files
        """
        return len(self.files)


@dataclass
class OrganizeOperation:
    """Configuration for a file organization operation.
    
    Attributes:
        source_dir: Source directory containing files to organize
        pattern: Regex pattern to match and extract groups
        output_dir: Output directory for organized files
        groups: List of file groups detected
        dry_run: If True, simulate without making changes
        delete_originals: If True, delete originals after successful copy
    """
    source_dir: Path
    pattern: str
    output_dir: Path
    groups: List[FileGroup] = field(default_factory=list)
    dry_run: bool = False
    delete_originals: bool = False


@dataclass
class FileOperation:
    """Record of an individual file operation.
    
    Attributes:
        source: Source file path
        target: Target file path
        operation_type: Type of operation ('copy', 'delete', 'skip')
        success: Whether operation succeeded
    """
    source: Path
    target: Path
    operation_type: str
    success: bool


@dataclass
class OperationResult:
    """Results from an organization operation.
    
    Attributes:
        success: Overall success status
        message: Summary message
        files_copied: Number of files copied
        files_deleted: Number of files deleted
        operations: List of individual file operations
    """
    success: bool
    message: str
    files_copied: int = 0
    files_deleted: int = 0
    operations: List[FileOperation] = field(default_factory=list)
