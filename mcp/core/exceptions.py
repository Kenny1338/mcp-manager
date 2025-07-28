"""
MCP Custom Exceptions

Defines specific exception types for better error handling
and more descriptive error messages.
"""


class MCPError(Exception):
    """Base exception for all MCP-related errors"""
    pass


class ServerNotFoundError(MCPError):
    """Raised when trying to access a server that doesn't exist"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        super().__init__(f"Server '{server_name}' not found")


class ServerAlreadyExistsError(MCPError):
    """Raised when trying to create a server with an existing name"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        super().__init__(f"Server '{server_name}' already exists")


class ServerStartError(MCPError):
    """Raised when a server fails to start"""
    
    def __init__(self, server_name: str, reason: str = ""):
        self.server_name = server_name
        self.reason = reason
        message = f"Failed to start server '{server_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class ServerStopError(MCPError):
    """Raised when a server fails to stop"""
    
    def __init__(self, server_name: str, reason: str = ""):
        self.server_name = server_name
        self.reason = reason
        message = f"Failed to stop server '{server_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class ConfigurationError(MCPError):
    """Raised when there's an issue with configuration"""
    pass


class ProcessError(MCPError):
    """Raised when there's an issue with process management"""
    pass


class LogError(MCPError):
    """Raised when there's an issue with log management"""
    pass