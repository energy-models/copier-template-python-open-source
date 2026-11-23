# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import copy_template


@pytest.fixture(scope="module")
def project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = copy_template(
        tmp_path_factory.mktemp("project"), {"project_slug": "my-project"}
    )
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def test_the_generated_changelog_tests_pass(project):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "tests/test_changelog.py",
        ],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_generated_changelog_releases_nothing(project):
    result = subprocess.run(
        [sys.executable, "-m", "tools.changelog", "check"],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "releases nothing on merge"


def test_the_release_checks_the_normalised_wheel_name(project):
    release = (project / ".github" / "workflows" / "release.yml").read_text()
    assert 'test -f "dist/my_project-${VERSION}-py3-none-any.whl"' in release
    assert 'test -f "dist/my_project-${VERSION}.tar.gz"' in release
