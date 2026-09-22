from .models import ContextItem


def estimate_tokens(text: str) -> int:
    if not text:
        return 0

    return max(
        1,
        len(text) // 4,
    )


def apply_context_budget(
    items: list[ContextItem],
    max_tokens: int,
) -> list[ContextItem]:
    sorted_items = sorted(
        items,
        key=lambda item: item.priority,
        reverse=True,
    )

    selected_items = []
    used_tokens = 0

    for item in sorted_items:
        item_tokens = estimate_tokens(item.content)

        if used_tokens + item_tokens > max_tokens:
            continue

        selected_items.append(item)
        used_tokens += item_tokens

    return selected_items
