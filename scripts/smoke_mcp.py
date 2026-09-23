import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_SCRIPT = PROJECT_ROOT / "src" / "mcp_server.py"
TOOL_NAME = "search_repository_context"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verifica el servidor MCP local mediante stdio."
    )
    parser.add_argument("--repo", required=True, help="Ruta absoluta del repositorio")
    parser.add_argument("--task", required=True, help="Tarea de desarrollo")
    parser.add_argument("--max-tokens", type=int, default=2000)
    return parser.parse_args()


def extract_payload(result: Any) -> dict[str, Any]:
    payload = result.structured_content

    if payload is None:
        text = next(
            (block.text for block in result.content if hasattr(block, "text")),
            None,
        )
        if text is None:
            raise RuntimeError("La herramienta no devolvió contenido JSON")
        payload = json.loads(text)

    if not isinstance(payload, dict):
        raise RuntimeError("La herramienta no devolvió un objeto JSON")

    return payload


async def run(repo_path: Path, task: str, max_tokens: int) -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
    )

    async with Client(server, read_timeout_seconds=300) as client:
        available = await client.list_tools()
        names = {tool.name for tool in available.tools}

        if TOOL_NAME not in names:
            raise RuntimeError(f"La herramienta {TOOL_NAME} no fue registrada")

        result = await client.call_tool(
            TOOL_NAME,
            arguments={
                "repo_path": str(repo_path),
                "task": task,
                "max_tokens": max_tokens,
            },
            read_timeout_seconds=300,
        )

        if result.is_error:
            raise RuntimeError(f"La herramienta devolvió un error: {result.content}")

        payload = extract_payload(result)

        if payload.get("repository_name") != repo_path.name:
            raise RuntimeError("El resultado corresponde a otro repositorio")

        items = payload.get("items")
        if not isinstance(items, list):
            raise RuntimeError("El resultado no contiene una lista de items")

        print(f"MCP: {TOOL_NAME} OK")
        print(f"Repositorio: {payload['repository_name']}")
        print(f"Items: {len(items)}")
        for item in items:
            print(f"- {item['kind']}: {item['source']}")


def main() -> None:
    args = parse_args()
    repo_path = Path(args.repo).expanduser().resolve()
    asyncio.run(run(repo_path, args.task, args.max_tokens))


if __name__ == "__main__":
    main()
