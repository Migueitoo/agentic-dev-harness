from dataclasses import dataclass


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
