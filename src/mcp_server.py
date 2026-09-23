from pathlib import Path
from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from context_engine.engine import DEFAULT_CONTEXT_BUDGET, build_context
from repository.scanner import scan_repository


mcp = MCPServer(
    "agentic-dev-harness",
    description="Read-only context retrieval for local source repositories.",
)


@mcp.tool()
def search_repository_context(
    repo_path: str,
    task: str,
    max_tokens: int = DEFAULT_CONTEXT_BUDGET,
) -> dict[str, Any]:
    """Retrieve relevant repository context for a development task.

    repo_path must be an absolute path on the machine running this server.
    Results are best-effort context, not a guarantee that every relevant file
    was found. This tool reads the repository and does not modify it.
    """
    if not repo_path.strip():
        raise ToolError("repo_path is required")

    repository_path = Path(repo_path).expanduser()

    if not repository_path.is_absolute():
        raise ToolError("repo_path must be an absolute path")

    repository_path = repository_path.resolve()

    if not repository_path.is_dir():
        raise ToolError(f"Repository directory does not exist: {repository_path}")

    if not task.strip():
        raise ToolError("task is required")

    if max_tokens <= 0:
        raise ToolError("max_tokens must be greater than zero")

    repository = scan_repository(repository_path)
    bundle = build_context(
        repository=repository,
        task=task.strip(),
        max_tokens=max_tokens,
    )

    return {
        "repository_name": bundle.repository_name,
        "task": bundle.task,
        "max_tokens": bundle.max_tokens,
        "items": [
            {
                "kind": item.kind,
                "source": item.source,
                "priority": item.priority,
                "content": item.content,
            }
            for item in bundle.items
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
