import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "evals"))

from code_retrieval_cases import CODE_RETRIEVAL_SUITES, ExpectedCode
from context_engine.engine import build_context
from repository.scanner import scan_repository


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evalúa el código presente en el ContextBundle."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Ruta del repositorio a evaluar",
    )
    parser.add_argument(
        "--suite",
        choices=sorted(CODE_RETRIEVAL_SUITES),
        default="findthatbook",
        help="Conjunto de casos correspondiente al repositorio",
    )
    args = parser.parse_args()

    repository = scan_repository(Path(args.repo))
    cases = CODE_RETRIEVAL_SUITES[args.suite]
    passed_cases = 0

    print(f"Suite: {args.suite}")
    print(f"Repositorio: {repository.name}")

    for case in cases:
        if evaluate_case(repository, case.task, case.expected_code):
            passed_cases += 1

    print()
    print(f"Resultado: {passed_cases}/{len(cases)} casos aprobados")

    return 0 if passed_cases == len(cases) else 1


def evaluate_case(
    repository,
    task: str,
    expected_code: tuple[ExpectedCode, ...],
) -> bool:
    bundle = build_context(repository, task=task)
    code_items = [item for item in bundle.items if item.kind == "code"]

    matches = [
        any(
            item.source.split("#chunk-", 1)[0] == expected.source
            and (expected.contains is None or expected.contains in item.content)
            for item in code_items
        )
        for expected in expected_code
    ]

    coverage = sum(matches) / len(expected_code)
    passed = all(matches)

    print()
    print(f"Tarea: {task}")
    print("Esperado:")

    for expected, matched in zip(expected_code, matches):
        detail = f" | contiene: {expected.contains}" if expected.contains else ""
        print(f"- {'OK' if matched else 'FALTA'} " f"{expected.source}{detail}")

    print("Chunks de código en el ContextBundle:")

    for item in code_items:
        print(f"- {item.source}")

    print(f"Cobertura en ContextBundle: {coverage:.2f}")
    print(f"Resultado: {'PASS' if passed else 'FAIL'}")

    return passed


if __name__ == "__main__":
    raise SystemExit(main())
