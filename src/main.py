"""Preview or write a deterministic repository map without starting MCP."""

from __future__ import annotations

import argparse
import json

from repository.mapping import inspect_repository, map_repository, render_repository_map


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Absolute Git repository root")
    parser.add_argument("--write", action="store_true", help="Write map and agent references")
    args = parser.parse_args()
    if args.write:
        print(json.dumps(map_repository(args.repo), ensure_ascii=False, indent=2))
    else:
        print(render_repository_map(inspect_repository(args.repo)), end="")


if __name__ == "__main__":
    main()
