#!/usr/bin/env python3
"""
MCP Management System - Docker-like interface for MCP servers

Version: 2.0.0 (Refactored with clean class architecture)
"""

import sys
from pathlib import Path

# Add the current directory to Python path so we can import mcp module
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from mcp.main import main
except ImportError as e:
    print(f"Error importing MCP modules: {e}")
    print("Make sure all required dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())