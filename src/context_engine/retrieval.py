import math
import re
import unicodedata

from .models import ContextItem

STOP_WORDS = {
    "a",
    "al",
    "de",
    "del",
    "el",
    "en",
    "la",
    "las",
    "lo",
    "los",
    "para",
    "por",
    "un",
    "una",
    "unos",
    "unas",
    "y",
    "o",
    "que",
    "con",
    "como",
    "the",
    "an",
    "and",
    "or",
    "to",
    "for",
    "of",
    "in",
    "on",
    "with",
}


def score_items_with_bm25(
    task: str | None,
    items: list[ContextItem],
) -> dict[str, float]:
    if not task or not items:
        return {}

    query_terms = tokenize(task)

    if not query_terms:
        return {}

    documents = [tokenize(item.content) for item in items]

    average_document_length = sum(len(document) for document in documents) / len(
        documents
    )

    document_frequencies = calculate_document_frequencies(documents)

    scores = {}

    for item, document in zip(
        items,
        documents,
    ):
        score = calculate_bm25_score(
            query_terms=query_terms,
            document=document,
            documents_count=len(documents),
            document_frequencies=document_frequencies,
            average_document_length=average_document_length,
        )

        scores[item.source] = score

    return scores


def calculate_bm25_score(
    query_terms: list[str],
    document: list[str],
    documents_count: int,
    document_frequencies: dict[str, int],
    average_document_length: float,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    if not document:
        return 0.0

    term_frequencies = {}

    for term in document:
        term_frequencies[term] = term_frequencies.get(term, 0) + 1

    score = 0.0

    for term in query_terms:
        frequency = term_frequencies.get(
            term,
            0,
        )

        if frequency == 0:
            continue

        document_frequency = document_frequencies.get(
            term,
            0,
        )

        inverse_document_frequency = math.log(
            1
            + (documents_count - document_frequency + 0.5) / (document_frequency + 0.5)
        )

        length_normalization = 1 - b + b * (len(document) / average_document_length)

        numerator = frequency * (k1 + 1)

        denominator = frequency + k1 * length_normalization

        score += inverse_document_frequency * (numerator / denominator)

    return score


def calculate_document_frequencies(
    documents: list[list[str]],
) -> dict[str, int]:
    frequencies = {}

    for document in documents:
        unique_terms = set(document)

        for term in unique_terms:
            frequencies[term] = frequencies.get(term, 0) + 1

    return frequencies


def tokenize(
    text: str,
) -> list[str]:
    normalized = normalize_text(text)

    raw_terms = re.findall(
        r"[a-z0-9]+",
        normalized,
    )

    return [
        normalize_term(term)
        for term in raw_terms
        if term not in STOP_WORDS and len(term) > 2
    ]


def normalize_text(
    text: str,
) -> str:
    text = text.lower()

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    return "".join(
        character for character in text if not unicodedata.combining(character)
    )


def normalize_term(
    term: str,
) -> str:
    if len(term) > 4 and term.endswith("s"):
        return term[:-1]

    return term
