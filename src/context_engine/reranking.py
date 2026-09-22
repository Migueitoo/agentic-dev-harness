from sentence_transformers import CrossEncoder

from .models import ContextItem

RERANKER_MODEL_NAME = "cross-encoder/" "mmarco-mMiniLMv2-L12-H384-v1"

_model = None


def get_reranker_model() -> CrossEncoder:
    global _model

    if _model is None:
        _model = CrossEncoder(RERANKER_MODEL_NAME)

    return _model


def rerank_items(
    task: str | None,
    items: list[ContextItem],
    top_k: int = 5,
) -> list[ContextItem]:
    if not task or not items:
        return items[:top_k]

    model = get_reranker_model()

    pairs = [
        (
            task,
            item.content,
        )
        for item in items
    ]

    scores = model.predict(
        pairs,
        convert_to_numpy=True,
    )

    ranked_items = sorted(
        zip(
            items,
            scores,
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )

    return [item for item, _ in ranked_items[:top_k]]
