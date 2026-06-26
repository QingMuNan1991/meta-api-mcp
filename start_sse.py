"""SSE wrapper for meta-api MCP server.

Starts the META API MCP server in Streamable HTTP mode (port 8101),
avoiding stdio compatibility issues with Codex CLI.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.mcp_server import mcp

mcp.settings.host = "127.0.0.1"
mcp.settings.port = 8101
mcp.settings.streamable_http_path = "/mcp"

if __name__ == "__main__":
    print(f"Starting meta-api MCP server on http://127.0.0.1:8101/mcp", flush=True)
    mcp.run(transport="streamable-http")
