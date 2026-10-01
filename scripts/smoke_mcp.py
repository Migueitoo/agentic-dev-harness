"""Exercise the single MCP tool against a disposable Git repository."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters


ROOT = Path(__file__).resolve().parents[1]
TOOL = "create_repository_map"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


async def smoke(repo: Path) -> None:
    server = StdioServerParameters(
        command=sys.executable, args=[str(ROOT / "src" / "mcp_server.py")], cwd=str(ROOT)
    )
    async with Client(server, read_timeout_seconds=60) as client:
        listing = await client.list_tools()
        names = {item.name for item in listing.tools}
        if names != {TOOL}:
            raise RuntimeError(f"Expected only {TOOL}; found {sorted(names)}")
        result = await client.call_tool(TOOL, arguments={"repo_path": str(repo)}, read_timeout_seconds=60)
        if result.is_error:
            raise RuntimeError(str(result.content))
        payload = result.structured_content
        if payload is None:
            block = next(item for item in result.content if hasattr(item, "text"))
            payload = json.loads(block.text)
        if not isinstance(payload, dict) or not (repo / "REPOSITORY_MAP.md").is_file():
            raise RuntimeError("MCP did not create a repository map")
        for name in ("AGENTS.md", "CLAUDE.md"):
            if "REPOSITORY_MAP.md" not in (repo / name).read_text(encoding="utf-8"):
                raise RuntimeError(f"Missing map reference in {name}")
        print(f"MCP: {TOOL} OK")
        print(f"Files inventoried: {payload['files_inventoried']}")
        print(f"Changed: {', '.join(payload['changed_files'])}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="repository-map-smoke-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q")
        (repo / "Example.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup>'
            '<TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>', encoding="utf-8"
        )
        git(repo, "add", "Example.csproj")
        git(repo, "-c", "user.name=Smoke", "-c", "user.email=smoke@example.invalid", "commit", "-qm", "fixture")
        asyncio.run(smoke(repo))


if __name__ == "__main__":
    main()
