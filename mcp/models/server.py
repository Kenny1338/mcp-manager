"""
MCP Server data model
"""

from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class MCPServer:
    """
    Data class representing an MCP Server with all its properties.
    
    This class encapsulates all the information needed to manage
    an MCP server instance including configuration, status, and runtime data.
    """
    name: str
    command: str
    config_file: str
    pid: Optional[int] = None
    status: str = "stopped"  # stopped, running, error, starting
    created: str = ""
    started: str = ""
    ports: List[str] = None
    health_check: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values after object creation"""
        if self.ports is None:
            self.ports = []
        if not self.created:
            self.created = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert server instance to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MCPServer':
        """Create server instance from dictionary"""
        return cls(**data)
    
    def is_running(self) -> bool:
        """Check if server is currently running"""
        return self.status == "running" and self.pid is not None
    
    def is_stopped(self) -> bool:
        """Check if server is stopped"""
        return self.status == "stopped"
    
    def has_health_check(self) -> bool:
        """Check if server has health check configured"""
        return bool(self.health_check)
    
    def get_created_datetime(self) -> datetime:
        """Get creation time as datetime object"""
        return datetime.fromisoformat(self.created)
    
    def get_started_datetime(self) -> Optional[datetime]:
        """Get start time as datetime object if available"""
        if self.started:
            return datetime.fromisoformat(self.started)
        return None
    
    def update_started_time(self):
        """Update the started timestamp to current time"""
        self.started = datetime.now().isoformat()
    
    def clear_runtime_data(self):
        """Clear runtime data (PID, started time) when server stops"""
        self.pid = None
        self.started = ""
        self.status = "stopped"