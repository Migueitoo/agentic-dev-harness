from pathlib import Path

from repository.models import RepositoryInfo
from repository.scanner import (
    IGNORED_DIRECTORIES,
    LANGUAGE_EXTENSIONS,
)

from .models import CodeDocument


def build_code_documents(
    repository: RepositoryInfo,
) -> list[CodeDocument]:
    documents = []

    for file_path in repository.path.rglob("*"):
        if not file_path.is_file():
            continue

        if is_ignored(file_path, repository.path):
            continue

        language = get_source_language(file_path)

        if language is None:
            continue

        content = read_code_file(file_path)

        if content is None:
            continue

        documents.append(
            CodeDocument(
                source=relative_source(
                    file_path,
                    repository.path,
                ),
                content=content,
                language=language,
                project=find_project_name(
                    file_path,
                    repository.path,
                ),
            )
        )

    return documents


def get_source_language(
    file_path: Path,
) -> str | None:
    return LANGUAGE_EXTENSIONS.get(file_path.suffix.lower())


def is_ignored(
    file_path: Path,
    repository_path: Path,
) -> bool:
    relative_parts = file_path.relative_to(repository_path).parts

    return any(part in IGNORED_DIRECTORIES for part in relative_parts)


def read_code_file(
    file_path: Path,
) -> str | None:
    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError:
        return None


def relative_source(
    file_path: Path,
    repository_path: Path,
) -> str:
    return file_path.relative_to(repository_path).as_posix()


def find_project_name(
    file_path: Path,
    repository_path: Path,
) -> str | None:
    current_path = file_path.parent

    while current_path != repository_path.parent:
        project_files = sorted(current_path.glob("*.csproj"))

        if project_files:
            return project_files[0].stem

        if current_path == repository_path:
            break

        current_path = current_path.parent

    return None
