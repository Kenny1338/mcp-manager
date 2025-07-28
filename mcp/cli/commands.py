"""
CLI Command Handlers for MCP Management System

Implements all CLI commands by coordinating the various managers.
"""

import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# YAML support is optional
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ..managers.server_manager import ServerManager
from ..managers.process_manager import ProcessManager
from ..managers.log_manager import LogManager
from ..core.config import ConfigManager
from ..core.exceptions import MCPError, ServerNotFoundError, ServerAlreadyExistsError
from ..core.constants import TABLE_HEADERS, COLUMN_WIDTHS, ServerStatus


class CommandHandler:
    """
    Handles all CLI commands by coordinating between managers.
    
    This class acts as a facade, providing a clean interface
    between the CLI and the business logic managers.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize command handler with managers.
        
        Args:
            config_dir: Custom configuration directory
        """
        self.config_manager = ConfigManager(config_dir)
        self.server_manager = ServerManager(self.config_manager)
        self.process_manager = ProcessManager(self.config_manager)
        self.log_manager = LogManager(self.config_manager)
    
    def handle_ps(self, args) -> int:
        """
        Handle 'ps' command - show servers.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        try:
            # Update all server statuses
            for server in self.server_manager.servers.values():
                self.process_manager.update_server_status(server)
            self.server_manager.save_servers()
            
            servers = self.server_manager.list_servers(include_stopped=args.all)
            
            if not servers:
                if args.all:
                    print("No MCP servers found. Use 'mcp create' to create a server.")
                else:
                    print("No running MCP servers. Use 'mcp ps -a' to see all servers.")
                return 0
            
            if args.format == 'json':
                self._output_json([server.to_dict() for server in servers])
            elif args.format == 'yaml':
                self._output_yaml([server.to_dict() for server in servers])
            else:
                self._output_servers_table(servers)
            
            return 0
            
        except Exception as e:
            print(f"Error listing servers: {e}")
            return 1
    
    def handle_create(self, args) -> int:
        """
        Handle 'create' command - create new server.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        try:
            server = self.server_manager.create_server(
                name=args.name,
                command=args.server_command,
                config_file=args.config or "",
                health_check=args.health_check or ""
            )
            
            print(f"MCP Server '{args.name}' created.")
            
            # Auto-start if requested
            if args.auto_start:
                if self.process_manager.start_server(server):
                    self.server_manager.save_servers()
                    print(f"Server '{args.name}' started automatically.")
                else:
                    print(f"Warning: Failed to auto-start server '{args.name}'.")
            
            return 0
            
        except ServerAlreadyExistsError as e:
            print(f"Error: {e}")
            return 1
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error creating server: {e}")
            return 1
    
    def handle_start(self, args) -> int:
        """
        Handle 'start' command - start servers.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        success_count = 0
        total_count = len(args.names)
        
        for name in args.names:
            try:
                server = self.server_manager.get_server(name)
                
                if self.process_manager.start_server(server):
                    print(f"Server '{name}' started (PID: {server.pid})")
                    success_count += 1
                else:
                    print(f"Failed to start server '{name}'. See logs: mcp logs {name}")
                    
            except ServerNotFoundError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error starting server '{name}': {e}")
        
        # Save any status updates
        self.server_manager.save_servers()
        
        return 0 if success_count == total_count else 1
    
    def handle_stop(self, args) -> int:
        """
        Handle 'stop' command - stop servers.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        success_count = 0
        total_count = len(args.names)
        
        for name in args.names:
            try:
                server = self.server_manager.get_server(name)
                
                if args.force:
                    if self.process_manager.force_kill_server(server):
                        print(f"Server '{name}' force killed.")
                        success_count += 1
                    else:
                        print(f"Failed to force kill server '{name}'.")
                else:
                    if self.process_manager.stop_server(server, timeout=args.timeout):
                        print(f"Server '{name}' stopped.")
                        success_count += 1
                    else:
                        print(f"Failed to stop server '{name}'.")
                        
            except ServerNotFoundError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error stopping server '{name}': {e}")
        
        # Save any status updates
        self.server_manager.save_servers()
        
        return 0 if success_count == total_count else 1
    
    def handle_restart(self, args) -> int:
        """
        Handle 'restart' command - restart servers.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        success_count = 0
        total_count = len(args.names)
        
        for name in args.names:
            try:
                server = self.server_manager.get_server(name)
                
                print(f"Restarting '{name}'...")
                if self.process_manager.restart_server(server):
                    print(f"Server '{name}' restarted (PID: {server.pid})")
                    success_count += 1
                else:
                    print(f"Failed to restart server '{name}'. See logs: mcp logs {name}")
                    
            except ServerNotFoundError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error restarting server '{name}': {e}")
        
        # Save any status updates
        self.server_manager.save_servers()
        
        return 0 if success_count == total_count else 1
    
    def handle_remove(self, args) -> int:
        """
        Handle 'rm' command - remove servers.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        success_count = 0
        total_count = len(args.names)
        
        for name in args.names:
            try:
                server = self.server_manager.get_server(name)
                
                # Stop server if running and force is specified
                if server.is_running() and args.force:
                    self.process_manager.stop_server(server)
                
                # Remove server
                if self.server_manager.remove_server(name, force=args.force):
                    print(f"Server '{name}' removed.")
                    success_count += 1
                    
                    # Remove logs unless --keep-logs is specified
                    if not args.keep_logs:
                        self.log_manager.delete_logs(name)
                else:
                    print(f"Failed to remove server '{name}'.")
                    
            except ServerNotFoundError as e:
                print(f"Error: {e}")
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error removing server '{name}': {e}")
        
        return 0 if success_count == total_count else 1
    
    def handle_logs(self, args) -> int:
        """
        Handle 'logs' command - show server logs.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        try:
            if args.clear:
                self.log_manager.clear_logs(args.name)
                print(f"Logs cleared for server '{args.name}'.")
                return 0
            
            if args.search:
                lines = self.log_manager.search_logs(args.name, args.search, args.tail)
                for line in lines:
                    print(line)
                return 0
            
            if args.follow:
                # Follow live logs
                try:
                    for line in self.log_manager.follow_logs(args.name):
                        print(line)
                except KeyboardInterrupt:
                    print("\nStopped following logs.")
                return 0
            else:
                # Show last N lines
                lines = self.log_manager.get_logs(args.name, args.tail)
                for line in lines:
                    print(line)
                return 0
                
        except ServerNotFoundError as e:
            print(f"Error: {e}")
            return 1
        except Exception as e:
            print(f"Error reading logs: {e}")
            return 1
    
    def handle_inspect(self, args) -> int:
        """
        Handle 'inspect' command - show detailed server info.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Exit code (0 for success)
        """
        try:
            server = self.server_manager.get_server(args.name)
            
            # Update server status
            self.process_manager.update_server_status(server)
            self.server_manager.save_servers()
            
            if args.format == 'json':
                data = server.to_dict()
                if server.is_running():
                    process_info = self.process_manager.get_process_info(server)
                    if process_info:
                        data['process_info'] = process_info
                self._output_json(data)
            elif args.format == 'yaml':
                data = server.to_dict()
                if server.is_running():
                    process_info = self.process_manager.get_process_info(server)
                    if process_info:
                        data['process_info'] = process_info
                self._output_yaml(data)
            else:
                self._output_server_details(server)
            
            return 0
            
        except ServerNotFoundError as e:
            print(f"Error: {e}")
            return 1
        except Exception as e:
            print(f"Error inspecting server: {e}")
            return 1
    
    def _output_servers_table(self, servers: List):
        """Output servers in table format"""
        if not servers:
            return
        
        # Print header
        header = f"{TABLE_HEADERS['name']:<{COLUMN_WIDTHS['name']}} " \
                f"{TABLE_HEADERS['status']:<{COLUMN_WIDTHS['status']}} " \
                f"{TABLE_HEADERS['pid']:<{COLUMN_WIDTHS['pid']}} " \
                f"{TABLE_HEADERS['created']:<{COLUMN_WIDTHS['created']}} " \
                f"{TABLE_HEADERS['command']:<{COLUMN_WIDTHS['command']}}"
        
        print(header)
        print("-" * (sum(COLUMN_WIDTHS.values()) + len(COLUMN_WIDTHS) - 1))
        
        # Print servers
        for server in servers:
            created_time = server.get_created_datetime().strftime("%Y-%m-%d %H:%M:%S")
            pid_str = str(server.pid) if server.pid else "-"
            command_short = server.command[:37] + "..." if len(server.command) > 40 else server.command
            
            row = f"{server.name:<{COLUMN_WIDTHS['name']}} " \
                  f"{server.status:<{COLUMN_WIDTHS['status']}} " \
                  f"{pid_str:<{COLUMN_WIDTHS['pid']}} " \
                  f"{created_time:<{COLUMN_WIDTHS['created']}} " \
                  f"{command_short:<{COLUMN_WIDTHS['command']}}"
            
            print(row)
    
    def _output_server_details(self, server):
        """Output detailed server information in text format"""
        print(f"=== MCP Server: {server.name} ===")
        print(f"Status: {server.status}")
        print(f"Command: {server.command}")
        print(f"Config File: {server.config_file or 'None'}")
        print(f"PID: {server.pid or 'Not running'}")
        print(f"Created: {server.created}")
        print(f"Started: {server.started or 'Never started'}")
        print(f"Health Check: {server.health_check or 'None'}")
        
        if server.is_running():
            process_info = self.process_manager.get_process_info(server)
            if process_info:
                print(f"Memory: {process_info['memory_mb']} MB")
                print(f"CPU: {process_info['cpu_percent']}%")
                print(f"Threads: {process_info['num_threads']}")
                created_time = datetime.fromtimestamp(process_info['create_time'])
                print(f"Running since: {created_time.isoformat()}")
        
        # Log file info
        log_size = self.log_manager.get_log_file_size(server.name)
        if log_size > 0:
            print(f"Log file size: {log_size:,} bytes")
    
    def _output_json(self, data: Any):
        """Output data in JSON format"""
        print(json.dumps(data, indent=2, default=str))
    
    def _output_yaml(self, data: Any):
        """Output data in YAML format"""
        if not HAS_YAML:
            print("YAML support not available. Install PyYAML: pip install PyYAML")
            print("Falling back to JSON format:")
            self._output_json(data)
            return
        print(yaml.dump(data, default_flow_style=False, default_style=None))