"""
File utility functions for MCP system
"""

import os
import json
from pathlib import Path
from typing import Any, Optional, Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        Path object of the directory
        
    Raises:
        OSError: If directory cannot be created
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def safe_write_file(file_path: Union[str, Path], content: str, 
                   encoding: str = 'utf-8', backup: bool = True) -> bool:
    """
    Safely write content to file with optional backup.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
        backup: Whether to create backup if file exists
        
    Returns:
        True if successful
        
    Raises:
        OSError: If write operation fails
    """
    file_path = Path(file_path)
    
    # Create parent directory if needed
    ensure_dir(file_path.parent)
    
    # Create backup if file exists and backup is requested
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        backup_path.write_text(file_path.read_text(encoding=encoding), encoding=encoding)
    
    # Write content
    file_path.write_text(content, encoding=encoding)
    return True


def safe_read_file(file_path: Union[str, Path], 
                  encoding: str = 'utf-8', default: Optional[str] = None) -> Optional[str]:
    """
    Safely read file content with fallback.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        default: Default value if file doesn't exist or can't be read
        
    Returns:
        File content or default value
    """
    try:
        return Path(file_path).read_text(encoding=encoding)
    except (OSError, UnicodeDecodeError):
        return default


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except OSError:
        return 0


def safe_json_write(file_path: Union[str, Path], data: Any, 
                   indent: int = 2, backup: bool = True) -> bool:
    """
    Safely write JSON data to file.
    
    Args:
        file_path: Path to JSON file
        data: Data to serialize as JSON
        indent: JSON indentation
        backup: Whether to create backup
        
    Returns:
        True if successful
        
    Raises:
        TypeError: If data is not JSON serializable
        OSError: If write operation fails
    """
    json_content = json.dumps(data, indent=indent, ensure_ascii=False)
    return safe_write_file(file_path, json_content, backup=backup)


def safe_json_read(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Safely read JSON data from file.
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or invalid JSON
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        content = safe_read_file(file_path)
        if content is None:
            return default
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return default


def list_files_with_extension(directory: Union[str, Path], 
                             extension: str, recursive: bool = False) -> list[Path]:
    """
    List files with specific extension in directory.
    
    Args:
        directory: Directory to search
        extension: File extension (with or without dot)
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    pattern = f"**/*{extension}" if recursive else f"*{extension}"
    return list(directory.glob(pattern))


def copy_file_safe(source: Union[str, Path], dest: Union[str, Path], 
                  overwrite: bool = False) -> bool:
    """
    Safely copy file with optional overwrite protection.
    
    Args:
        source: Source file path
        dest: Destination file path
        overwrite: Whether to overwrite existing file
        
    Returns:
        True if successful
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination exists and overwrite=False
        OSError: If copy operation fails
    """
    source = Path(source)
    dest = Path(dest)
    
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if dest.exists() and not overwrite:
        raise FileExistsError(f"Destination file exists: {dest}")
    
    # Ensure destination directory exists
    ensure_dir(dest.parent)
    
    # Copy file
    dest.write_bytes(source.read_bytes())
    return True


def cleanup_empty_dirs(directory: Union[str, Path], preserve_root: bool = True) -> int:
    """
    Remove empty directories recursively.
    
    Args:
        directory: Root directory to clean
        preserve_root: Whether to preserve the root directory itself
        
    Returns:
        Number of directories removed
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    removed_count = 0
    
    # Process subdirectories first (bottom-up)
    for subdir in directory.iterdir():
        if subdir.is_dir():
            removed_count += cleanup_empty_dirs(subdir, preserve_root=False)
    
    # Remove current directory if empty (unless it's root and preserve_root=True)
    try:
        if not preserve_root or directory != Path(directory).resolve():
            if not any(directory.iterdir()):  # Directory is empty
                directory.rmdir()
                removed_count += 1
    except OSError:
        # Directory not empty or permission denied
        pass
    
    return removed_count


def rotate_file(file_path: Union[str, Path], max_backups: int = 5) -> bool:
    """
    Rotate file by moving to numbered backup.
    
    Args:
        file_path: Path to file to rotate
        max_backups: Maximum number of backup files to keep
        
    Returns:
        True if successful
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return True
    
    try:
        # Move existing backups
        for i in range(max_backups - 1, 0, -1):
            old_backup = file_path.with_suffix(f'.{i}')
            new_backup = file_path.with_suffix(f'.{i + 1}')
            
            if old_backup.exists():
                if new_backup.exists():
                    new_backup.unlink()
                old_backup.rename(new_backup)
        
        # Move current file to .1
        backup_file = file_path.with_suffix('.1')
        if backup_file.exists():
            backup_file.unlink()
        file_path.rename(backup_file)
        
        return True
    except OSError:
        return False