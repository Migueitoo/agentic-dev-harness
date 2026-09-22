from sentence_transformers import SentenceTransformer

from .models import ContextItem

MODEL_NAME = "sentence-transformers/" "paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def score_items_semantically(
    task: str | None,
    items: list[ContextItem],
) -> dict[str, float]:
    if not task or not items:
        return {}

    model = get_embedding_model()

    texts = [
        task,
        *[item.content for item in items],
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    task_embedding = embeddings[0]
    item_embeddings = embeddings[1:]

    scores = {}

    for item, embedding in zip(
        items,
        item_embeddings,
    ):
        similarity = float(task_embedding @ embedding)

        scores[item.source] = similarity

    return scores
