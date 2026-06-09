"""Setup meta-api-mcp for CodeBuddy."""
import json
import sys
import subprocess
from pathlib import Path

CODEBUDDY_CONFIG = Path.home() / ".codebuddy" / "mcp.json"
PROJECT_DIR = Path(__file__).parent.resolve()

# 1. Ensure package is installed
print("[1/3] Installing meta-api-mcp ...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-e", str(PROJECT_DIR)],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"  ERROR: {result.stderr}")
    sys.exit(1)
print("  OK")

# 2. Find meta-api-mcp executable
print("[2/3] Locating meta-api-mcp ...")
result = subprocess.run(
    ["where", "meta-api-mcp"],
    capture_output=True, text=True
)
exe_path = result.stdout.strip().splitlines()
if exe_path:
    exe_path = exe_path[0]
    print(f"  Found: {exe_path}")
else:
    # Fallback: use python -m tools
    exe_path = sys.executable
    print(f"  Using: {exe_path} -m tools")

# 3. Write CodeBuddy config
print(f"[3/3] Writing {CODEBUDDY_CONFIG} ...")
CODEBUDDY_CONFIG.parent.mkdir(parents=True, exist_ok=True)

if CODEBUDDY_CONFIG.exists():
    config = json.loads(CODEBUDDY_CONFIG.read_text(encoding="utf-8"))
else:
    config = {}

servers = config.setdefault("mcpServers", {})

if "meta-api" in servers:
    print(f"  SKIP: meta-api already registered")
    sys.exit(0)

if exe_path.endswith("meta-api-mcp.exe") or exe_path.endswith("meta-api-mcp"):
    servers["meta-api"] = {
        "type": "stdio",
        "command": exe_path,
        "args": [],
        "env": {},
    }
else:
    servers["meta-api"] = {
        "type": "stdio",
        "command": exe_path,
        "args": ["-m", "tools"],
        "env": {
            "PYTHONPATH": str(PROJECT_DIR),
        },
    }

CODEBUDDY_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
print("  DONE")
print()
print("=== meta-api MCP registered to CodeBuddy ===")
print(f"Config: {CODEBUDDY_CONFIG}")
print("Restart CodeBuddy to activate.")
