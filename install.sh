#!/bin/bash
# Installation Script für MCP Manager

set -e

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed!"
    exit 1
fi

echo "🔧 Installing MCP Manager..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt 2>/dev/null || pip install -r requirements.txt

# Make mcp.py executable
chmod +x mcp.py

# Create symbolic link
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SCRIPT="$SCRIPT_DIR/mcp.py"

# Check if /usr/local/bin is writable
if [ -w "/usr/local/bin" ]; then
    echo "🔗 Creating symbolic link in /usr/local/bin..."
    sudo ln -sf "$MCP_SCRIPT" /usr/local/bin/mcp
    echo "✅ MCP Manager successfully installed!"
    echo "   You can now run 'mcp ps' from anywhere."
else
    # Fallback: use ~/.local/bin
    mkdir -p ~/.local/bin
    echo "🔗 Creating symbolic link in ~/.local/bin..."
    ln -sf "$MCP_SCRIPT" ~/.local/bin/mcp
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "⚠️  ~/.local/bin is not in your PATH!"
        echo "   Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "   Then run: source ~/.bashrc"
        echo "   (or start a new terminal)"
    else
        echo "✅ MCP Manager successfully installed!"
        echo "   You can now run 'mcp ps' from anywhere."
    fi
fi

echo ""
echo "📚 Quick start:"
echo "   mcp create my-server \"python3 server.py\""
echo "   mcp start my-server"
echo "   mcp ps"
echo "   mcp logs my-server"
echo ""
echo "📖 For more help: mcp --help"