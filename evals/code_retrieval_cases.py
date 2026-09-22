import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExpectedCode:
    source: str
    contains: str | None = None


@dataclass(frozen=True)
class CodeRetrievalCase:
    name: str
    task: str
    expected_code: tuple[ExpectedCode, ...]


def load_suites(path: Path) -> dict[str, tuple[CodeRetrievalCase, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    return {
        suite_name: tuple(
            CodeRetrievalCase(
                name=case["name"],
                task=case["task"],
                expected_code=tuple(
                    ExpectedCode(**expected) for expected in case["expected_code"]
                ),
            )
            for case in cases
        )
        for suite_name, cases in data.items()
    }


CODE_RETRIEVAL_SUITES = load_suites(Path(__file__).with_suffix(".json"))
