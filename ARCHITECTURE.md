# MCP Management System - Architecture

## Overview

The MCP Management System has been completely refactored to implement a clean, class-based architecture. Each class has a specific responsibility and is clearly separated from others, following SOLID principles.

## Project Structure

```
mcp/
├── __init__.py                 # Main package with exports
├── main.py                     # CLI entry point
├── models/
│   ├── __init__.py
│   └── server.py               # MCPServer data model
├── core/
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Custom exceptions
│   └── constants.py            # Constants & settings
├── managers/
│   ├── __init__.py
│   ├── server_manager.py       # Server lifecycle (create, remove, inspect)
│   ├── process_manager.py      # Process handling (start, stop, restart)
│   └── log_manager.py          # Log management (logs, follow)
├── cli/
│   ├── __init__.py
│   ├── parser.py               # Argument parsing
│   └── commands.py             # Command implementations
└── utils/
    ├── __init__.py
    ├── file_utils.py           # File operations
    └── system_utils.py         # System utilities

mcp.py                          # Main executable
mcp_backup.py                   # Backup of original implementation
```

## Design Principles

### 1. Single Responsibility Principle (SRP)
Each class has exactly one responsibility:

- **ServerManager**: Manages server configurations (CRUD operations)
- **ProcessManager**: Manages processes (start/stop/restart)
- **LogManager**: Manages log files (read/write/rotation)
- **ConfigManager**: Manages configuration files
- **CommandHandler**: Coordinates CLI commands

### 2. Open/Closed Principle (OCP)
The system is open for extension, closed for modification:

- New managers can be easily added without changing existing code
- New CLI commands can be added through the parser system
- New output formats can be added without modifying core logic

### 3. Dependency Inversion Principle (DIP)
High-level modules don't depend on low-level modules:

- Managers depend on abstractions (ConfigManager interface)
- CLI commands depend on manager interfaces, not implementations
- Easy to swap implementations for testing

### 4. Interface Segregation Principle (ISP)
Clients only depend on interfaces they use:

- Each manager has a focused interface
- No fat interfaces with unused methods
- Clear separation of concerns

## Core Components

### Data Model

#### MCPServer (`mcp/models/server.py`)
```python
@dataclass
class MCPServer:
    name: str
    command: str
    config_file: str
    pid: Optional[int] = None
    status: str = "stopped"
    created: str = ""
    started: str = ""
    ports: List[str] = None
    health_check: Optional[str] = None
```

**Responsibilities:**
- Data validation and serialization
- Status management helpers
- Datetime handling utilities

### Configuration Layer

#### ConfigManager (`mcp/core/config.py`)
```python
class ConfigManager:
    def load_servers(self) -> Dict[str, MCPServer]
    def save_servers(self, servers: Dict[str, MCPServer])
    def get_log_file_path(self, server_name: str) -> Path
    def backup_config(self, backup_suffix: str) -> Path
```

**Responsibilities:**
- JSON file operations for server configurations
- Directory structure management
- Configuration backup and restore
- Error handling for file operations

### Business Logic Layer

#### ServerManager (`mcp/managers/server_manager.py`)
```python
class ServerManager:
    def create_server(self, name: str, command: str, ...) -> MCPServer
    def remove_server(self, name: str, force: bool) -> bool
    def get_server(self, name: str) -> MCPServer
    def list_servers(self, include_stopped: bool) -> List[MCPServer]
```

**Responsibilities:**
- Server CRUD operations
- Server registry management
- Validation of server parameters
- Server metadata management

#### ProcessManager (`mcp/managers/process_manager.py`)
```python
class ProcessManager:
    def start_server(self, server: MCPServer) -> bool
    def stop_server(self, server: MCPServer, timeout: int) -> bool
    def restart_server(self, server: MCPServer) -> bool
    def update_server_status(self, server: MCPServer)
```

**Responsibilities:**
- Process lifecycle management
- PID tracking and monitoring
- Graceful and force termination
- Process status updates
- System resource monitoring

#### LogManager (`mcp/managers/log_manager.py`)
```python
class LogManager:
    def get_logs(self, server_name: str, tail_lines: int) -> List[str]
    def follow_logs(self, server_name: str) -> Iterator[str]
    def clear_logs(self, server_name: str) -> bool
    def search_logs(self, server_name: str, pattern: str) -> List[str]
```

**Responsibilities:**
- Log file operations
- Live log following
- Log searching and filtering
- Log rotation and cleanup
- Log file size management

