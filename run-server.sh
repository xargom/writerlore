#!/bin/zsh
echo "$(date) started, HOME=$HOME" >> /tmp/writerlore-mcp.log
source ~/.zprofile 2>/dev/null
source ~/.zshrc 2>/dev/null
echo "$(date) MONGO=${WRITERLORE_MONGO_URI:0:20}" >> /tmp/writerlore-mcp.log
exec /Users/javierarmendariz/writerlore/.venv/bin/writerlore "$@" 2>>/tmp/writerlore-mcp.log
