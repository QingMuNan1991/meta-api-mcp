"""Install meta-api-mcp to CodeBuddy MCP config."""
import json
import sys
from pathlib import Path

CODEBUDDY_CONFIG = Path.home() / ".codebuddy" / "mcp.json"

# Ensure directory exists
CODEBUDDY_CONFIG.parent.mkdir(parents=True, exist_ok=True)

# Read existing config
if CODEBUDDY_CONFIG.exists():
    config = json.loads(CODEBUDDY_CONFIG.read_text(encoding="utf-8"))
else:
    config = {}

servers = config.setdefault("mcpServers", {})

if "meta-api" in servers:
    print(f"[SKIP] meta-api already registered in {CODEBUDDY_CONFIG}")
    sys.exit(0)

# Get python path
python_exe = sys.executable
meta_api_mcp_path = str(Path(__file__).parent / "tools" / "mcp_server.py")

servers["meta-api"] = {
    "type": "stdio",
    "command": python_exe,
    "args": ["-m", "tools"],
    "env": {
        "PYTHONPATH": str(Path(__file__).parent),
    },
}

CODEBUDDY_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"[OK] meta-api MCP registered → {CODEBUDDY_CONFIG}")
print(f"     command: {python_exe} -m tools")
print()
print("Restart CodeBuddy to activate.")
