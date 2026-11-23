# SPDX-FileCopyrightText: 2025 QuantCo Inc
# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: 0BSD
# SPDX-License-Identifier: MIT

import json
import subprocess

import pytest


def test_generation(generated_project, project_slug):
    assert (
        generated_project / "src" / project_slug.replace("-", "_") / "__init__.py"
    ).exists()
    surface_test = (generated_project / "tests" / "test_public_surface.py").read_text()
    assert f"import {project_slug.replace('-', '_')}\n" in surface_test
    readme = (generated_project / "README.md").read_text()
    assert (
        f"https://img.shields.io/github/actions/workflow/status/energy-models/{project_slug}/ci.yml"
        in readme
    )
    assert "<!-- ALL-CONTRIBUTORS-LIST:START" in readme
    assert "<!-- ALL-CONTRIBUTORS-LIST:END -->" in readme
    contributors = json.loads((generated_project / ".all-contributorsrc").read_text())
    assert contributors["contributors"][0]["name"] == "Lando Calrissian"

    pyproject = (generated_project / "pyproject.toml").read_text()
    assert (
        'authors = [{ name = "Lando Calrissian", email = "lando@calrissian.org" }]'
        in pyproject
    )


def test_generation_incorrect_params(generate_project):
    with pytest.raises(subprocess.CalledProcessError):
        generate_project({"project_slug": "test_project"})

    with pytest.raises(subprocess.CalledProcessError):
        generate_project({"repository_owner": "Lando Calrissian"})

    with pytest.raises(subprocess.CalledProcessError):
        generate_project({"author_email": "foo"})


@pytest.mark.parametrize("use_devcontainer", [True, False])
def test_devcontainer(generate_project, use_devcontainer):
    path = generate_project({"use_devcontainer": use_devcontainer})
    paths = [
        path / ".devcontainer",
        path / ".devcontainer" / "Dockerfile",
        path / ".devcontainer" / "devcontainer.json",
    ]
    for path in paths:
        assert path.exists() == use_devcontainer


@pytest.mark.parametrize("add_autobump_workflow", [True, False])
def test_add_autobump_workflow(generate_project, add_autobump_workflow):
    path = generate_project({"add_autobump_workflow": add_autobump_workflow})
    assert (
        path / ".github" / "workflows" / "update-lockfiles.yml"
    ).exists() == add_autobump_workflow


def test_agents_md(generated_project):
    assert (generated_project / "AGENTS.md").exists()
    claude_md = generated_project / ".claude" / "CLAUDE.md"
    assert claude_md.is_symlink()
    assert claude_md.resolve() == (generated_project / "AGENTS.md").resolve()


@pytest.mark.parametrize("minimal_python_version", ["py312", "py313", "py314"])
def test_minimal_python_version(generate_project, minimal_python_version: str):
    minimal_python_version_str = minimal_python_version.replace("py3", "3.")
    all_supported_python_versions = ["3.12", "3.13", "3.14"]
    all_supported_python_envs = [
        f"py{version.replace('.', '')}" for version in all_supported_python_versions
    ]
    supported_python_versions = all_supported_python_versions[
        all_supported_python_versions.index(minimal_python_version_str) :
    ]
    unsupported_python_versions = all_supported_python_versions[
        : all_supported_python_versions.index(minimal_python_version_str)
    ]

    path = generate_project({"minimal_python_version": minimal_python_version})
    with open(path / "pyproject.toml") as f:
        pyproject_toml_content = f.read()
    assert (
        f']\nrequires-python = ">={minimal_python_version_str}"\nreadme = "README.md'
        in pyproject_toml_content
    )
    assert (
        f'[tool.pyrefly]\npython-version = "{minimal_python_version_str}"\n'
        in pyproject_toml_content
    )

    for version in supported_python_versions:
        assert f"Programming Language :: Python :: {version}" in pyproject_toml_content
    for version in unsupported_python_versions:
        assert (
            f"Programming Language :: Python :: {version}" not in pyproject_toml_content
        )

    with open(path / "pixi.toml") as f:
        pixi_toml = f.read()
    with open(path / ".github" / "workflows" / "ci.yml") as f:
        ci = f.read()

    for version in all_supported_python_versions:
        if version == minimal_python_version_str:
            assert f'python = ">={minimal_python_version_str}"' in pixi_toml
        else:
            assert f">={version}" not in pixi_toml

    for version, env in zip(all_supported_python_versions, all_supported_python_envs):
        if version in supported_python_versions:
            assert env in pixi_toml
            assert env in ci
        else:
            assert env not in pixi_toml
            assert env not in ci


@pytest.mark.parametrize("skill", ["prose-writing", "docs-writing"])
def test_recopy_keeps_project_rules_and_replaces_shared_skill(generate_project, skill):
    path = generate_project()
    skill_dir = path / ".claude" / "skills" / skill
    shared = (skill_dir / "SKILL.md").read_text()
    (skill_dir / "project.md").write_text("project rules\n")
    (skill_dir / "SKILL.md").write_text("local edit\n")

    subprocess.check_call(
        [
            "copier",
            "recopy",
            "--overwrite",
            "--defaults",
            "--trust",
            "--skip-tasks",
            "--vcs-ref=HEAD",
            path,
        ]
    )

    assert (skill_dir / "project.md").read_text() == "project rules\n"
    assert (skill_dir / "SKILL.md").read_text() == shared


@pytest.mark.parametrize("stub", ["CHANGELOG.md", "docs/index.md", "tests/conftest.py"])
def test_recopy_keeps_project_stubs(generate_project, stub):
    path = generate_project()
    (path / stub).write_text("project text\n")

    subprocess.check_call(
        [
            "copier",
            "recopy",
            "--overwrite",
            "--defaults",
            "--trust",
            "--skip-tasks",
            "--vcs-ref=HEAD",
            path,
        ]
    )

    assert (path / stub).read_text() == "project text\n"
