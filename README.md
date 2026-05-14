# WriterLore

A personal, human-curated semantic memory layer for AI-assisted documentation work. Built as a custom MCP server backed by MongoDB Atlas.

## What it does

Every Claude Code session starts from zero. Context about editorial decisions, structural patterns, and cross-repo choices lives in markdown files that don't scale and can't reason about relevance. WriterLore lets you save a decision once and surface it automatically in future sessions — in any repo.

It is **not** an automatic capture system. You decide what is worth keeping.

## How it works

WriterLore exposes two MCP tools to Claude Code:

- **`writerlore_save`** — explicitly save an editorial decision, pattern, or workflow quirk to MongoDB. The current repo and Jira ticket are auto-detected from `git remote` and the branch name. If no ticket is found in the branch name, Claude looks it up in Jira before saving.
- **`writerlore_recall`** — semantic search across saved memories, optionally filtered by repo.

At session start, a hook queries MongoDB and injects the top 3 relevant memories into the session context automatically.

## Stack

| Component | Choice |
| --- | --- |
| Language | Python 3.9+ |
| Database | MongoDB Atlas — `writerLore.memories` |
| Embeddings | `all-MiniLM-L6-v2` via `sentence-transformers` (384 dims, local) |
| MCP server | FastMCP (`mcp>=1.0`) |
| MCP config | `~/.mcp.json` |

## Prerequisites

- Python 3.9+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) cluster (free tier works)
- [Claude Code](https://claude.ai/code) CLI

## Setup

```bash
git clone https://github.com/xargom/writerlore
cd writerlore
bash setup.sh
```

`setup.sh` will:

1. Create a `.venv` and install dependencies
2. Register the MCP server in `~/.mcp.json` (prompts for your Atlas connection string)
3. Register the session hook in `~/.claude/settings.json`
4. Print the Atlas Vector Search index definition to create manually

Restart Claude Code after setup completes.

## Atlas Vector Search index

Create a vector index named `vector_index` on the `memories` collection in the `writerLore` database:

```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },
    { "type": "filter", "path": "primary_repo" },
    { "type": "filter", "path": "also_relevant_for" },
    { "type": "filter", "path": "components" }
  ]
}
```

## Memory schema

```python
{
  "content": str,              # The editorial decision or pattern
  "primary_repo": str,         # Auto-detected from git remote
  "also_relevant_for": [str],  # Other repos this applies to
  "ticket": str | None,        # Auto-detected from branch name, or Jira lookup
  "components": [str],           # e.g. ["Atlas Search", "Vector Search"]
  "saved_at": datetime,        # UTC
  "embedding": [float],        # 384-dim local sentence-transformers vector
}
```

## Usage

**Save a memory** — say this to Claude during a session:

> "Save to WriterLore: In Terraform module repos, always use absolute GitHub URLs for cross-file anchors because the template renders at two different directory depths."

**Recall on demand:**

> "What do I know about PR workflow for Terraform repos?"

**Automatic recall** happens at every session start — no action needed.

## Known limitations

- `session-recall.py` runs as a standalone hook and cannot reach MCP — ticket detection there is branch-name only.
- Memories are personal and not team-shared (v1 scope).
- The local model (`all-MiniLM-L6-v2`, ~90 MB) is downloaded on first use.
