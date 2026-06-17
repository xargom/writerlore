#!/bin/zsh
WRITERLORE_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "$(date) started, HOME=$HOME" >> /tmp/writerlore-mcp.log
[ -f "$WRITERLORE_DIR/.env" ] && source "$WRITERLORE_DIR/.env"
echo "$(date) MONGO=${WRITERLORE_MONGO_URI:0:20}" >> /tmp/writerlore-mcp.log
exec "$WRITERLORE_DIR/.venv/bin/writerlore" "$@" 2>>/tmp/writerlore-mcp.log
