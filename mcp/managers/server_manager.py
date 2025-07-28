"""
Server Manager - Handles MCP server lifecycle management

Responsible for creating, removing, and inspecting MCP servers.
Does NOT handle process management (starting/stopping) - that's ProcessManager's job.
"""

from typing import Dict, List, Optional
from datetime import datetime

from ..models.server import MCPServer
from ..core.config import ConfigManager
from ..core.exceptions import ServerNotFoundError, ServerAlreadyExistsError, ConfigurationError
from ..core.constants import ServerStatus


class ServerManager:
    """
    Manages MCP server configurations and metadata.
    
    Responsibilities:
    - Creating new server configurations
    - Removing server configurations  
    - Inspecting server details
    - Loading/saving server registry
    - Validating server configurations
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize server manager.
        
        Args:
            config_manager: Optional custom config manager
        """
        self.config_manager = config_manager or ConfigManager()
        self.servers: Dict[str, MCPServer] = {}
        self.load_servers()
    
    def load_servers(self):
        """Load server configurations from storage"""
        try:
            self.servers = self.config_manager.load_servers()
        except ConfigurationError as e:
            print(f"Warning: Error loading server configurations: {e}")
            self.servers = {}
    
    def save_servers(self):
        """Save server configurations to storage"""
        self.config_manager.save_servers(self.servers)
    
    def create_server(self, name: str, command: str, config_file: str = "", 
                     health_check: str = "") -> MCPServer:
        """
        Create a new MCP server configuration.
        
        Args:
            name: Unique server name
            command: Command to start the server
            config_file: Optional configuration file path
            health_check: Optional health check command
            
        Returns:
            Created MCPServer instance
            
        Raises:
            ServerAlreadyExistsError: If server name already exists
            ValueError: If invalid parameters provided
        """
        if not name or not name.strip():
            raise ValueError("Server name cannot be empty")
        
        if not command or not command.strip():
            raise ValueError("Server command cannot be empty")
        
        name = name.strip()
        if name in self.servers:
            raise ServerAlreadyExistsError(name)
        
        server = MCPServer(
            name=name,
            command=command.strip(),
            config_file=config_file.strip(),
            health_check=health_check.strip() if health_check else ""
        )
        
        self.servers[name] = server
        self.save_servers()
        
        return server
    
    def remove_server(self, name: str, force: bool = False) -> bool:
        """
        Remove a server configuration.
        
        Args:
            name: Server name to remove
            force: Force removal even if server is running
            
        Returns:
            True if removed successfully
            
        Raises:
            ServerNotFoundError: If server doesn't exist
            ValueError: If server is running and force=False
        """
        if name not in self.servers:
            raise ServerNotFoundError(name)
        
        server = self.servers[name]
        
        # Check if server is running
        if server.is_running() and not force:
            raise ValueError(f"Server '{name}' is still running. Use force=True to remove or stop it first.")
        
        # Remove server from registry
        del self.servers[name]
        self.save_servers()
        
        # Clean up log file
        log_file = self.config_manager.get_log_file_path(name)
        if log_file.exists():
            try:
                log_file.unlink()
            except OSError:
                pass  # Log cleanup is not critical
        
        return True
    
    def get_server(self, name: str) -> MCPServer:
        """
        Get server by name.
        
        Args:
            name: Server name
            
        Returns:
            MCPServer instance
            
        Raises:
            ServerNotFoundError: If server doesn't exist
        """
        if name not in self.servers:
            raise ServerNotFoundError(name)
        return self.servers[name]
    
    def list_servers(self, include_stopped: bool = False) -> List[MCPServer]:
        """
        Get list of servers.
        
        Args:
            include_stopped: Whether to include stopped servers
            
        Returns:
            List of MCPServer instances
        """
        if include_stopped:
            return list(self.servers.values())
        
        return [server for server in self.servers.values() 
                if server.status != ServerStatus.STOPPED]
    
    def get_server_names(self) -> List[str]:
        """Get list of all server names"""
        return list(self.servers.keys())
    
    def server_exists(self, name: str) -> bool:
        """Check if server exists"""
        return name in self.servers
    
    def get_servers_by_status(self, status: str) -> List[MCPServer]:
        """
        Get servers filtered by status.
        
        Args:
            status: Server status to filter by
            
        Returns:
            List of servers with matching status
        """
        return [server for server in self.servers.values() 
                if server.status == status]
    
    def get_server_count(self) -> int:
        """Get total number of registered servers"""
        return len(self.servers)
    
    def get_running_server_count(self) -> int:
        """Get number of currently running servers"""
        return len(self.get_servers_by_status(ServerStatus.RUNNING))
    
    def update_server(self, name: str, **kwargs) -> MCPServer:
        """
        Update server configuration.
        
        Args:
            name: Server name
            **kwargs: Fields to update
            
        Returns:
            Updated server instance
            
        Raises:
            ServerNotFoundError: If server doesn't exist
        """
        if name not in self.servers:
            raise ServerNotFoundError(name)
        
        server = self.servers[name]
        
        # Update allowed fields
        updatable_fields = ['command', 'config_file', 'health_check']
        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(server, field, value)
        
        self.save_servers()
        return server
    
    def backup_servers(self, backup_suffix: str = None) -> str:
        """
        Create backup of server configurations.
        
        Args:
            backup_suffix: Optional suffix for backup file
            
        Returns:
            Path to backup file
        """
        if backup_suffix is None:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_file = self.config_manager.backup_config(backup_suffix)
        return str(backup_file)