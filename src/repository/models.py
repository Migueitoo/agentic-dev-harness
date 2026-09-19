from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageReferenceInfo:
    name: str
    version: str | None


@dataclass
class DotNetProjectInfo:
    name: str
    sdk: str | None
    target_framework: str | None
    is_test_project: bool
    project_type: str
    test_framework: str | None
    project_references: list[str]
    package_references: list[PackageReferenceInfo]


@dataclass
class RepositoryInfo:
    name: str
    path: Path
    languages: list[str]
    frameworks: list[str]
    capabilities: list[str]
    context_files: list[str]
    current_branch: str | None
    projects: list[DotNetProjectInfo]
