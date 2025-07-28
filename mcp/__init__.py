"""
MCP Management System - Docker-like interface for MCP servers
"""

__version__ = "1.0.0"
__author__ = "MCP Team"
__description__ = "Docker-like interface for MCP servers"

from .models.server import MCPServer
from .managers.server_manager import ServerManager
from .managers.process_manager import ProcessManager
from .managers.log_manager import LogManager
from .core.config import ConfigManager
from .core.exceptions import MCPError, ServerNotFoundError, ServerAlreadyExistsError

__all__ = [
    "MCPServer",
    "ServerManager", 
    "ProcessManager",
    "LogManager",
    "ConfigManager",
    "MCPError",
    "ServerNotFoundError", 
    "ServerAlreadyExistsError"
]