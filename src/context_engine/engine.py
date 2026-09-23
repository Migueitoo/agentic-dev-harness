from pathlib import Path

from repository.models import RepositoryInfo

from .budget import apply_context_budget
from .chunking import chunk_markdown
from .code_chunking import chunk_code_documents
from .code_documents import build_code_documents
from .hybrid import score_items_hybrid
from .models import ContextBundle, ContextItem
from .reranking import rerank_items
from .scoring import score_project

DEFAULT_CONTEXT_BUDGET = 2000

HYBRID_PRIORITY_MULTIPLIER = 30
MAX_HYBRID_BOOST = 30

MAX_HYBRID_CANDIDATES = 20
MAX_RERANKED_CODE_ITEMS = 8
MAX_DOCUMENT_ITEMS = 1

RERANKED_CODE_PRIORITY_START = 120
CODE_CONTEXT_PRIORITY = 60


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

    code_items = build_code_context(repository)

    retrieval_items = [
        *instruction_items,
        *code_items,
    ]

    selected_retrieval_items = retrieve_context(
        retrieval_items,
        task,
    )

    items.extend(selected_retrieval_items)

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


def retrieve_context(
    items: list[ContextItem],
    task: str | None,
) -> list[ContextItem]:
    if not task:
        return items

    apply_hybrid_scores(items, task)

    code_items = [item for item in items if item.kind == "code"]
    instruction_items = [
        item
        for item in items
        if item.kind == "instructions" and is_instruction_file(item.source)
    ]
    document_items = [
        item
        for item in items
        if item.kind == "instructions" and not is_instruction_file(item.source)
    ]

    selected_code = rerank_context_items(code_items, task)
    selected_code = select_diverse_code_items(
        selected_code, MAX_RERANKED_CODE_ITEMS
    )
    apply_reranking_priorities(selected_code)

    selected_documents = select_top_items(document_items, MAX_DOCUMENT_ITEMS)

    return [*instruction_items, *selected_code, *selected_documents]


def is_instruction_file(source: str) -> bool:
    return source.split("#", 1)[0].upper() in {"AGENTS.MD", "CLAUDE.MD"}


def rerank_context_items(
    items: list[ContextItem], task: str
) -> list[ContextItem]:
    if not items:
        return []

    candidates = select_top_items(items, MAX_HYBRID_CANDIDATES)
    return rerank_items(task, candidates, top_k=len(candidates))


def select_diverse_code_items(
    ranked_items: list[ContextItem], top_k: int
) -> list[ContextItem]:
    if top_k <= 0:
        return []

    selected = []
    seen_files = set()
    seen_scopes = set()

    for distinct_scope in (True, False):
        for item in ranked_items:
            file_source = item.source.split("#chunk-", 1)[0]
            scope = item.scope or file_source

            if file_source in seen_files:
                continue
            if distinct_scope and scope in seen_scopes:
                continue

            selected.append(item)
            seen_files.add(file_source)
            seen_scopes.add(scope)

            if len(selected) == top_k:
                return selected

    return selected


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
        item.priority = RERANKED_CODE_PRIORITY_START - index


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


def build_code_context(
    repository: RepositoryInfo,
) -> list[ContextItem]:
    documents = build_code_documents(repository)

    code_chunks = chunk_code_documents(documents)

    items = []

    for chunk in code_chunks:
        project = chunk.project or "Unknown"
        symbol = chunk.symbol or "Unknown"
        code_kind = chunk.kind or "Unknown"

        content = (
            f"Path: {chunk.source}\n"
            f"Language: {chunk.language}\n"
            f"Project: {project}\n"
            f"Symbol: {symbol}\n"
            f"Kind: {code_kind}\n\n"
            f"{chunk.content}"
        )

        items.append(
            ContextItem(
                kind="code",
                source=chunk.source,
                content=content,
                priority=CODE_CONTEXT_PRIORITY,
                scope=chunk.project
                or str(Path(chunk.source.split("#chunk-", 1)[0]).parent),
            )
        )

    return items


def context_file_priority(
    filename: str,
) -> int:
    filename = filename.upper()

    if filename == "AGENTS.MD":
        return 130

    if filename == "CLAUDE.MD":
        return 130

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
