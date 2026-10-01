"""MCP entry point for durable, source-backed repository maps."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from repository.mapping import map_repository


mcp = MCPServer(
    "agentic-dev-harness",
    description="Inspect a local Git repository and maintain its agent-facing map.",
)


@mcp.tool()
def create_repository_map(repo_path: str) -> dict[str, Any]:
    """Map one local Git repository and write REPOSITORY_MAP.md.

    Also creates or updates a short REPOSITORY_MAP.md reference in the root
    AGENTS.md and CLAUDE.md files. Existing instructions are preserved. Pass the
    absolute repository root; invoke once per repository. This tool changes only
    those three documentation files in the selected repository, never source code.
    """
    try:
        return map_repository(repo_path)
    except (OSError, ValueError) as exc:
        raise ToolError(str(exc)) from exc


if __name__ == "__main__":
    mcp.run(transport="stdio")
