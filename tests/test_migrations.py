# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: MIT

import re

import pytest

from migrations.v1_1_0 import migrate

GUIDE = """<!---
Changelog headings can be any of:

Added: for new features.

Release headings should be of the form:
## [X.Y.Z] - YEAR-MONTH-DAY
-->

"""
OLD = """# Changelog

## Unreleased

### Added

- a line

## [0.2.0] - 2026-09-01

- b

## v0.1.0 (2026.08.17)

- a
"""
NEW = """# Changelog

## Upcoming version

### Added

- a line

## 0.2.0 (2026-09-01)

- b

## 0.1.0 (2026-08-17)

- a
"""


def test_the_old_template_changelog_reads_as_the_new_one():
    assert migrate(GUIDE + OLD, {"v0.1.0", "v0.2.0"}) == NEW


@pytest.mark.parametrize(
    ("heading", "expected"),
    [
        ("## [Unreleased]", "## Upcoming version"),
        ("## [0.1.0rc1] - 2026-10-01", "## 0.1.0rc1 (2026-10-01)"),
        (
            "## [v0.1.0](https://example.org/compare) - 2026-10-01",
            "## 0.1.0 (2026-10-01)",
        ),
        ("## 0.1.0 (2026-10-01)", "## 0.1.0 (2026-10-01)"),
    ],
)
def test_a_heading_takes_the_new_form(heading, expected):
    assert migrate(f"# Changelog\n\n{heading}\n\n- a\n", {"v0.1.0", "v0.1.0rc1"}) == (
        f"# Changelog\n\n{expected}\n\n- a\n"
    )


@pytest.mark.parametrize(
    ("text", "tags", "message"),
    [
        pytest.param(
            "## Next release\n", set(), '"## Next release"', id="unknown-heading"
        ),
        pytest.param(
            "## [0.1] - 2026-10-01\n\n- a\n",
            set(),
            "no new form",
            id="two-part-version",
        ),
        pytest.param(OLD, {"v0.1.0"}, 'no tag "v0.2.0"', id="latest-release-untagged"),
        pytest.param(OLD, {"0.2.0", "0.1.0"}, "git tag v0.2.0", id="tags-without-v"),
    ],
)
def test_a_changelog_the_release_tool_would_refuse_stops_the_update(
    text, tags, message
):
    with pytest.raises(ValueError, match=re.escape(message)):
        migrate(text, tags)
