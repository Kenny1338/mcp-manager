# MCP Manager - Docker-like Interface for MCP Servers

A management system for Model Context Protocol (MCP) servers with a Docker-like user interface.

## Installation

### Automatic Installation (recommended)

```bash
# Run the installation script
./install.sh
```

The script does the following:
- Installs Python dependencies
- Makes the tool executable
- Creates a symbolic link in `/usr/local/bin/` or `~/.local/bin/`
- Checks PATH configuration

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the tool executable:
```bash
chmod +x mcp.py
```

3. Create symbolic link for global usage:
```bash
# Option 1: System-wide (requires sudo)
sudo ln -s $(pwd)/mcp.py /usr/local/bin/mcp

# Option 2: Only for current user
mkdir -p ~/.local/bin
ln -s $(pwd)/mcp.py ~/.local/bin/mcp
export PATH="$HOME/.local/bin:$PATH"  # Add to ~/.bashrc
```

## Verwendung

### Basic Commands

After installation you can run `mcp` from anywhere:

```bash
# Show all running MCP servers
mcp ps

# Show all servers (including stopped)
mcp ps -a

# Create new MCP server
mcp create my-server "python /path/to/server.py"

# Start server
mcp start my-server

# Stop server
mcp stop my-server

# Restart server
mcp restart my-server

# Show server logs
mcp logs my-server

# Follow live logs
mcp logs my-server -f

# Show detailed server information
mcp inspect my-server

# Remove server
mcp rm my-server

# Force remove running server
mcp rm my-server -f
```

### Advanced Configuration

```bash
# Create server with configuration file
mcp create my-server "python server.py" --config /path/to/config.json

# Create server with health check
mcp create my-server "python server.py" --health-check "curl http://localhost:8080/health"
```

## Features

### ✅ Implemented

- **Docker-like CLI**: Familiar commands like `ps`, `start`, `stop`, `logs`, `inspect`
- **Server Registry**: Automatic storage and management of server configurations
- **Process Management**: Monitoring of server processes with PIDs
- **Logging**: Automatic log collection for each server
- **Status Tracking**: Real-time status updates (running, stopped, error, starting)
- **Configuration Management**: Support for server-specific configuration files
- **Health Checks**: Optional health check commands
- **Force Operations**: Forced server removal even for running processes

### 🔄 In Development

- Service Discovery
- Automatic Start/Stop
- Container-like Isolation
- Network Management
- Volume Management

## Architecture

The system consists of:

1. **MCPManager**: Main class for server management
2. **MCPServer**: Data class for server representation
3. **CLI Interface**: Argparse-based command line
4. **Configuration Storage**: JSON-based persistence in `~/.mcp/`
5. **Logging System**: Separate log files for each server

## File Structure

```
~/.mcp/
├── servers.json          # Server-Konfigurationen
└── logs/
    ├── server1.log       # Server-spezifische Logs
    └── server2.log
```

## Beispiele

### MCP Server mit Python erstellen und starten

```bash
# Server erstellen
mcp create weather-server "python3 /home/user/mcp-servers/weather/server.py"

# Server starten
mcp start weather-server

# Status prüfen
mcp ps

# Logs ansehen
mcp logs weather-server -f
```

### Mehrere Server verwalten

```bash
# Mehrere Server erstellen
mcp create database-server "node /path/to/db-server.js"
mcp create api-server "python /path/to/api-server.py"
mcp create file-server "go run /path/to/file-server.go"

# Alle starten
mcp start database-server
mcp start api-server
mcp start file-server

# Status aller Server
mcp ps
```

## Development

The system is expandable and follows a modular structure. New functions can be easily added by:

1. Extending the “MCPServer” class

2. Adding new methods to the “MCPManager” class

3. Extending the CLI parser

## License

MIT license