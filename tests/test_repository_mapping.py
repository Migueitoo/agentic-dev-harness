"""Behavior that protects generated maps and human-written agent instructions."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repository.mapping import inspect_repository, map_repository, render_repository_map


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class RepositoryMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="repository-mapping-test-")
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "-q")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "App.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup>'
            '<TargetFrameworks>net8.0;net9.0</TargetFrameworks></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../Core/Core.csproj"/>'
            '<PackageReference Include="Swashbuckle.AspNetCore" Version="6.0"/>'
            '</ItemGroup></Project>', encoding="utf-8"
        )
        (self.repo / "src" / "Program.cs").write_text("class Program {}", encoding="utf-8")
        (self.repo / "src" / "Controllers").mkdir()
        (self.repo / "src" / "Controllers" / "ReportController.cs").write_text(
            "class ReportController {}", encoding="utf-8"
        )
        (self.repo / "package.json").write_text(
            '{"name":"sample", "dependencies":{"express":"*"}, "devDependencies":{"vitest":"*"}}',
            encoding="utf-8",
        )
        (self.repo / "pyproject.toml").write_text(
            '[project]\nname = "sample"\ndependencies = ["httpx>=0.27", "rich[all]>=13"]\n',
            encoding="utf-8",
        )
        (self.repo / "go.mod").write_text(
            'module example.com/sample\nrequire example.com/dependency v1.2.3\n', encoding="utf-8"
        )
        (self.repo / "pom.xml").write_text(
            '<project><groupId>example</groupId><artifactId>app</artifactId>'
            '<dependencies><dependency><groupId>org.sample</groupId>'
            '<artifactId>sample-lib</artifactId></dependency></dependencies></project>',
            encoding="utf-8",
        )
        (self.repo / "AGENTS.md").write_text("# Human instructions\n\nKeep this section.\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_preview_and_write_preserve_instructions_and_are_idempotent(self) -> None:
        preview = render_repository_map(inspect_repository(str(self.repo)))
        self.assertIn("net8.0;net9.0", preview)
        self.assertIn("../Core/Core.csproj", preview)
        self.assertIn("Swashbuckle.AspNetCore", preview)
        self.assertIn("express", preview)
        self.assertIn("httpx", preview)
        self.assertIn("example.com/dependency", preview)
        self.assertIn("org.sample:sample-lib", preview)
        self.assertIn("src/Program.cs", preview)
        self.assertIn("src/Controllers/ReportController.cs", preview)
        self.assertFalse((self.repo / "REPOSITORY_MAP.md").exists())

        first = map_repository(str(self.repo))
        self.assertEqual(set(first["changed_files"]), {"REPOSITORY_MAP.md", "AGENTS.md", "CLAUDE.md"})
        self.assertIn("Keep this section.", (self.repo / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual((self.repo / "AGENTS.md").read_text(encoding="utf-8").count("REPOSITORY_MAP.md"), 2)
        self.assertIn("REPOSITORY_MAP.md", (self.repo / "CLAUDE.md").read_text(encoding="utf-8"))
        second = map_repository(str(self.repo))
        self.assertEqual(second["changed_files"], [])

    def test_manual_map_is_never_overwritten(self) -> None:
        manual = self.repo / "REPOSITORY_MAP.md"
        manual.write_text("Human map\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            map_repository(str(self.repo))
        self.assertEqual(manual.read_text(encoding="utf-8"), "Human map\n")
        self.assertFalse((self.repo / "CLAUDE.md").exists())

    def test_sensitive_file_contents_are_not_copied(self) -> None:
        (self.repo / ".env").write_text("PASSWORD=top-secret-value", encoding="utf-8")
        (self.repo / "appsettings.json").write_text(
            '{"ConnectionString":"top-secret-value"}', encoding="utf-8"
        )
        rendered = render_repository_map(inspect_repository(str(self.repo)))
        self.assertNotIn("top-secret-value", rendered)
        self.assertNotIn(".env", rendered)


if __name__ == "__main__":
    unittest.main()
