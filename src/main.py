import argparse
from pathlib import Path

from repository.scanner import scan_repository
from context_engine.engine import (
    build_context,
    render_context,
)


def main():
    parser = argparse.ArgumentParser(
        description=("Analiza un repositorio y construye " "contexto para agentes.")
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Ruta del repositorio a analizar",
    )

    parser.add_argument(
        "--context",
        action="store_true",
        help="Construye el contexto del repositorio",
    )

    parser.add_argument(
        "--task",
        required=False,
        help="Tarea para la cual se construye el contexto",
    )

    args = parser.parse_args()

    repo_info = scan_repository(Path(args.repo))

    if args.context:
        context = build_context(
            repository=repo_info,
            task=args.task,
        )

        print(render_context(context))
        return

    print(repo_info)


if __name__ == "__main__":
    main()
