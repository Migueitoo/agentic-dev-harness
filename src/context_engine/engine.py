from pathlib import Path

from repository.models import RepositoryInfo

from .budget import apply_context_budget
from .chunking import chunk_markdown
from .hybrid import score_items_hybrid
from .models import ContextBundle, ContextItem
from .reranking import rerank_items
from .scoring import score_project

DEFAULT_CONTEXT_BUDGET = 2000

HYBRID_PRIORITY_MULTIPLIER = 30
MAX_HYBRID_BOOST = 30

MAX_HYBRID_CANDIDATES = 20
MAX_RERANKED_ITEMS = 5

RERANKED_PRIORITY_START = 99


def build_context(
    repository: RepositoryInfo,
    task: str | None = None,
    max_tokens: int = DEFAULT_CONTEXT_BUDGET,
) -> ContextBundle:
    items = []

    items.append(build_repository_summary(repository))

    items.extend(
        build_project_context(
            repository,
            task,
        )
    )

    instruction_items = build_instruction_context(repository)

    selected_instruction_items = retrieve_instruction_context(
        instruction_items,
        task,
    )

    items.extend(selected_instruction_items)

    selected_items = apply_context_budget(
        items,
        max_tokens,
    )

    return ContextBundle(
        repository_name=repository.name,
        task=task,
        items=selected_items,
        max_tokens=max_tokens,
    )


def retrieve_instruction_context(
    items: list[ContextItem],
    task: str | None,
) -> list[ContextItem]:
    if not task:
        return items

    apply_hybrid_scores(
        items,
        task,
    )

    hybrid_candidates = select_top_items(
        items,
        MAX_HYBRID_CANDIDATES,
    )

    reranked_items = rerank_items(
        task,
        hybrid_candidates,
        top_k=MAX_RERANKED_ITEMS,
    )

    apply_reranking_priorities(reranked_items)

    return reranked_items


def select_top_items(
    items: list[ContextItem],
    top_k: int,
) -> list[ContextItem]:
    sorted_items = sorted(
        items,
        key=lambda item: item.priority,
        reverse=True,
    )

    return sorted_items[:top_k]


def apply_hybrid_scores(
    items: list[ContextItem],
    task: str | None,
) -> None:
    scores = score_items_hybrid(
        task,
        items,
    )

    for item in items:
        hybrid_score = scores.get(
            item.source,
            0.0,
        )

        boost = int(hybrid_score * HYBRID_PRIORITY_MULTIPLIER)

        boost = min(
            boost,
            MAX_HYBRID_BOOST,
        )

        item.priority += boost


def apply_reranking_priorities(
    items: list[ContextItem],
) -> None:
    for index, item in enumerate(items):
        item.priority = RERANKED_PRIORITY_START - index


def build_repository_summary(
    repository: RepositoryInfo,
) -> ContextItem:
    languages = ", ".join(repository.languages) or "Unknown"

    frameworks = ", ".join(repository.frameworks) or "None"

    capabilities = ", ".join(repository.capabilities) or "None"

    content = (
        f"Repository: {repository.name}\n"
        f"Branch: "
        f"{repository.current_branch or 'Unknown'}\n"
        f"Languages: {languages}\n"
        f"Frameworks: {frameworks}\n"
        f"Capabilities: {capabilities}"
    )

    return ContextItem(
        kind="repository_summary",
        source="repository",
        content=content,
        priority=100,
    )


def build_project_context(
    repository: RepositoryInfo,
    task: str | None,
) -> list[ContextItem]:
    items = []

    for project in repository.projects:
        references = ", ".join(project.project_references) or "None"

        packages = (
            ", ".join(
                format_package_reference(
                    package.name,
                    package.version,
                )
                for package in project.package_references
            )
            or "None"
        )

        content = (
            f"Project: {project.name}\n"
            f"Type: {project.project_type}\n"
            f"SDK: {project.sdk or 'Unknown'}\n"
            f"Target framework: "
            f"{project.target_framework or 'Unknown'}\n"
            f"Test framework: "
            f"{project.test_framework or 'None'}\n"
            f"Project references: "
            f"{references}\n"
            f"Packages: {packages}"
        )

        items.append(
            ContextItem(
                kind="project",
                source=project.name,
                content=content,
                priority=score_project(
                    project,
                    task,
                ),
            )
        )

    return items


def build_instruction_context(
    repository: RepositoryInfo,
) -> list[ContextItem]:
    items = []

    for filename in repository.context_files:
        file_path = repository.path / filename

        content = read_text_file(file_path)

        if content is None:
            continue

        chunks = chunk_markdown(content)

        base_priority = context_file_priority(filename)

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            items.append(
                ContextItem(
                    kind="instructions",
                    source=(f"{filename}" f"#chunk-{index}"),
                    content=chunk,
                    priority=base_priority,
                )
            )

    return items


def context_file_priority(
    filename: str,
) -> int:
    filename = filename.upper()

    if filename == "AGENTS.MD":
        return 100

    if filename == "CLAUDE.MD":
        return 100

    if filename == "README.MD":
        return 70

    return 50


def read_text_file(
    file_path: Path,
) -> str | None:
    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError:
        return None


def format_package_reference(
    name: str,
    version: str | None,
) -> str:
    if version:
        return f"{name} ({version})"

    return name


def render_context(
    bundle: ContextBundle,
) -> str:
    sections = []

    sections.append(f"# Repository Context: " f"{bundle.repository_name}")

    sections.append(f"Context budget: " f"{bundle.max_tokens} " f"estimated tokens")

    if bundle.task:
        sections.append(f"## Task\n" f"{bundle.task}")

    sorted_items = sorted(
        bundle.items,
        key=lambda item: item.priority,
        reverse=True,
    )

    for item in sorted_items:
        sections.append(
            f"## {item.kind}: "
            f"{item.source}\n"
            f"Priority: "
            f"{item.priority}\n\n"
            f"{item.content}"
        )

    return "\n\n".join(sections)
