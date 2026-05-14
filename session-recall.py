#!/usr/bin/env python3
"""Surface relevant WriterLore memories at session start."""
import json
import os
import subprocess
import sys


def get_repo():
    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return remote.split("/")[-1].replace(".git", "")
    except Exception:
        return None


def get_ticket():
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        parts = branch.split("-")
        if len(parts) >= 2 and parts[0].isupper():
            return f"{parts[0]}-{parts[1]}"
    except Exception:
        pass
    return None


def load_env():
    config_path = os.path.expanduser("~/.mcp.json")
    with open(config_path) as f:
        config = json.load(f)
    env = config["mcpServers"]["writerlore"]["env"]
    os.environ["WRITERLORE_MONGO_URI"] = env["WRITERLORE_MONGO_URI"]


def main():
    try:
        load_env()

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        from writerlore.db import get_collection
        from writerlore.embeddings import embed_query

        repo = get_repo()
        ticket = get_ticket()

        query = f"documentation patterns editorial decisions{' ' + ticket if ticket else ''}"
        vector = embed_query(query)

        vector_search = {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": vector,
            "numCandidates": 30,
            "limit": 3,
        }
        if repo:
            vector_search["filter"] = {
                "$or": [
                    {"primary_repo": repo},
                    {"also_relevant_for": repo},
                ]
            }

        pipeline = [
            {"$vectorSearch": vector_search},
            {"$project": {"_id": 0, "content": 1, "score": {"$meta": "vectorSearchScore"}}},
        ]

        results = list(get_collection().aggregate(pipeline))

        if results:
            print("  🧠 WriterLore:")
            for r in results:
                content = r["content"]
                if len(content) > 120:
                    content = content[:117] + "..."
                print(f"     • {content}")

    except Exception:
        pass


if __name__ == "__main__":
    main()
