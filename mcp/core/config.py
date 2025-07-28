"""
Configuration Management for MCP

Handles loading, saving, and managing server configurations
and system settings.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from ..models.server import MCPServer
from ..core.constants import DEFAULT_CONFIG_DIR, DEFAULT_SERVERS_FILE, DEFAULT_CONFIG_FILE
from ..core.exceptions import ConfigurationError


class ConfigManager:
    """
    Manages configuration files for MCP servers and system settings.
    
    Responsible for:
    - Loading and saving server configurations
    - Managing system configuration
    - Ensuring directory structure exists
    - Handling configuration file errors
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory (defaults to ~/.mcp)
        """
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.servers_file = self.config_dir / "servers.json"
        self.config_file = self.config_dir / "config.json"
        self.logs_dir = self.config_dir / "logs"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            self.logs_dir.mkdir(exist_ok=True)
        except OSError as e:
            raise ConfigurationError(f"Failed to create config directories: {e}")
    
    def load_servers(self) -> Dict[str, MCPServer]:
        """
        Load server configurations from file.
        
        Returns:
            Dictionary mapping server names to MCPServer instances
            
        Raises:
            ConfigurationError: If loading fails
        """
        servers = {}
        
        if not self.servers_file.exists():
            return servers
        
        try:
            with open(self.servers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for name, server_data in data.items():
                servers[name] = MCPServer.from_dict(server_data)
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ConfigurationError(f"Invalid server configuration file: {e}")
        except OSError as e:
            raise ConfigurationError(f"Failed to read server configuration: {e}")
        
        return servers
    
    def save_servers(self, servers: Dict[str, MCPServer]):
        """
        Save server configurations to file.
        
        Args:
            servers: Dictionary of server configurations to save
            
        Raises:
            ConfigurationError: If saving fails
        """
        try:
            data = {name: server.to_dict() for name, server in servers.items()}
            
            with open(self.servers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except (TypeError, OSError) as e:
            raise ConfigurationError(f"Failed to save server configuration: {e}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load system configuration.
        
        Returns:
            Dictionary containing system configuration
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ConfigurationError(f"Failed to load system configuration: {e}")
    
    def save_config(self, config: Dict[str, Any]):
        """
        Save system configuration.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except (TypeError, OSError) as e:
            raise ConfigurationError(f"Failed to save system configuration: {e}")
    
    def get_log_file_path(self, server_name: str) -> Path:
        """
        Get the log file path for a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Path to the server's log file
        """
        return self.logs_dir / f"{server_name}.log"
    
    def backup_config(self, backup_suffix: str = "backup") -> Path:
        """
        Create a backup of the current server configuration.
        
        Args:
            backup_suffix: Suffix for backup file
            
        Returns:
            Path to the backup file
        """
        if not self.servers_file.exists():
            raise ConfigurationError("No configuration file to backup")
        
        backup_file = self.config_dir / f"servers.{backup_suffix}.json"
        
        try:
            backup_file.write_text(self.servers_file.read_text())
            return backup_file
        except OSError as e:
            raise ConfigurationError(f"Failed to create backup: {e}")
    
    def restore_config(self, backup_file: Path):
        """
        Restore configuration from backup file.
        
        Args:
            backup_file: Path to backup file
        """
        if not backup_file.exists():
            raise ConfigurationError(f"Backup file not found: {backup_file}")
        
        try:
            self.servers_file.write_text(backup_file.read_text())
        except OSError as e:
            raise ConfigurationError(f"Failed to restore from backup: {e}")