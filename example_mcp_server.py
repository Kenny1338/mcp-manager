#!/usr/bin/env python3
"""
Example MCP Server for testing the MCP Management System
Simulates a simple MCP server that runs for some time
"""

import time
import json
import sys
from datetime import datetime

def main():
    print(f"[{datetime.now().isoformat()}] MCP Test Server started")
    print(f"[{datetime.now().isoformat()}] PID: {sys.argv[0] if len(sys.argv) > 1 else 'unknown'}")
    
    # Simulate MCP Server initialization
    for i in range(3):
        print(f"[{datetime.now().isoformat()}] Initializing... {i+1}/3")
        time.sleep(1)
    
    print(f"[{datetime.now().isoformat()}] Server ready - waiting for connections")
    
    # Main loop - simulates a running server
    counter = 0
    try:
        while True:
            counter += 1
            print(f"[{datetime.now().isoformat()}] Heartbeat #{counter}")
            time.sleep(5)  # Heartbeat every 5 seconds
            
            # Simulate occasional activity
            if counter % 10 == 0:
                print(f"[{datetime.now().isoformat()}] Processing request #{counter//10}")
                
    except KeyboardInterrupt:
        print(f"[{datetime.now().isoformat()}] Shutdown signal received")
        print(f"[{datetime.now().isoformat()}] Cleaning up...")
        time.sleep(1)
        print(f"[{datetime.now().isoformat()}] Server terminated")

if __name__ == "__main__":
    main()