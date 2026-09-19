from pathlib import Path
import xml.etree.ElementTree as ET

from ..models import DotNetProjectInfo, PackageReferenceInfo


def inspect_dotnet_project(file_path: Path) -> DotNetProjectInfo:
    tree = ET.parse(file_path)
    root = tree.getroot()

    sdk = root.attrib.get("Sdk")

    target_framework_element = root.find(".//TargetFramework")
    target_framework = (
        target_framework_element.text if target_framework_element is not None else None
    )

    is_test_project_element = root.find(".//IsTestProject")

    is_test_project = (
        is_test_project_element is not None
        and is_test_project_element.text is not None
        and is_test_project_element.text.lower() == "true"
    )

    if is_test_project:
        project_type = "test"
    elif sdk == "Microsoft.NET.Sdk.Web":
        project_type = "web"
    else:
        project_type = "library"

    package_references = []

    for package_reference in root.findall(".//PackageReference"):
        package_name = package_reference.attrib.get("Include")
        package_version = package_reference.attrib.get("Version")

        if package_name:
            package_references.append(
                PackageReferenceInfo(
                    name=package_name,
                    version=package_version,
                )
            )

    test_framework = None

    package_names = {package.name.lower() for package in package_references}

    if "xunit" in package_names:
        test_framework = "xUnit"
    elif "nunit" in package_names:
        test_framework = "NUnit"
    elif "mstest.testframework" in package_names:
        test_framework = "MSTest"

    project_references = []

    for project_reference in root.findall(".//ProjectReference"):
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


def detect_dotnet_capabilities(
    projects: list[DotNetProjectInfo],
) -> list[str]:
    capabilities = set()

    for project in projects:
        if project.is_test_project:
            capabilities.add("Testing")

        if project.test_framework:
            capabilities.add(project.test_framework)

        for package in project.package_references:
            package_name = package.name.lower()

            if package_name.startswith("modelcontextprotocol"):
                capabilities.add("MCP")

            if package_name.startswith("swashbuckle"):
                capabilities.add("Swagger / OpenAPI")

            if package_name.startswith("coverlet"):
                capabilities.add("Code Coverage")

    return sorted(capabilities)
