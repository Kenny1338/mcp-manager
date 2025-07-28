"""
CLI Argument Parser for MCP Management System

Defines all command line arguments and subcommands in a clean,
organized structure.
"""

import argparse
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the main argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='mcp',
        description="MCP Management System - Docker-like interface for MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp ps                          # Show running servers
  mcp ps -a                       # Show all servers
  mcp create my-server "python server.py"
  mcp start my-server
  mcp stop my-server
  mcp restart my-server
  mcp logs my-server
  mcp logs my-server -f           # Live logs
  mcp inspect my-server
  mcp rm my-server
        """
    )
    
    # Global options
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 1.0.0'
    )
    parser.add_argument(
        '--config-dir',
        help='Custom configuration directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='command', 
        help='Available commands',
        metavar='{ps,create,start,stop,restart,rm,logs,inspect}'
    )
    
    # Add all subcommands
    _add_ps_command(subparsers)
    _add_create_command(subparsers)
    _add_start_command(subparsers)
    _add_stop_command(subparsers)
    _add_restart_command(subparsers)
    _add_remove_command(subparsers)
    _add_logs_command(subparsers)
    _add_inspect_command(subparsers)
    
    return parser


def _add_ps_command(subparsers) -> None:
    """Add 'ps' command to show servers"""
    ps_parser = subparsers.add_parser(
        'ps', 
        help='Show MCP servers',
        description='List MCP servers and their status'
    )
    ps_parser.add_argument(
        '-a', '--all', 
        action='store_true', 
        help='Show all servers (including stopped)'
    )
    ps_parser.add_argument(
        '--format',
        choices=['table', 'json', 'yaml'],
        default='table',
        help='Output format'
    )


def _add_create_command(subparsers) -> None:
    """Add 'create' command to create new servers"""
    create_parser = subparsers.add_parser(
        'create', 
        help='Create new MCP server',
        description='Create a new MCP server configuration'
    )
    create_parser.add_argument(
        'name', 
        help='Server name (must be unique)'
    )
    create_parser.add_argument(
        'server_command', 
        help='Command to start the server'
    )
    create_parser.add_argument(
        '--config', 
        help='Path to configuration file'
    )
    create_parser.add_argument(
        '--health-check', 
        help='Health check command'
    )
    create_parser.add_argument(
        '--auto-start',
        action='store_true',
        help='Automatically start the server after creation'
    )


def _add_start_command(subparsers) -> None:
    """Add 'start' command to start servers"""
    start_parser = subparsers.add_parser(
        'start', 
        help='Start MCP server',
        description='Start one or more MCP servers'
    )
    start_parser.add_argument(
        'names', 
        nargs='+',
        help='Server name(s) to start'
    )
    start_parser.add_argument(
        '--wait',
        action='store_true',
        help='Wait for server to be ready before returning'
    )


def _add_stop_command(subparsers) -> None:
    """Add 'stop' command to stop servers"""
    stop_parser = subparsers.add_parser(
        'stop', 
        help='Stop MCP server',
        description='Stop one or more MCP servers'
    )
    stop_parser.add_argument(
        'names', 
        nargs='+',
        help='Server name(s) to stop'
    )
    stop_parser.add_argument(
        '--timeout', 
        type=int, 
        default=10,
        help='Seconds to wait before force killing (default: 10)'
    )
    stop_parser.add_argument(
        '--force',
        action='store_true',
        help='Force kill immediately without graceful shutdown'
    )


def _add_restart_command(subparsers) -> None:
    """Add 'restart' command to restart servers"""
    restart_parser = subparsers.add_parser(
        'restart', 
        help='Restart MCP server',
        description='Restart one or more MCP servers'
    )
    restart_parser.add_argument(
        'names', 
        nargs='+',
        help='Server name(s) to restart'
    )
    restart_parser.add_argument(
        '--timeout', 
        type=int, 
        default=10,
        help='Seconds to wait before force killing during stop (default: 10)'
    )


def _add_remove_command(subparsers) -> None:
    """Add 'rm' command to remove servers"""
    rm_parser = subparsers.add_parser(
        'rm', 
        help='Remove MCP server',
        description='Remove one or more MCP server configurations',
        aliases=['remove']
    )
    rm_parser.add_argument(
        'names', 
        nargs='+',
        help='Server name(s) to remove'
    )
    rm_parser.add_argument(
        '-f', '--force', 
        action='store_true', 
        help='Force removal even if server is running'
    )
    rm_parser.add_argument(
        '--keep-logs',
        action='store_true',
        help='Keep log files after removal'
    )


def _add_logs_command(subparsers) -> None:
    """Add 'logs' command to show server logs"""
    logs_parser = subparsers.add_parser(
        'logs', 
        help='Show server logs',
        description='Display logs from MCP server',
        aliases=['log']
    )
    logs_parser.add_argument(
        'name', 
        help='Server name'
    )
    logs_parser.add_argument(
        '-f', '--follow', 
        action='store_true', 
        help='Follow live logs (like tail -f)'
    )
    logs_parser.add_argument(
        '--tail', 
        type=int, 
        default=50, 
        help='Number of lines to show from end (default: 50)'
    )
    logs_parser.add_argument(
        '--since',
        help='Show logs since timestamp (e.g., "2023-01-01T10:00:00")'
    )
    logs_parser.add_argument(
        '--search',
        help='Search for pattern in logs'
    )
    logs_parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear (truncate) the log file'
    )


def _add_inspect_command(subparsers) -> None:
    """Add 'inspect' command to show detailed server information"""
    inspect_parser = subparsers.add_parser(
        'inspect', 
        help='Show detailed server information',
        description='Display detailed information about an MCP server'
    )
    inspect_parser.add_argument(
        'name', 
        help='Server name'
    )
    inspect_parser.add_argument(
        '--format',
        choices=['text', 'json', 'yaml'],
        default='text',
        help='Output format'
    )
    inspect_parser.add_argument(
        '--show-config',
        action='store_true',
        help='Include configuration file content'
    )


def validate_args(args) -> Optional[str]:
    """
    Validate parsed arguments and return error message if invalid.
    
    Args:
        args: Parsed arguments from ArgumentParser
        
    Returns:
        Error message if validation fails, None if valid
    """
    # Validate server names
    if hasattr(args, 'name') and args.name:
        if not args.name.strip():
            return "Server name cannot be empty"
        if any(char in args.name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            return "Server name contains invalid characters"
    
    if hasattr(args, 'names') and args.names:
        for name in args.names:
            if not name.strip():
                return "Server name cannot be empty"
            if any(char in name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                return f"Server name '{name}' contains invalid characters"
    
    # Validate command for create
    if hasattr(args, 'server_command') and args.server_command:
        if not args.server_command.strip():
            return "Server command cannot be empty"
    
    # Validate timeout values
    if hasattr(args, 'timeout') and args.timeout is not None:
        if args.timeout < 1:
            return "Timeout must be at least 1 second"
        if args.timeout > 300:
            return "Timeout cannot be more than 300 seconds"
    
    # Validate tail lines
    if hasattr(args, 'tail') and args.tail is not None:
        if args.tail < 1:
            return "Tail lines must be at least 1"
        if args.tail > 10000:
            return "Tail lines cannot be more than 10000"
    
    return None