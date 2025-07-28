# MCP Manager - Docker-like Interface for MCP Servers

A clean, class-based management system for Model Context Protocol (MCP) servers with a Docker-like command-line interface.

## Features

### ✅ Core Features

- **Docker-like CLI**: Familiar commands like `ps`, `start`, `stop`, `logs`, `inspect`
- **Server Registry**: Automatic storage and management of server configurations  
- **Process Management**: Full lifecycle management of server processes with PID tracking
- **Real-time Logging**: Automatic log collection and live log following for each server
- **Status Tracking**: Real-time status updates (running, stopped, error, starting)
- **Health Checks**: Optional health check command configuration
- **Multiple Output Formats**: JSON, YAML, and table output formats
- **Force Operations**: Graceful and force termination options
- **Auto-start**: Option to automatically start servers after creation

### 🏗️ Architecture

- **Clean Class-based Design**: Modular architecture with single responsibility principle
- **Separation of Concerns**: Dedicated managers for servers, processes, and logs
- **Extensible Structure**: Easy to add new features and commands
- **Error Handling**: Comprehensive exception handling with custom error types
- **Configuration Management**: JSON-based persistence with backup support

## Installation

### Quick Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Make executable:**
```bash
chmod +x mcp.py
```

3. **Optional: Create system-wide link:**
```bash
# System-wide (requires sudo)
sudo ln -s $(pwd)/mcp.py /usr/local/bin/mcp

# Or user-only
mkdir -p ~/.local/bin
ln -s $(pwd)/mcp.py ~/.local/bin/mcp
export PATH="$HOME/.local/bin:$PATH"  # Add to ~/.bashrc
```

### Automated Installation

```bash
./install.sh
```

## Usage

### Basic Commands

```bash
# Show running servers
mcp ps

# Show all servers (including stopped)
mcp ps -a

# Create new MCP server
mcp create my-server "python3 /path/to/server.py"

# Create server with configuration and health check
mcp create my-server "python3 server.py" --config config.json --health-check "curl localhost:8080/health"

# Create and auto-start server
mcp create my-server "python3 server.py" --auto-start

# Start server(s)
mcp start my-server
mcp start server1 server2 server3  # Multiple servers

# Stop server(s)
mcp stop my-server
mcp stop server1 server2 --timeout 30  # Custom timeout

# Force kill server(s)
mcp stop my-server --force

# Restart server(s)
mcp restart my-server

# Show server logs
mcp logs my-server
mcp logs my-server --tail 100    # Show last 100 lines
mcp logs my-server -f            # Follow live logs
mcp logs my-server --search "ERROR"  # Search logs
mcp logs my-server --clear       # Clear log file

# Show detailed server information
mcp inspect my-server
mcp inspect my-server --format json    # JSON output
mcp inspect my-server --format yaml    # YAML output

# Remove server(s)
mcp rm my-server
mcp rm server1 server2 -f       # Force remove running servers
mcp rm my-server --keep-logs     # Remove but keep log files
```

### Output Formats

#### Table Format (Default)
```bash
mcp ps
# NAME                 STATUS     PID      CREATED              COMMAND
# weather-server       running    12345    2024-01-15 10:30:45  python3 weather.py
# api-server          stopped    -        2024-01-15 09:15:20  node api.js
```

#### JSON Format
```bash
mcp ps --format json
mcp inspect my-server --format json
```

#### YAML Format
```bash
mcp ps --format yaml
mcp inspect my-server --format yaml
```

## Configuration

### Server Configuration Structure
```json
{
  "my-server": {
    "name": "my-server",
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

### File Structure
```
~/.mcp/
├── servers.json          # Server configurations
└── logs/
    ├── my-server.log      # Server-specific logs
    └── api-server.log
```

## Examples

### Basic Server Management

```bash
# Create a Python MCP server
mcp create weather-server "python3 weather_server.py"

# Start and monitor
mcp start weather-server
mcp ps
mcp logs weather-server -f

# Stop when done
mcp stop weather-server
```

### Managing Multiple Servers

```bash
# Create multiple servers
mcp create db-server "node database.js" --config db-config.json
mcp create api-server "python3 api.py" --health-check "curl localhost:8080/health"
mcp create file-server "go run fileserver.go"

# Start all servers
mcp start db-server api-server file-server

# Check status
mcp ps

# Stop specific servers
mcp stop api-server file-server

# Remove all servers
mcp rm db-server api-server file-server -f
```

### Advanced Log Management

```bash
# View recent logs
mcp logs my-server --tail 50

# Follow live logs
mcp logs my-server -f

# Search for errors
mcp logs my-server --search "ERROR" --tail 1000

# Clear log file
mcp logs my-server --clear
```

## Architecture

The system uses a clean, modular architecture:

- **[`mcp/models/server.py`](mcp/models/server.py)**: MCPServer data model with validation
- **[`mcp/managers/server_manager.py`](mcp/managers/server_manager.py)**: Server lifecycle management (CRUD operations)
- **[`mcp/managers/process_manager.py`](mcp/managers/process_manager.py)**: Process management (start/stop/restart)
- **[`mcp/managers/log_manager.py`](mcp/managers/log_manager.py)**: Log file operations and monitoring
- **[`mcp/core/config.py`](mcp/core/config.py)**: Configuration file management
- **[`mcp/cli/`](mcp/cli/)**: Command-line interface and argument parsing
- **[`mcp/utils/`](mcp/utils/)**: Utility functions for file and system operations

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed architecture documentation.

## Error Handling

The system includes comprehensive error handling:

- **ServerNotFoundError**: When trying to access non-existent servers
- **ServerAlreadyExistsError**: When creating servers with duplicate names
- **ServerStartError/ServerStopError**: Process management failures
- **ConfigurationError**: Configuration file issues
- **LogError**: Log file operation failures

## Requirements

- Python 3.7+
- psutil
- PyYAML (optional, for YAML output format)

## Development

### Adding New Features

1. **New Commands**: Add to [`mcp/cli/parser.py`](mcp/cli/parser.py) and [`mcp/cli/commands.py`](mcp/cli/commands.py)
2. **New Managers**: Create in [`mcp/managers/`](mcp/managers/) following the existing pattern
3. **New Utilities**: Add to [`mcp/utils/`](mcp/utils/) for reusable functions
4. **New Exceptions**: Add to [`mcp/core/exceptions.py`](mcp/core/exceptions.py)

### Testing

```bash
# Test basic functionality
python3 mcp.py --help
python3 mcp.py ps
python3 mcp.py create test-server "python3 example_mcp_server.py" --auto-start
python3 mcp.py ps
python3 mcp.py logs test-server
python3 mcp.py stop test-server
python3 mcp.py rm test-server
```

## License

MIT License