### Presentation Layer

#### CLI Parser (`mcp/cli/parser.py`)
```python
def create_parser() -> argparse.ArgumentParser
def validate_args(args) -> Optional[str]
```

**Responsibilities:**
- Command-line argument definition
- Input validation
- Help text generation
- Subcommand organization

#### CommandHandler (`mcp/cli/commands.py`)
```python
class CommandHandler:
    def handle_ps(self, args) -> int
    def handle_create(self, args) -> int
    def handle_start(self, args) -> int
    # ... other command handlers
```

**Responsibilities:**
- CLI command orchestration
- Manager coordination
- Output formatting (table, JSON, YAML)
- Error handling and user feedback

## Data Flow

### 1. Command Execution Flow
```
CLI Input → Parser → Validator → CommandHandler → Managers → Data Layer
```

### 2. Server Creation Flow
```
User Input → Parser → CommandHandler → ServerManager → ConfigManager → File System
```

### 3. Process Management Flow
```
Start Command → CommandHandler → ProcessManager → System Process → Status Update
```

### 4. Log Operations Flow
```
Log Command → CommandHandler → LogManager → File System → Output Formatter
```

## Error Handling Strategy

### Custom Exception Hierarchy
```python
MCPError (Base)
├── ServerNotFoundError
├── ServerAlreadyExistsError
├── ServerStartError
├── ServerStopError
├── ConfigurationError
├── ProcessError
└── LogError
```

### Error Propagation
1. **Low-level errors** (file I/O, process operations) caught at manager level
2. **Business logic errors** propagated as custom exceptions
3. **CLI errors** handled at command handler level with user-friendly messages
4. **Validation errors** caught at parser level

## Configuration Management

### File Structure
```
~/.mcp/
├── servers.json          # Server configurations
├── config.json           # System configuration (future use)
└── logs/
    ├── server1.log        # Individual server logs
    └── server2.log
```

### Configuration Schema
```json
{
  "server-name": {
    "name": "server-name",
    "command": "python3 server.py",
    "config_file": "/path/to/config.json",
    "health_check": "curl localhost:8080/health",
    "pid": 12345,
    "status": "running",
    "created": "2024-01-15T10:30:45.123456",
    "started": "2024-01-15T10:30:45.789012",
    "ports": []
  }
}
```

## Extension Points

### Adding New Commands
1. Add command definition to `mcp/cli/parser.py`
2. Implement handler in `mcp/cli/commands.py`
3. Add to command dispatch map in `mcp/main.py`

### Adding New Managers
1. Create new manager class in `mcp/managers/`
2. Implement required interface methods
3. Add to `CommandHandler` initialization
4. Use dependency injection pattern

### Adding New Output Formats
1. Add format option to relevant parser commands
2. Implement formatter method in `CommandHandler`
3. Handle format selection in command handlers

### Adding New Utilities
1. Add to appropriate utility module in `mcp/utils/`
2. Follow existing patterns for error handling
3. Add comprehensive docstrings and type hints

## Testing Strategy

### Unit Testing Structure
```
tests/
├── test_models/
├── test_managers/
├── test_cli/
├── test_utils/
└── test_integration/
```

### Testing Approach
- **Unit tests** for individual classes and methods
- **Integration tests** for manager interactions
- **CLI tests** for command-line interface
- **Mock external dependencies** (file system, processes)

## Performance Considerations

### Efficiency Optimizations
- **Lazy loading** of server configurations
- **Efficient process monitoring** with psutil
- **Streaming log operations** for large files
- **Minimal memory footprint** for long-running operations

### Scalability Factors
- **Concurrent server management** capability
- **Large log file handling** with streaming
- **Many servers** with efficient data structures
- **Fast startup time** with optimized imports

## Security Considerations

### Input Validation
- **Command injection prevention** in server commands
- **Path traversal protection** in file operations
- **Process privilege separation** where possible

### File Operations
- **Safe file writing** with atomic operations
- **Backup creation** before configuration changes
- **Permission handling** for log files

## Future Architecture Improvements

### Potential Enhancements
1. **Plugin system** for custom managers
2. **Event system** for manager communication
3. **REST API** layer for remote management
4. **Database backend** for large-scale deployments
5. **Container integration** for isolated server execution
6. **Monitoring and alerting** system integration

### Migration Strategy
The modular architecture supports incremental improvements:
- New features can be added without breaking existing functionality
- Individual managers can be enhanced independently
- Configuration format is versioned for backward compatibility