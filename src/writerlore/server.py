from typing import Optional
from mcp.server.fastmcp import FastMCP

from .schema import Memory
from .db import get_collection
from .embeddings import embed, embed_query

mcp = FastMCP("writerlore")


@mcp.tool()
def writerlore_save(
    content: str,
    also_relevant_for: Optional[list] = None,
    ticket: Optional[str] = None,
    components: Optional[list] = None,
) -> str:
    """Save an editorial decision or documentation pattern to WriterLore memory.

    Before calling this tool:
    1. Run `git rev-parse --abbrev-ref HEAD` to get the current branch name.
    2. If the branch name matches a Jira ticket pattern (e.g. DOCSP-58142 —
       uppercase prefix, hyphen, digits), pass it as `ticket`.
    3. If the branch name has no ticket pattern, search Jira using the Atlassian
       MCP (jira_search) to identify the most relevant open ticket for the current
       work, then pass it as `ticket`. Do not leave ticket blank when a Jira ticket
       can be reasonably identified.
    4. Infer `components` from the current working context — e.g. the content
       directory name, the ticket component field in Jira, or the topic being
       discussed. Use human-readable component names (e.g. "Atlas Search",
       "Vector Search", "Ops Manager", "Atlas Architecture Center").
       Leave empty only if no component can be reasonably identified.
    """
    memory = Memory(content=content, also_relevant_for=also_relevant_for or [])
    if ticket is not None:
        memory.ticket = ticket
    if components is not None:
        memory.components = components
    memory.embedding = embed(content)
    result = get_collection().insert_one(memory.to_document())
    return f"Saved. id={result.inserted_id}"


@mcp.tool()
def writerlore_recall(
    query: str,
    repo: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 5,
) -> list:
    """Recall relevant editorial memories via semantic search, optionally filtered by repo and/or component."""
    vector = embed_query(query)

    vector_search: dict = {
        "index": "vector_index",
        "path": "embedding",
        "queryVector": vector,
        "numCandidates": limit * 10,
        "limit": limit,
    }

    filters = []
    if repo:
        filters.append({"$or": [{"primary_repo": repo}, {"also_relevant_for": repo}]})
    if component:
        filters.append({"components": component})
    if filters:
        vector_search["filter"] = {"$and": filters} if len(filters) > 1 else filters[0]

    pipeline = [
        {"$vectorSearch": vector_search},
        {
            "$project": {
                "_id": 0,
                "content": 1,
                "primary_repo": 1,
                "ticket": 1,
                "saved_at": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(get_collection().aggregate(pipeline))


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
