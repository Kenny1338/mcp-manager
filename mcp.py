#!/usr/bin/env python3
"""
MCP Management System - Docker-like interface for MCP servers
Similar to Docker, but for MCP (Model Context Protocol) servers
"""

import argparse
import json
import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import psutil

@dataclass
class MCPServer:
    """Represents an MCP Server"""
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
        if self.ports is None:
            self.ports = []
        if not self.created:
            self.created = datetime.now().isoformat()

class MCPManager:
    """Main class for MCP Server Management"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".mcp"
        self.config_dir.mkdir(exist_ok=True)
        self.servers_file = self.config_dir / "servers.json"
        self.logs_dir = self.config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.servers: Dict[str, MCPServer] = {}
        self.load_servers()
    
    def load_servers(self):
        """Load server configurations"""
        if self.servers_file.exists():
            try:
                with open(self.servers_file, 'r') as f:
                    data = json.load(f)
                    for name, server_data in data.items():
                        self.servers[name] = MCPServer(**server_data)
            except Exception as e:
                print(f"Error loading server configuration: {e}")
    
    def save_servers(self):
        """Save server configurations"""
        try:
            data = {name: asdict(server) for name, server in self.servers.items()}
            with open(self.servers_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving server configuration: {e}")
    
    def update_server_status(self):
        """Update status of all servers based on running processes"""
        for server in self.servers.values():
            if server.pid:
                try:
                    if psutil.pid_exists(server.pid):
                        proc = psutil.Process(server.pid)
                        if proc.is_running():
                            server.status = "running"
                        else:
                            server.status = "stopped"
                            server.pid = None
                    else:
                        server.status = "stopped"
                        server.pid = None
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    server.status = "stopped"
                    server.pid = None
    
    def ps(self, all_servers: bool = False):
        """Show running MCP servers (like docker ps)"""
        self.update_server_status()
        
        if not self.servers:
            print("No MCP servers found. Use 'mcp create' to create a server.")
            return
        
        # Header
        print(f"{'NAME':<20} {'STATUS':<10} {'PID':<8} {'CREATED':<20} {'COMMAND':<40}")
        print("-" * 98)
        
        for name, server in self.servers.items():
            if not all_servers and server.status == "stopped":
                continue
                
            created_time = datetime.fromisoformat(server.created).strftime("%Y-%m-%d %H:%M:%S")
            pid_str = str(server.pid) if server.pid else "-"
            command_short = server.command[:37] + "..." if len(server.command) > 40 else server.command
            
            print(f"{name:<20} {server.status:<10} {pid_str:<8} {created_time:<20} {command_short:<40}")
    
    def create(self, name: str, command: str, config_file: str = "", health_check: str = ""):
        """Create a new MCP server"""
        if name in self.servers:
            print(f"Server '{name}' already exists!")
            return False
        
        server = MCPServer(
            name=name,
            command=command,
            config_file=config_file,
            health_check=health_check
        )
        
        self.servers[name] = server
        self.save_servers()
        print(f"MCP Server '{name}' created.")
        return True
    
    def start(self, name: str):
        """Start an MCP server"""
        if name not in self.servers:
            print(f"Server '{name}' not found!")
            return False
        
        server = self.servers[name]
        
        # Prüfe ob bereits läuft
        self.update_server_status()
        if server.status == "running":
            print(f"Server '{name}' is already running!")
            return True
        
        try:
            # Log file for the server
            log_file = self.logs_dir / f"{name}.log"
            
            # Start the server process
            with open(log_file, 'a') as log:
                log.write(f"\n=== Starting {name} at {datetime.now().isoformat()} ===\n")
                
                # Start process in background
                proc = subprocess.Popen(
                    server.command,
                    shell=True,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid  # New process group for clean termination
                )
                
                server.pid = proc.pid
                server.status = "starting"
                server.started = datetime.now().isoformat()
                
                # Wait briefly and check status
                time.sleep(1)
                if proc.poll() is None:
                    server.status = "running"
                    print(f"Server '{name}' started (PID: {server.pid})")
                else:
                    server.status = "error"
                    server.pid = None
                    print(f"Error starting server '{name}'. See logs: mcp logs {name}")
                    return False
                
                self.save_servers()
                return True
                
        except Exception as e:
            print(f"Error starting server '{name}': {e}")
            server.status = "error"
            server.pid = None
            self.save_servers()
            return False
    
    def stop(self, name: str):
        """Stop an MCP server"""
        if name not in self.servers:
            print(f"Server '{name}' not found!")
            return False
        
        server = self.servers[name]
        
        if not server.pid:
            print(f"Server '{name}' is not running!")
            return True
        
        try:
            # Try graceful shutdown
            os.killpg(os.getpgid(server.pid), signal.SIGTERM)
            
            # Wait for termination
            for _ in range(10):  # Wait 10 seconds
                if not psutil.pid_exists(server.pid):
                    break
                time.sleep(1)
            
            # If still running, force kill
            if psutil.pid_exists(server.pid):
                os.killpg(os.getpgid(server.pid), signal.SIGKILL)
                time.sleep(1)
            
            server.status = "stopped"
            server.pid = None
            self.save_servers()
            print(f"Server '{name}' stopped.")
            return True
            
        except (ProcessLookupError, psutil.NoSuchProcess):
            # Process was already terminated
            server.status = "stopped"
            server.pid = None
            self.save_servers()
            print(f"Server '{name}' was already stopped.")
            return True
        except Exception as e:
            print(f"Error stopping server '{name}': {e}")
            return False
    
    def restart(self, name: str):
        """Restart an MCP server"""
        print(f"Restarting '{name}'...")
        self.stop(name)
        time.sleep(2)
        return self.start(name)
    
    def remove(self, name: str, force: bool = False):
        """Remove an MCP server"""
        if name not in self.servers:
            print(f"Server '{name}' not found!")
            return False
        
        server = self.servers[name]
        
        # Stop first if running
        if server.status == "running" and not force:
            print(f"Server '{name}' is still running. Use --force to remove or stop it first.")
            return False
        elif server.status == "running" and force:
            self.stop(name)
        
        # Remove server
        del self.servers[name]
        self.save_servers()
        
        # Delete log file
        log_file = self.logs_dir / f"{name}.log"
        if log_file.exists():
            log_file.unlink()
        
        print(f"Server '{name}' removed.")
        return True
    
    def logs(self, name: str, follow: bool = False, tail: int = 50):
        """Show logs of an MCP server"""
        if name not in self.servers:
            print(f"Server '{name}' not found!")
            return False
        
        log_file = self.logs_dir / f"{name}.log"
        if not log_file.exists():
            print(f"No logs found for server '{name}'.")
            return False
        
        if follow:
            # Live display of logs
            subprocess.run(["tail", "-f", str(log_file)])
        else:
            # Show last N lines
            try:
                subprocess.run(["tail", "-n", str(tail), str(log_file)])
            except FileNotFoundError:
                # Fallback if tail not available
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-tail:]:
                        print(line.rstrip())
        
        return True
    
    def inspect(self, name: str):
        """Show detailed information about an MCP server"""
        if name not in self.servers:
            print(f"Server '{name}' not found!")
            return False
        
        server = self.servers[name]
        self.update_server_status()
        
        print(f"=== MCP Server: {name} ===")
        print(f"Status: {server.status}")
        print(f"Command: {server.command}")
        print(f"Config File: {server.config_file or 'None'}")
        print(f"PID: {server.pid or 'Not running'}")
        print(f"Created: {server.created}")
        print(f"Started: {server.started or 'Nie gestartet'}")
        print(f"Health Check: {server.health_check or 'None'}")
        
        if server.pid and server.status == "running":
            try:
                proc = psutil.Process(server.pid)
                print(f"Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"CPU: {proc.cpu_percent():.1f}%")
                print(f"Running since: {datetime.fromtimestamp(proc.create_time()).isoformat()}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print("Process information not available")
        
        return True

def main():
    """Main function - CLI Interface"""
    parser = argparse.ArgumentParser(
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
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ps command
    ps_parser = subparsers.add_parser('ps', help='Show MCP servers')
    ps_parser.add_argument('-a', '--all', action='store_true', help='Show all servers (including stopped)')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create new MCP server')
    create_parser.add_argument('name', help='Server name')
    create_parser.add_argument('server_command', help='Command to start the server')
    create_parser.add_argument('--config', help='Path to configuration file')
    create_parser.add_argument('--health-check', help='Health check command')
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start MCP server')
    start_parser.add_argument('name', help='Server name')
    
    # stop command
    stop_parser = subparsers.add_parser('stop', help='Stop MCP server')
    stop_parser.add_argument('name', help='Server name')
    
    # restart command
    restart_parser = subparsers.add_parser('restart', help='Restart MCP server')
    restart_parser.add_argument('name', help='Server name')
    
    # remove command
    rm_parser = subparsers.add_parser('rm', help='Remove MCP server')
    rm_parser.add_argument('name', help='Server name')
    rm_parser.add_argument('-f', '--force', action='store_true', help='Force removal even if server is running')
    
    # logs command
    logs_parser = subparsers.add_parser('logs', help='Show server logs')
    logs_parser.add_argument('name', help='Server name')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='Follow live logs')
    logs_parser.add_argument('--tail', type=int, default=50, help='Number of lines to show from end (default: 50)')
    
    # inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Show detailed server information')
    inspect_parser.add_argument('name', help='Server name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MCPManager()
    
    try:
        if args.command == 'ps':
            manager.ps(all_servers=args.all)
        elif args.command == 'create':
            manager.create(args.name, args.server_command, args.config or "", args.health_check or "")
        elif args.command == 'start':
            manager.start(args.name)
        elif args.command == 'stop':
            manager.stop(args.name)
        elif args.command == 'restart':
            manager.restart(args.name)
        elif args.command == 'rm':
            manager.remove(args.name, args.force)
        elif args.command == 'logs':
            manager.logs(args.name, args.follow, args.tail)
        elif args.command == 'inspect':
            manager.inspect(args.name)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nAborted.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()