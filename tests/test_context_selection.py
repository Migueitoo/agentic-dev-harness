import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from context_engine.engine import retrieve_context, select_diverse_code_items
from context_engine.models import ContextItem


def code(source: str, scope: str) -> ContextItem:
    return ContextItem("code", source, source, 60, scope)


class ContextSelectionTests(unittest.TestCase):
    def test_diversity_keeps_one_file_per_scope_before_filling(self):
        ranked = [
            code("Tests/test_a.py#chunk-1", "Tests"),
            code("Tests/test_a.py#chunk-2", "Tests"),
            code("Tests/test_b.py#chunk-1", "Tests"),
            code("App/controller.py#chunk-1", "App"),
            code("Core/service.py#chunk-1", "Core"),
        ]

        selected = select_diverse_code_items(ranked, 4)

        self.assertEqual(
            [item.source for item in selected],
            [
                "Tests/test_a.py#chunk-1",
                "App/controller.py#chunk-1",
                "Core/service.py#chunk-1",
                "Tests/test_b.py#chunk-1",
            ],
        )

    def test_code_and_documents_have_separate_candidate_pools(self):
        items = [
            ContextItem("instructions", "AGENTS.md#chunk-1", "rules", 130),
            *[
                ContextItem("instructions", f"README.md#chunk-{i}", "docs", 100)
                for i in range(1, 25)
            ],
            code("App/controller.py#chunk-1", "App"),
            code("Core/service.py#chunk-1", "Core"),
        ]

        with patch("context_engine.engine.apply_hybrid_scores"), patch(
            "context_engine.engine.rerank_items", side_effect=lambda _task, pool, top_k: pool[:top_k]
        ):
            selected = retrieve_context(items, "Add endpoint")

        sources = [item.source for item in selected]
        self.assertIn("AGENTS.md#chunk-1", sources)
        self.assertIn("App/controller.py#chunk-1", sources)
        self.assertIn("Core/service.py#chunk-1", sources)
        self.assertEqual(sum(source.startswith("README.md") for source in sources), 1)


if __name__ == "__main__":
    unittest.main()
