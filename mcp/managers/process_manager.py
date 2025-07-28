"""
Process Manager - Handles MCP server process lifecycle

Responsible for starting, stopping, restarting servers and monitoring
their process status. Works with ServerManager for configuration.
"""

import os
import signal
import subprocess
import time
from typing import Optional
import psutil

from ..models.server import MCPServer
from ..core.config import ConfigManager
from ..core.exceptions import ServerStartError, ServerStopError, ProcessError
from ..core.constants import (
    ServerStatus, 
    DEFAULT_SHUTDOWN_TIMEOUT, 
    DEFAULT_STARTUP_WAIT
)


class ProcessManager:
    """
    Manages MCP server processes - starting, stopping, monitoring.
    
    Responsibilities:
    - Starting server processes
    - Stopping server processes gracefully
    - Force-killing unresponsive processes
    - Monitoring process status
    - Updating server status based on process state
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize process manager.
        
        Args:
            config_manager: Optional custom config manager for logs
        """
        self.config_manager = config_manager or ConfigManager()
    
    def start_server(self, server: MCPServer) -> bool:
        """
        Start a server process.
        
        Args:
            server: MCPServer instance to start
            
        Returns:
            True if started successfully
            
        Raises:
            ServerStartError: If server fails to start
        """
        # Check if already running
        if server.is_running():
            return True
        
        try:
            # Prepare log file
            log_file = self.config_manager.get_log_file_path(server.name)
            
            # Start the server process
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"\n=== Starting {server.name} at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                
                # Start process in new process group for clean termination
                proc = subprocess.Popen(
                    server.command,
                    shell=True,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid,  # New process group
                    cwd=None,  # Use current working directory
                    env=None   # Use current environment
                )
                
                # Update server state
                server.pid = proc.pid
                server.status = ServerStatus.STARTING
                server.update_started_time()
                
                # Wait briefly and check if process is still running
                time.sleep(DEFAULT_STARTUP_WAIT)
                
                if proc.poll() is None:
                    # Process is still running
                    server.status = ServerStatus.RUNNING
                    return True
                else:
                    # Process terminated immediately
                    server.status = ServerStatus.ERROR
                    server.clear_runtime_data()
                    raise ServerStartError(
                        server.name, 
                        f"Process terminated immediately with exit code {proc.returncode}"
                    )
                    
        except subprocess.SubprocessError as e:
            server.status = ServerStatus.ERROR
            server.clear_runtime_data()
            raise ServerStartError(server.name, f"Subprocess error: {e}")
        except OSError as e:
            server.status = ServerStatus.ERROR
            server.clear_runtime_data()
            raise ServerStartError(server.name, f"OS error: {e}")
        except Exception as e:
            server.status = ServerStatus.ERROR
            server.clear_runtime_data()
            raise ServerStartError(server.name, f"Unexpected error: {e}")
    
    def stop_server(self, server: MCPServer, timeout: int = DEFAULT_SHUTDOWN_TIMEOUT) -> bool:
        """
        Stop a server process gracefully.
        
        Args:
            server: MCPServer instance to stop
            timeout: Seconds to wait before force killing
            
        Returns:
            True if stopped successfully
            
        Raises:
            ServerStopError: If server fails to stop
        """
        if not server.pid or server.status == ServerStatus.STOPPED:
            # Already stopped
            server.clear_runtime_data()
            return True
        
        try:
            # Try graceful shutdown first
            self._terminate_process_group(server.pid, signal.SIGTERM)
            
            # Wait for graceful termination
            if self._wait_for_termination(server.pid, timeout):
                server.clear_runtime_data()
                return True
            
            # If still running, force kill
            self._terminate_process_group(server.pid, signal.SIGKILL)
            
            # Wait a bit more for force kill
            if self._wait_for_termination(server.pid, 3):
                server.clear_runtime_data()
                return True
            
            # If it's still not dead, something is very wrong
            raise ServerStopError(server.name, "Process could not be terminated")
            
        except ProcessLookupError:
            # Process was already terminated
            server.clear_runtime_data()
            return True
        except OSError as e:
            raise ServerStopError(server.name, f"OS error: {e}")
        except Exception as e:
            raise ServerStopError(server.name, f"Unexpected error: {e}")
    
    def restart_server(self, server: MCPServer) -> bool:
        """
        Restart a server (stop then start).
        
        Args:
            server: MCPServer instance to restart
            
        Returns:
            True if restarted successfully
        """
        # Stop first
        if server.is_running():
            self.stop_server(server)
        
        # Wait a moment
        time.sleep(1)
        
        # Start again
        return self.start_server(server)
    
    def update_server_status(self, server: MCPServer):
        """
        Update server status based on actual process state.
        
        Args:
            server: MCPServer instance to update
        """
        if not server.pid:
            server.status = ServerStatus.STOPPED
            return
        
        try:
            if psutil.pid_exists(server.pid):
                proc = psutil.Process(server.pid)
                if proc.is_running():
                    server.status = ServerStatus.RUNNING
                else:
                    server.clear_runtime_data()
            else:
                server.clear_runtime_data()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            server.clear_runtime_data()
    
    def get_process_info(self, server: MCPServer) -> Optional[dict]:
        """
        Get detailed process information.
        
        Args:
            server: MCPServer instance
            
        Returns:
            Dictionary with process info or None if not running
        """
        if not server.pid or not server.is_running():
            return None
        
        try:
            proc = psutil.Process(server.pid)
            return {
                'pid': server.pid,
                'memory_mb': round(proc.memory_info().rss / 1024 / 1024, 1),
                'cpu_percent': round(proc.cpu_percent(), 1),
                'create_time': proc.create_time(),
                'status': proc.status(),
                'num_threads': proc.num_threads(),
                'cmdline': proc.cmdline()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def _terminate_process_group(self, pid: int, sig: int):
        """
        Terminate process group (parent + children).
        
        Args:
            pid: Process ID
            sig: Signal to send
        """
        try:
            os.killpg(os.getpgid(pid), sig)
        except ProcessLookupError:
            # Process group doesn't exist, try individual process
            os.kill(pid, sig)
    
    def _wait_for_termination(self, pid: int, timeout: int) -> bool:
        """
        Wait for process to terminate.
        
        Args:
            pid: Process ID to wait for
            timeout: Maximum seconds to wait
            
        Returns:
            True if process terminated, False if still running
        """
        for _ in range(timeout):
            if not psutil.pid_exists(pid):
                return True
            time.sleep(1)
        return False
    
    def force_kill_server(self, server: MCPServer) -> bool:
        """
        Force kill a server process immediately.
        
        Args:
            server: MCPServer instance to kill
            
        Returns:
            True if killed successfully
        """
        if not server.pid:
            return True
        
        try:
            self._terminate_process_group(server.pid, signal.SIGKILL)
            time.sleep(1)
            server.clear_runtime_data()
            return True
        except (ProcessLookupError, OSError):
            server.clear_runtime_data()
            return True
    
    def is_port_in_use(self, port: int) -> bool:
        """
        Check if a port is in use.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is in use
        """
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True