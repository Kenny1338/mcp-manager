"""
Log Manager - Handles MCP server log operations

Responsible for reading, following, and managing server log files.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List, Iterator

from ..core.config import ConfigManager
from ..core.exceptions import LogError, ServerNotFoundError
from ..core.constants import DEFAULT_LOG_TAIL_LINES


class LogManager:
    """
    Manages MCP server log files and operations.
    
    Responsibilities:
    - Reading log files
    - Following live logs
    - Cleaning up log files
    - Log file rotation
    - Log formatting and filtering
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize log manager.
        
        Args:
            config_manager: Optional custom config manager
        """
        self.config_manager = config_manager or ConfigManager()
    
    def get_logs(self, server_name: str, tail_lines: int = DEFAULT_LOG_TAIL_LINES) -> List[str]:
        """
        Get the last N lines from a server's log file.
        
        Args:
            server_name: Name of the server
            tail_lines: Number of lines to return from the end
            
        Returns:
            List of log lines
            
        Raises:
            ServerNotFoundError: If log file doesn't exist
            LogError: If unable to read log file
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        if not log_file.exists():
            raise ServerNotFoundError(f"No logs found for server '{server_name}'")
        
        try:
            # Try using system 'tail' command first (faster for large files)
            result = subprocess.run(
                ['tail', '-n', str(tail_lines), str(log_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.splitlines()
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to Python implementation
            pass
        
        # Python fallback
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                return [line.rstrip() for line in lines[-tail_lines:]]
        except OSError as e:
            raise LogError(f"Failed to read log file for '{server_name}': {e}")
    
    def follow_logs(self, server_name: str) -> Iterator[str]:
        """
        Follow live logs for a server (like tail -f).
        
        Args:
            server_name: Name of the server
            
        Yields:
            New log lines as they appear
            
        Raises:
            ServerNotFoundError: If log file doesn't exist
            LogError: If unable to follow log file
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        if not log_file.exists():
            raise ServerNotFoundError(f"No logs found for server '{server_name}'")
        
        try:
            # Try using system 'tail -f' command
            proc = subprocess.Popen(
                ['tail', '-f', str(log_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            try:
                for line in iter(proc.stdout.readline, ''):
                    yield line.rstrip()
            except KeyboardInterrupt:
                proc.terminate()
                proc.wait()
                return
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait()
                    
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to Python implementation
            yield from self._follow_logs_python(log_file)
    
    def _follow_logs_python(self, log_file: Path) -> Iterator[str]:
        """
        Python fallback for following logs.
        
        Args:
            log_file: Path to log file
            
        Yields:
            New log lines as they appear
        """
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        yield line.rstrip()
                    else:
                        # No new data, wait a bit
                        time.sleep(0.1)
        except OSError as e:
            raise LogError(f"Failed to follow log file: {e}")
    
    def clear_logs(self, server_name: str) -> bool:
        """
        Clear (truncate) a server's log file.
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if cleared successfully
            
        Raises:
            LogError: If unable to clear log file
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        try:
            if log_file.exists():
                log_file.write_text('')
            return True
        except OSError as e:
            raise LogError(f"Failed to clear log file for '{server_name}': {e}")
    
    def delete_logs(self, server_name: str) -> bool:
        """
        Delete a server's log file completely.
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if deleted successfully
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        try:
            if log_file.exists():
                log_file.unlink()
            return True
        except OSError:
            return False
    
    def get_log_file_size(self, server_name: str) -> int:
        """
        Get the size of a server's log file in bytes.
        
        Args:
            server_name: Name of the server
            
        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        try:
            return log_file.stat().st_size if log_file.exists() else 0
        except OSError:
            return 0
    
    def rotate_logs(self, server_name: str, keep_backups: int = 5) -> bool:
        """
        Rotate log files (like logrotate).
        
        Args:
            server_name: Name of the server
            keep_backups: Number of backup files to keep
            
        Returns:
            True if rotated successfully
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        if not log_file.exists():
            return True
        
        try:
            # Move existing backups
            for i in range(keep_backups - 1, 0, -1):
                old_backup = log_file.with_suffix(f'.{i}')
                new_backup = log_file.with_suffix(f'.{i + 1}')
                
                if old_backup.exists():
                    if new_backup.exists():
                        new_backup.unlink()
                    old_backup.rename(new_backup)
            
            # Move current log to .1
            backup_file = log_file.with_suffix('.1')
            if backup_file.exists():
                backup_file.unlink()
            log_file.rename(backup_file)
            
            # Create new empty log file
            log_file.touch()
            
            return True
        except OSError as e:
            raise LogError(f"Failed to rotate logs for '{server_name}': {e}")
    
    def search_logs(self, server_name: str, pattern: str, 
                   max_lines: int = 1000, case_sensitive: bool = False) -> List[str]:
        """
        Search for a pattern in server logs.
        
        Args:
            server_name: Name of the server
            pattern: Search pattern
            max_lines: Maximum lines to search from end
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of matching log lines
        """
        log_file = self.config_manager.get_log_file_path(server_name)
        
        if not log_file.exists():
            return []
        
        try:
            lines = self.get_logs(server_name, max_lines)
            
            if not case_sensitive:
                pattern = pattern.lower()
                return [line for line in lines if pattern in line.lower()]
            else:
                return [line for line in lines if pattern in line]
                
        except (LogError, ServerNotFoundError):
            return []
    
    def get_all_log_files(self) -> List[str]:
        """
        Get list of all log files.
        
        Returns:
            List of server names that have log files
        """
        log_files = []
        logs_dir = self.config_manager.logs_dir
        
        if logs_dir.exists():
            for log_file in logs_dir.glob('*.log'):
                server_name = log_file.stem
                log_files.append(server_name)
        
        return sorted(log_files)
    
    def cleanup_orphaned_logs(self, active_servers: List[str]) -> int:
        """
        Clean up log files for servers that no longer exist.
        
        Args:
            active_servers: List of currently registered server names
            
        Returns:
            Number of orphaned log files removed
        """
        removed_count = 0
        all_log_files = self.get_all_log_files()
        
        for server_name in all_log_files:
            if server_name not in active_servers:
                if self.delete_logs(server_name):
                    removed_count += 1
        
        return removed_count