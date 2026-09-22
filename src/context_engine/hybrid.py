from .models import ContextItem
from .retrieval import score_items_with_bm25
from .semantic import score_items_semantically

BM25_WEIGHT = 0.45
SEMANTIC_WEIGHT = 0.55


def score_items_hybrid(
    task: str | None,
    items: list[ContextItem],
) -> dict[str, float]:
    if not task or not items:
        return {}

    bm25_scores = score_items_with_bm25(
        task,
        items,
    )

    semantic_scores = score_items_semantically(
        task,
        items,
    )

    normalized_bm25 = normalize_scores(bm25_scores)

    normalized_semantic = normalize_scores(semantic_scores)

    hybrid_scores = {}

    for item in items:
        bm25_score = normalized_bm25.get(
            item.source,
            0.0,
        )

        semantic_score = normalized_semantic.get(
            item.source,
            0.0,
        )

        hybrid_scores[item.source] = (
            bm25_score * BM25_WEIGHT + semantic_score * SEMANTIC_WEIGHT
        )

    return hybrid_scores


def normalize_scores(
    scores: dict[str, float],
) -> dict[str, float]:
    if not scores:
        return {}

    positive_scores = {source: max(score, 0.0) for source, score in scores.items()}

    max_score = max(
        positive_scores.values(),
        default=0.0,
    )

    if max_score == 0:
        return {source: 0.0 for source in positive_scores}

    return {source: score / max_score for source, score in positive_scores.items()}
