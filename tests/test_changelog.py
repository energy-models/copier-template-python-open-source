# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: MIT

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from .conftest import copy_template

PREAMBLE = "# Changelog\n\nProse the tool never reads.\n\n"
HISTORY = "## 0.0.9 (2026-09-25)\n\n- an old line\n"
TAGS = {"v0.0.8", "v0.0.9"}


def changelog(*blocks: str) -> str:
    return PREAMBLE + "".join(blocks) + HISTORY


@pytest.fixture(scope="module")
def project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return copy_template(
        tmp_path_factory.mktemp("project"), {"project_slug": "my-project"}
    )


@pytest.fixture(scope="module")
def tool(project: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "changelog", project / "tools" / "changelog.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("text", "tags", "expected"),
    [
        pytest.param(changelog("## Upcoming version\n\n- a line\n\n"), TAGS, None, id="upcoming-only"),
        pytest.param(changelog(), TAGS, None, id="nothing-above-the-history"),
        pytest.param(PREAMBLE + "## Upcoming version\n", set(), None, id="no-release-yet"),
        pytest.param(changelog("## 0.1.0 (2026-10-01)\n\n- a line\n\n"), TAGS, "0.1.0", id="a-new-release"),
        pytest.param(
            changelog("## Upcoming version\n\n## 0.1.0 (2026-10-01)\n\n- a line\n\n"),
            TAGS,
            "0.1.0",
            id="a-new-release-under-an-empty-upcoming",
        ),
        pytest.param(changelog("## 0.1.0rc1 (2026-10-01)\n\n- a line\n\n"), TAGS, "0.1.0rc1", id="a-release-candidate"),
        pytest.param(PREAMBLE + "## 0.1.0 (2026-10-01)\n\n- a line\n", set(), "0.1.0", id="the-first-release"),
        pytest.param(
            changelog("## 0.1.0 (2026-10-01)\n\n- a line\n\n"), TAGS | {"v0.1.0"}, None, id="a-release-already-tagged"
        ),
        pytest.param(
            changelog("## 0.1.1 (2026-10-02)\n\n- b\n\n## 0.1.0 (2026-10-01)\n\n- a\n\n"),
            TAGS | {"v0.1.0"},
            "0.1.1",
            id="the-next-release-above-a-tagged-one",
        ),
    ],
)  # fmt: skip
def test_the_first_untagged_release_heading_is_the_release(tool, text, tags, expected):
    assert tool.pending(text, tags) == expected


@pytest.mark.parametrize(
    ("text", "message"),
    [
        pytest.param(changelog("## Unreleased\n\n- a line\n\n"), 'neither "## Upcoming version"', id="another-name"),
        pytest.param(changelog("## v0.1.0 (2026-10-01)\n\n- a\n\n"), "neither", id="a-v-before-the-version"),
        pytest.param(changelog("## 0.1 (2026-10-01)\n\n- a\n\n"), "neither", id="two-parts"),
        pytest.param(changelog("## 0.1.0-alpha.1 (2026-10-01)\n\n- a\n\n"), "neither", id="a-semver-pre"),
        pytest.param(changelog("## 0.1.0\n\n- a\n\n"), "neither", id="no-date"),
        pytest.param(changelog("## 0.1.0 (2026-13-01)\n\n- a\n\n"), "not a day", id="a-date-that-is-not-a-day"),
        pytest.param(changelog("## 0.1.0 (2026-10-01)\n\n"), "nothing under it", id="no-notes"),
        pytest.param(
            changelog("## 0.0.7 (2026-10-01)\n\n- a\n\n"),
            "not newer than the latest tag, v0.0.9",
            id="older-than-the-latest-tag",
        ),
        pytest.param(changelog("## Upcoming version\n\n## Upcoming version\n\n"), 'two "## Upcoming version"', id="two"),
    ],
)  # fmt: skip
def test_a_heading_the_workflow_cannot_release_is_refused(tool, text, message):
    with pytest.raises(tool.ChangelogError, match=re.escape(message)):
        tool.pending(text, TAGS)


@pytest.mark.parametrize(
    ("smaller", "larger"),
    [
        pytest.param("v0.1.0a1", "v0.1.0b1", id="alpha-before-beta"),
        pytest.param("v0.1.0a9", "v0.1.0a10", id="a-pre-release-counter-as-a-number"),
        pytest.param("v0.1.0rc2", "v0.1.0", id="a-candidate-before-the-release"),
        pytest.param("v0.9.0", "v0.10.0", id="a-part-as-a-number"),
    ],
)
def test_tags_order_as_versions(tool, smaller, larger):
    assert tool.order(smaller) < tool.order(larger)


def test_a_tag_that_is_not_a_version_is_ignored(tool):
    assert tool.order("docs-snapshot") is None, (
        "a stray tag neither blocks nor pins a release"
    )


def test_the_notes_are_the_section_as_written(tool):
    text = changelog("## 0.1.0 (2026-10-01)\n\n### Features\n\n- a line\n\n")
    assert tool.notes(text, "0.1.0") == "### Features\n\n- a line\n", (
        "the release notes are the text under the heading"
    )


def test_notes_for_a_version_with_no_heading_are_refused(tool):
    with pytest.raises(
        tool.ChangelogError, match=re.escape('no "## 0.2.0 (date)" heading')
    ):
        tool.notes(changelog(), "0.2.0")


BASE = changelog("## Upcoming version\n\n- an earlier line\n\n")
ADDED = changelog("## Upcoming version\n\n- an earlier line\n- this PR\n\n")


@pytest.mark.parametrize(
    ("title", "text", "owes"),
    [
        pytest.param("feat(io): a new thing", ADDED, False, id="a-feat-that-adds-its-line"),
        pytest.param("feat(io): a new thing", BASE, True, id="a-feat-that-adds-none"),
        pytest.param("fix: a bug", BASE, True, id="a-fix-that-adds-none"),
        pytest.param("docs: a page", BASE, True, id="a-docs-pr-that-adds-none"),
        pytest.param("revert: a change", BASE, True, id="a-revert-that-adds-none"),
        pytest.param("chore: a tidy", BASE, False, id="a-chore-owes-none"),
        pytest.param("ci: a workflow", BASE, False, id="a-ci-pr-owes-none"),
        pytest.param("test: a case", BASE, False, id="a-test-pr-owes-none"),
        pytest.param(
            "feat: a new thing",
            changelog("## Upcoming version\n\n- an earlier line, reworded\n\n"),
            False,
            id="a-reworded-line-counts",
        ),
        pytest.param(
            "feat: a new thing",
            changelog("## 0.1.0 (2026-10-01)\n\n- an earlier line\n- this PR\n\n"),
            True,
            id="a-line-outside-upcoming-does-not-count",
        ),
    ],
)  # fmt: skip
def test_a_pr_a_changelog_reader_wants_to_hear_about_adds_a_line(
    tool, title, text, owes
):
    assert (tool.missing_entry(title, text, BASE) is not None) == owes


def test_a_pr_that_owes_a_line_is_told_the_way_out(tool):
    reason = tool.missing_entry("feat: a new thing", BASE, BASE)
    assert reason is not None
    assert 'under "## Upcoming version"' in reason, (
        "the message says where the line goes"
    )
    assert 'the label "no changelog"' in reason, "and how a PR that owes none says so"


def test_the_generated_changelog_releases_nothing(project):
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
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
