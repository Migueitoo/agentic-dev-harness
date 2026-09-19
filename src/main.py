import argparse
from pathlib import Path

from repository.scanner import scan_repository


def main():
    parser = argparse.ArgumentParser(
        description="Analiza la estructura y metadata de un repositorio."
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Ruta del repositorio a analizar",
    )

    args = parser.parse_args()

    repo_info = scan_repository(Path(args.repo))

    print(repo_info)


if __name__ == "__main__":
    main()
