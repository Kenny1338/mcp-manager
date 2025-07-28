"""
System utility functions for MCP system
"""

import os
import signal
import time
from datetime import datetime, timedelta
from typing import Optional, List
import psutil


def is_process_running(pid: int) -> bool:
    """
    Check if a process is currently running.
    
    Args:
        pid: Process ID to check
        
    Returns:
        True if process is running
    """
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def kill_process_tree(pid: int, sig: int = signal.SIGTERM, timeout: int = 10) -> bool:
    """
    Kill a process and all its children.
    
    Args:
        pid: Root process ID
        sig: Signal to send
        timeout: Seconds to wait for termination
        
    Returns:
        True if all processes were terminated
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Send signal to all processes
        for child in children:
            try:
                child.send_signal(sig)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        try:
            parent.send_signal(sig)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Wait for termination
        gone, alive = psutil.wait_procs(children + [parent], timeout=timeout)
        
        # Force kill any remaining processes
        for proc in alive:
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return len(alive) == 0
        
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return True  # Process was already dead


def get_process_info(pid: int) -> Optional[dict]:
    """
    Get detailed process information.
    
    Args:
        pid: Process ID
        
    Returns:
        Dictionary with process info or None if process not found
    """
    try:
        proc = psutil.Process(pid)
        return {
            'pid': pid,
            'name': proc.name(),
            'status': proc.status(),
            'create_time': proc.create_time(),
            'cpu_percent': proc.cpu_percent(),
            'memory_mb': round(proc.memory_info().rss / 1024 / 1024, 1),
            'num_threads': proc.num_threads(),
            'cmdline': proc.cmdline(),
            'cwd': proc.cwd() if hasattr(proc, 'cwd') else None,
            'username': proc.username() if hasattr(proc, 'username') else None
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human readable string.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 0:
        return "0s"
    
    duration = timedelta(seconds=int(seconds))
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def format_timestamp(timestamp: float, format_type: str = "iso") -> str:
    """
    Format timestamp to human readable string.
    
    Args:
        timestamp: Unix timestamp
        format_type: Format type ("iso", "relative", "datetime")
        
    Returns:
        Formatted timestamp string
    """
    dt = datetime.fromtimestamp(timestamp)
    
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "relative":
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"
    else:  # datetime
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        host: Host to check on
        
    Returns:
        True if port is available
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection failed
    except socket.error:
        return False


def find_free_port(start_port: int = 8000, end_port: int = 9000, host: str = "localhost") -> Optional[int]:
    """
    Find a free port in the given range.
    
    Args:
        start_port: Start of port range
        end_port: End of port range
        host: Host to check on
        
    Returns:
        Free port number or None if no free port found
    """
    for port in range(start_port, end_port + 1):
        if is_port_available(port, host):
            return port
    return None


def get_system_info() -> dict:
    """
    Get basic system information.
    
    Returns:
        Dictionary with system info
    """
    try:
        return {
            'platform': psutil.PLATFORM,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free
            },
            'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            'boot_time': psutil.boot_time()
        }
    except Exception:
        return {}


def wait_for_condition(condition_func, timeout: int = 30, interval: float = 0.5) -> bool:
    """
    Wait for a condition to become true.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum seconds to wait
        interval: Seconds between checks
        
    Returns:
        True if condition was met, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    return False


def daemonize_process(pid_file: Optional[str] = None) -> bool:
    """
    Daemonize the current process.
    
    Args:
        pid_file: Optional PID file to write
        
    Returns:
        True if successfully daemonized
    """
    try:
        # First fork
        if os.fork() > 0:
            return False  # Parent process exits
    except OSError:
        return False
    
    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    try:
        # Second fork
        if os.fork() > 0:
            os._exit(0)  # Second parent exits
    except OSError:
        os._exit(1)
    
    # Redirect standard file descriptors
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Write PID file if requested
    if pid_file:
        try:
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except OSError:
            pass
    
    return True


def cleanup_pid_file(pid_file: str) -> bool:
    """
    Remove PID file if it exists.
    
    Args:
        pid_file: Path to PID file
        
    Returns:
        True if successful or file didn't exist
    """
    try:
        if os.path.exists(pid_file):
            os.unlink(pid_file)
        return True
    except OSError:
        return False