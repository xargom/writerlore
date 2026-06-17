#!/bin/bash
# WriterLore setup — run once per machine to wire up MCP server and session hook.
# Prerequisites: Python 3.9+, a MongoDB Atlas cluster, a Voyage AI API key.

set -e

WRITERLORE_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_CONFIG="$HOME/.mcp.json"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

echo "=== WriterLore setup ==="
echo "Project: $WRITERLORE_DIR"

# ── 1. Python venv + dependencies ─────────────────────
echo ""
echo "1. Installing dependencies..."
python3 -m venv "$WRITERLORE_DIR/.venv"
"$WRITERLORE_DIR/.venv/bin/pip" install -e "$WRITERLORE_DIR" -q
echo "   Done."

# ── 2. .mcp.json — register MCP server ────────────────
echo ""
echo "2. Registering MCP server in $MCP_CONFIG"
echo "   You need one credential:"
echo ""
read -r -p "   WRITERLORE_MONGO_URI: " MONGO_URI
echo ""

# Add or update the writerlore entry using Python's json module.
# Variables are passed via env to avoid bash string interpolation into JSON values.
SETUP_MONGO_URI="$MONGO_URI" \
SETUP_MCP_CONFIG="$MCP_CONFIG" \
SETUP_WRITERLORE_DIR="$WRITERLORE_DIR" \
python3 - <<'EOF'
import json, os

mongo_uri = os.environ["SETUP_MONGO_URI"]
path = os.environ["SETUP_MCP_CONFIG"]
writerlore_dir = os.environ["SETUP_WRITERLORE_DIR"]

config = {}
if os.path.exists(path):
    with open(path) as f:
        config = json.load(f)

config.setdefault("mcpServers", {})["writerlore"] = {
    "type": "stdio",
    "command": f"{writerlore_dir}/.venv/bin/python",
    "args": ["-m", "writerlore.server"],
    "env": {
        "WRITERLORE_MONGO_URI": mongo_uri,
    },
}

with open(path, "w") as f:
    json.dump(config, f, indent=2)
print("   Written.")
EOF

# ── 3. settings.json — register session hook ──────────
echo ""
echo "3. Registering session hook in $CLAUDE_SETTINGS"

SETUP_CLAUDE_SETTINGS="$CLAUDE_SETTINGS" \
SETUP_WRITERLORE_DIR="$WRITERLORE_DIR" \
python3 - <<'EOF'
import json, os

path = os.environ["SETUP_CLAUDE_SETTINGS"]
writerlore_dir = os.environ["SETUP_WRITERLORE_DIR"]

if not os.path.exists(path):
    print(f"   {path} not found — skipping.")
    exit(0)

with open(path) as f:
    config = json.load(f)

hook_cmd = f"{writerlore_dir}/.venv/bin/python {writerlore_dir}/session-recall.py"
hook_entry = {"type": "command", "command": hook_cmd}

sessions = config.setdefault("hooks", {}).setdefault("SessionStart", [])
if not sessions:
    sessions.append({"hooks": []})

hooks = sessions[0].setdefault("hooks", [])
if not any(h.get("command") == hook_cmd for h in hooks):
    hooks.append(hook_entry)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print("   Hook added.")
else:
    print("   Hook already registered.")
EOF

# ── 4. Atlas Vector Search index reminder ─────────────
echo ""
echo "4. Atlas Vector Search index"
echo "   Create a vector index named 'vector_index' on the 'memories' collection:"
echo ""
echo '   { "fields": ['
echo '       { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },'
echo '       { "type": "filter", "path": "primary_repo" },'
echo '       { "type": "filter", "path": "also_relevant_for" }'
echo '   ]}'
echo ""
echo "=== Setup complete. Restart Claude Code to activate. ==="
