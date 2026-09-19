from pathlib import Path
import subprocess

from .models import RepositoryInfo
from .detectors.dotnet import (
    inspect_dotnet_project,
    detect_dotnet_capabilities,
)

LANGUAGE_EXTENSIONS = {
    ".cs": "C#",
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".php": "PHP",
    ".rb": "Ruby",
}


IGNORED_DIRECTORIES = {
    ".git",
    "bin",
    "obj",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
}


CONTEXT_FILE_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
}


def scan_repository(repo_path: Path) -> RepositoryInfo:
    repo_path = repo_path.resolve()

    context_files = detect_context_files(repo_path)
    current_branch = detect_git_branch(repo_path)
    languages = detect_languages(repo_path)
    projects = detect_dotnet_projects(repo_path)

    frameworks = detect_frameworks(projects)
    capabilities = detect_dotnet_capabilities(projects)

    return RepositoryInfo(
        name=repo_path.name,
        path=repo_path,
        languages=languages,
        frameworks=frameworks,
        capabilities=capabilities,
        context_files=context_files,
        current_branch=current_branch,
        projects=projects,
    )


def detect_context_files(repo_path: Path) -> list[str]:
    context_files = []

    for filename in CONTEXT_FILE_NAMES:
        file_path = repo_path / filename

        if file_path.exists():
            context_files.append(filename)

    return sorted(context_files)


def detect_git_branch(repo_path: Path) -> str | None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_path),
                "branch",
                "--show-current",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        branch = result.stdout.strip()

        return branch or None

    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        return None


def detect_languages(repo_path: Path) -> list[str]:
    language_counts = {}

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        if is_ignored(file_path):
            continue

        language = LANGUAGE_EXTENSIONS.get(file_path.suffix.lower())

        if language:
            language_counts[language] = language_counts.get(language, 0) + 1

    return sorted(
        language_counts,
        key=language_counts.get,
        reverse=True,
    )


def detect_dotnet_projects(repo_path: Path):
    projects = []

    for file_path in repo_path.rglob("*.csproj"):
        if is_ignored(file_path):
            continue

        projects.append(inspect_dotnet_project(file_path))

    return projects


def detect_frameworks(projects) -> list[str]:
    frameworks = set()

    for project in projects:
        if project.sdk == "Microsoft.NET.Sdk.Web":
            frameworks.add("ASP.NET Core")

    return sorted(frameworks)


def is_ignored(file_path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in file_path.parts)
