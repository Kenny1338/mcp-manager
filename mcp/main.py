"""
MCP Management System - Main Entry Point

This is the new, refactored main entry point that uses the
clean class-based architecture.
"""

import sys
from pathlib import Path

from .cli.parser import create_parser, validate_args
from .cli.commands import CommandHandler
from .core.exceptions import MCPError


def main():
    """
    Main entry point for the MCP Management System.
    
    This function:
    1. Parses command line arguments
    2. Validates input
    3. Dispatches to appropriate command handler
    4. Handles errors gracefully
    5. Returns appropriate exit code
    """
    # Create and parse arguments
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        args = parser.parse_args()
        
        # Validate arguments
        validation_error = validate_args(args)
        if validation_error:
            print(f"Error: {validation_error}", file=sys.stderr)
            return 1
        
        # Create command handler
        config_dir = Path(args.config_dir) if args.config_dir else None
        handler = CommandHandler(config_dir)
        
        # Dispatch to appropriate command handler
        exit_code = dispatch_command(handler, args)
        return exit_code
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130  # Standard exit code for Ctrl+C
    except MCPError as e:
        print(f"MCP Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def dispatch_command(handler: CommandHandler, args) -> int:
    """
    Dispatch to the appropriate command handler method.
    
    Args:
        handler: CommandHandler instance
        args: Parsed command arguments
        
    Returns:
        Exit code from the command handler
    """
    command_map = {
        'ps': handler.handle_ps,
        'create': handler.handle_create,
        'start': handler.handle_start,
        'stop': handler.handle_stop,
        'restart': handler.handle_restart,
        'rm': handler.handle_remove,
        'remove': handler.handle_remove,
        'logs': handler.handle_logs,
        'log': handler.handle_logs,
        'inspect': handler.handle_inspect,
    }
    
    command_func = command_map.get(args.command)
    if command_func:
        return command_func(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())