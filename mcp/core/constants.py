"""
MCP Constants and Configuration Values

Central location for all constants used across the application.
"""

from pathlib import Path

# Directory paths
DEFAULT_CONFIG_DIR = Path.home() / ".mcp"
DEFAULT_LOGS_DIR = DEFAULT_CONFIG_DIR / "logs"
DEFAULT_SERVERS_FILE = DEFAULT_CONFIG_DIR / "servers.json"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

# Server statuses
class ServerStatus:
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    STARTING = "starting"

SERVER_STATUSES = [
    ServerStatus.STOPPED,
    ServerStatus.RUNNING,
    ServerStatus.ERROR,
    ServerStatus.STARTING
]

# Process management
DEFAULT_SHUTDOWN_TIMEOUT = 10  # seconds to wait for graceful shutdown
DEFAULT_STARTUP_WAIT = 1       # seconds to wait after startup
DEFAULT_LOG_TAIL_LINES = 50    # default number of log lines to show

# Display formatting
TABLE_HEADERS = {
    'name': 'NAME',
    'status': 'STATUS',
    'pid': 'PID', 
    'created': 'CREATED',
    'command': 'COMMAND'
}

COLUMN_WIDTHS = {
    'name': 20,
    'status': 10,
    'pid': 8,
    'created': 20,
    'command': 40
}

# Command shortcuts (similar to Docker)
COMMAND_ALIASES = {
    'ps': ['list', 'ls'],
    'rm': ['remove', 'delete'],
    'logs': ['log']
}

# File extensions for log files
LOG_FILE_EXTENSION = ".log"

# Default health check settings
DEFAULT_HEALTH_CHECK_TIMEOUT = 30
DEFAULT_HEALTH_CHECK_INTERVAL = 10