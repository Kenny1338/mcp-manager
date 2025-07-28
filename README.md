# MCP Manager - Docker-like Interface for MCP Servers

A comprehensive management system for Model Context Protocol (MCP) servers with a Docker-like user interface and AI-assisted development features.

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

### Setup for AI Features

After installation, run the interactive setup wizard to configure your LLM:

```bash
# Interactive setup wizard (recommended)
mcp setup

# Or configure manually
mcp config set llm.api_key YOUR_API_KEY
mcp config show
```

The setup wizard will guide you through:
1. **Provider Selection**: Anthropic Claude, OpenAI GPT, or Local LLM
2. **API Key Configuration**: Secure entry and storage
3. **Model Selection**: Choose the best model for your needs
4. **Verification**: Test your configuration

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

## Usage

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

### AI-Assisted Development Commands

```bash
# Generate new MCP server with AI assistance
mcp generate weather-server

# Generate and auto-start server
mcp generate my-api-server --auto-start

# Edit existing server with AI guidance
mcp edit weather-server "add a tool for getting 7-day forecast"

# Edit server with specific instructions
mcp edit my-server "optimize the database queries and add error handling"
```

### JSON Configuration Export

```bash
# Export server configuration for Cline/Claude Desktop
mcp provide weather-server

# Output: Ready-to-use JSON configuration with:
# - Correct command and arguments
# - Environment variables (API keys) for server type
# - File path instructions for different tools
```

### Configuration Management

```bash
# Show current configuration
mcp config show

# Set LLM API key (required for AI features)
mcp config set llm.api_key YOUR_API_KEY

# Set LLM provider (anthropic, openai, or local)
mcp config set llm.provider anthropic

# Set specific model
mcp config set llm.model claude-3-sonnet-20240229

# For local LLMs, set base URL
mcp config set llm.base_url http://localhost:11434

# Get specific configuration value
mcp config get llm.provider
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
- **🤖 AI-Assisted Generation**: Create new MCP servers with interactive project selection
- **🎯 Smart Project Templates**: Pre-configured templates for common server types
- **✏️ AI-Guided Editing**: Modify existing servers with natural language instructions
- **🔄 Auto-Integration**: Generated servers are automatically added and optionally started

### 🔄 In Development

- **Full AI Integration**: Real server generation based on user requirements
- **Advanced Editing**: AI-powered code modifications and optimizations
- **Template Expansion**: More project types and customization options
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
├── servers.json          # Server configurations
├── config.json           # LLM and system configuration
└── logs/
    ├── server1.log        # Server-specific logs
    └── server2.log
```

## Examples

### Create and start MCP Server with Python

```bash
# Create server
mcp create weather-server "python3 /home/user/mcp-servers/weather/server.py"

# Start server
mcp start weather-server

# Check status
mcp ps

# View logs
mcp logs weather-server -f
```

### Manage multiple servers

```bash
# Create multiple servers
mcp create database-server "node /path/to/db-server.js"
mcp create api-server "python /path/to/api-server.py"
mcp create file-server "go run /path/to/file-server.go"

# Start all
mcp start database-server
mcp start api-server
mcp start file-server

# Status of all servers
mcp ps
```

### AI-Assisted Development Examples

```bash
# Generate a weather server
mcp generate weather-api
# Interactive prompt:
# 1. Weather Server (OpenWeather API) ✅
# Generated server with TypeScript, API integration, and tools

# Generate and auto-start a file management server
mcp generate file-manager --auto-start
# Select: 2. File System Server
# Server created, built, and started automatically

# Edit existing server to add new functionality
mcp edit weather-api "add a tool for getting weather alerts and warnings"
# AI analyzes current server and adds new tools

# Complex modifications
mcp edit database-server "optimize all queries, add connection pooling, and improve error handling"
# AI modifies multiple files and rebuilds server
```

## Development

The system is expandable and follows a modular structure. New features can be easily added by:

1. Extending the `MCPServer` class
2. Adding new methods to the `MCPManager` class
3. Extending the CLI parser

## License

MIT License