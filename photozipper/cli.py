"""Command-line interface for PhotoZipper.

This module provides the CLI interface and main orchestration logic.
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from photozipper import __version__
from photozipper.logger import setup_logging
from photozipper.pattern_matcher import extract_group, scan_and_group, validate_pattern
from photozipper.file_organizer import (
    create_folder,
    copy_file_with_metadata,
    verify_copy,
    handle_merge,
    delete_original
)
from photozipper.zip_creator import create_zip
from photozipper.models import OperationResult, FileOperation


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='photozipper',
        description='Organize photos into folders by filename pattern and zip them',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Source directory containing files to organize'
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        required=True,
        help='Pattern to match in filenames (regex supported)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for organized folders and ZIP files'
    )
    
    # Optional flags
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--delete-originals',
        action='store_true',
        help='Delete original files after successful copy (cannot be used with --dry-run)'
    )
    
    parser.add_argument(
        '--zip-only',
        action='store_true',
        help='Delete organized folders after creating ZIP files, keeping only the archives'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> Optional[str]:
    """Validate argument compatibility (returns validation errors - exit 2).
    
    Only checks flag compatibility. Pattern and filesystem validation
    happen later and return operation errors (exit 1).
    
    Args:
        args: Parsed arguments
        
    Returns:
        Error message if validation fails, None if valid
    """
    # Check incompatible flags
    if args.dry_run and args.delete_originals:
        return "Error: --dry-run and --delete-originals cannot be used together"
    
    if args.dry_run and args.zip_only:
        return "Error: --dry-run and --zip-only cannot be used together"
    
    return None


def main() -> int:
    """Main entry point for PhotoZipper CLI.
    
    Returns:
        Exit code (0=success, 1=operation error, 2=validation error)
    """
    # Configure stdout/stderr to use UTF-8 on Windows for Unicode support
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Parse arguments
    parser = create_parser()
    
    # Handle case where no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 2
    
    args = parser.parse_args()
    
    # Validate arguments (operation error - exit 1)
    error_msg = validate_arguments(args)
    if error_msg:
        print(error_msg, file=sys.stderr)
        return 1
    
    # Convert paths
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    
    # Validate source directory exists (operation error - exit 1)
    if not source_dir.exists():
        print(f"Error: Source directory does not exist: {args.source}", file=sys.stderr)
        return 1
    
    if not source_dir.is_dir():
        print(f"Error: Source path is not a directory: {args.source}", file=sys.stderr)
        return 1
    
    # Validate pattern (operation error - exit 1)
    try:
        validate_pattern(args.pattern)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Set up logging
    logger = setup_logging(output_dir, args.log_level)
    
    try:
        # Log start
        if args.dry_run:
            logger.info("[DRY RUN] Starting organization (no changes will be made)")
        else:
            logger.info("Starting organization")
        
        logger.info(f"Source: {source_dir}")
        logger.info(f"Pattern: {args.pattern}")
        logger.info(f"Output: {output_dir}")
        
        # Scan and group files
        logger.info("Scanning source directory...")
        groups = scan_and_group(source_dir, args.pattern)
        
        if not groups:
            logger.warning("No files matched the pattern")
            print("No files matched the pattern", file=sys.stdout)
            return 0
        
        logger.info(f"Found {len(groups)} group(s)")
        
        # Track statistics
        files_copied = 0
        files_skipped = 0
        files_deleted = 0
        
        # Calculate total files for progress tracking
        total_files = sum(g.file_count() for g in groups)
        
        # Process each group with progress bar
        with tqdm(total=total_files, desc="Organizing files", unit="file", disable=args.dry_run) as pbar_files:
            for group in tqdm(groups, desc="Processing groups", unit="group", leave=False, disable=args.dry_run):
                group_name = group.name
                logger.info(f"Processing group '{group_name}' ({group.file_count()} file(s))")
                
                # Create group folder
                group_folder = output_dir / group_name
                
                if not args.dry_run:
                    create_folder(group_folder)
                    logger.debug(f"Created folder: {group_folder}")
                else:
                    logger.info(f"[DRY RUN] Would create folder: {group_folder}")
                
                # Copy files
                for source_file in group.files:
                    target_path = group_folder / source_file.name
                    
                    # Check if merge scenario
                    should_copy, action = handle_merge(target_path)
                    
                    if not should_copy:
                        logger.info(f"Skipping duplicate: {source_file.name}")
                        files_skipped += 1
                        pbar_files.update(1)
                        continue
                    
                    if args.dry_run:
                        logger.info(f"[DRY RUN] Would copy: {source_file.name} -> {target_path}")
                    else:
                        try:
                            # Copy file
                            copy_file_with_metadata(source_file.path, target_path)
                            
                            # Verify copy
                            if verify_copy(source_file.path, target_path):
                                logger.debug(f"Copied: {source_file.name}")
                                files_copied += 1
                                pbar_files.update(1)
                                
                                # Delete original if requested
                                if args.delete_originals:
                                    delete_original(source_file.path)
                                    logger.debug(f"Deleted original: {source_file.name}")
                                    files_deleted += 1
                            else:
                                logger.error(f"Copy verification failed: {source_file.name}")
                                pbar_files.close()
                                return 1
                        except Exception as e:
                            logger.error(f"Error copying {source_file.name}: {e}")
                            pbar_files.close()
                            return 1
                
                # Create ZIP
                zip_path = output_dir / f"{group_name}.zip"
                
                if not args.dry_run:
                    try:
                        create_zip(group_folder, zip_path)
                        logger.info(f"Created ZIP: {zip_path.name}")
                        
                        # Delete folder if --zip-only is specified
                        if args.zip_only:
                            shutil.rmtree(group_folder)
                            logger.info(f"Removed folder: {group_folder.name}")
                    except Exception as e:
                        logger.error(f"Error creating ZIP for {group_name}: {e}")
                        pbar_files.close()
                        return 1
                else:
                    logger.info(f"[DRY RUN] Would create ZIP: {zip_path.name}")
                    if args.zip_only:
                        logger.info(f"[DRY RUN] Would remove folder: {group_name}")
        
        # Print summary
        if args.dry_run:
            summary = f"[DRY RUN] Would process {sum(g.file_count() for g in groups)} files in {len(groups)} groups"
        else:
            summary = f"Successfully organized {files_copied} files into {len(groups)} groups"
            if files_skipped > 0:
                summary += f" ({files_skipped} skipped)"
            if files_deleted > 0:
                summary += f" ({files_deleted} deleted)"
        
        # Include group names in output
        if groups:
            group_names = ", ".join(g.name for g in groups)
            print(f"{summary}\nGroups: {group_names}", file=sys.stdout)
        else:
            print(summary, file=sys.stdout)
        
        logger.info(summary)
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
