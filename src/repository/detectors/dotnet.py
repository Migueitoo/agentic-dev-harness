from pathlib import Path
import xml.etree.ElementTree as ET

from ..models import DotNetProjectInfo, PackageReferenceInfo


def _elements(root: ET.Element, name: str) -> list[ET.Element]:
    return [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] == name]


def _first_text(root: ET.Element, *names: str) -> str | None:
    for name in names:
        for element in _elements(root, name):
            if element.text and element.text.strip():
                return element.text.strip()
    return None


def inspect_dotnet_project(file_path: Path) -> DotNetProjectInfo:
    tree = ET.parse(file_path)
    root = tree.getroot()

    sdk = root.attrib.get("Sdk")

    target_framework = _first_text(root, "TargetFramework", "TargetFrameworks", "TargetFrameworkVersion")
    is_test_project = (_first_text(root, "IsTestProject") or "").lower() == "true"

    package_references = []

    for package_reference in _elements(root, "PackageReference"):
        package_name = package_reference.attrib.get("Include")
        package_version = package_reference.attrib.get("Version")
        if package_version is None:
            package_version = _first_text(package_reference, "Version")

        if package_name:
            package_references.append(
                PackageReferenceInfo(
                    name=package_name,
                    version=package_version,
                )
            )

    test_framework = None

    package_names = {package.name.lower() for package in package_references}

    if is_test_project or package_names.intersection({"microsoft.net.test.sdk", "xunit", "nunit", "mstest.testframework"}):
        project_type = "test"
        is_test_project = True
    elif sdk == "Microsoft.NET.Sdk.Web":
        project_type = "web"
    elif sdk == "Microsoft.NET.Sdk.Worker":
        project_type = "worker"
    elif "worker" in file_path.stem.casefold():
        project_type = "worker candidate (project name)"
    else:
        project_type = "not determined"

    if "xunit" in package_names:
        test_framework = "xUnit"
    elif "nunit" in package_names:
        test_framework = "NUnit"
    elif "mstest.testframework" in package_names:
        test_framework = "MSTest"

    project_references = []

    for project_reference in _elements(root, "ProjectReference"):
        include = project_reference.attrib.get("Include")

        if include:
            project_references.append(include)

    return DotNetProjectInfo(
        name=file_path.name,
        sdk=sdk,
        target_framework=target_framework,
        is_test_project=is_test_project,
        project_type=project_type,
        test_framework=test_framework,
        project_references=project_references,
        package_references=package_references,
    )
