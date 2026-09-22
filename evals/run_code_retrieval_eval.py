import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

sys.path.insert(
    0,
    str(PROJECT_ROOT / "evals"),
)

from code_retrieval_cases import CODE_RETRIEVAL_CASES
from context_engine.engine import build_context
from repository.scanner import scan_repository


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Evalúa la recuperación de " "código relevante.")
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Ruta del repositorio a evaluar",
    )

    args = parser.parse_args()

    repository = scan_repository(Path(args.repo))

    passed_cases = 0

    for case in CODE_RETRIEVAL_CASES:
        passed = evaluate_case(
            repository,
            case.task,
            case.expected_sources,
        )

        if passed:
            passed_cases += 1

    total_cases = len(CODE_RETRIEVAL_CASES)

    print()
    print(f"Resultado: " f"{passed_cases}/{total_cases} " f"casos aprobados")

    return 0 if passed_cases == total_cases else 1


def evaluate_case(
    repository,
    task: str,
    expected_sources: tuple[str, ...],
) -> bool:
    bundle = build_context(
        repository,
        task=task,
    )

    retrieved_sources = [item.source for item in bundle.items if item.kind == "code"]

    matched_sources = [
        expected_source
        for expected_source in expected_sources
        if any(source.startswith(expected_source) for source in retrieved_sources)
    ]

    recall = len(matched_sources) / len(expected_sources)

    passed = recall == 1.0

    print()
    print(f"Tarea: {task}")
    print("Esperado: " f"{', '.join(expected_sources)}")

    print("Recuperado:")

    for source in retrieved_sources:
        print(f"- {source}")

    print(f"Recall@5: {recall:.2f}")
    print("Resultado: " f"{'PASS' if passed else 'FAIL'}")

    return passed


if __name__ == "__main__":
    raise SystemExit(main())
