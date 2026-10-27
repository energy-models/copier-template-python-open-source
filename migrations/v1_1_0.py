# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: MIT

"""Rewrite ``CHANGELOG.md`` headings to the form ``tools/changelog.py`` reads.

Runs in the project being updated, before copier applies the template diff.
Standard library only, because copier runs it on its own Python.
"""

import re
import subprocess
import sys
from pathlib import Path

PATH = Path("CHANGELOG.md")
UPCOMING = "Upcoming version"
GUIDE = re.compile(r"<!---\s*Changelog headings can be any of:.*?-->\n*", re.DOTALL)
UNRELEASED = re.compile(r"^## \[?Unreleased\]?[ \t]*$", re.MULTILINE | re.IGNORECASE)
OLD_RELEASE = re.compile(
    r"^## \[?v?(?P<version>\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?)\]?(?:\(\S+\))?"
    r"[ \t]*-?[ \t]*\(?(?P<y>\d{4})[-.](?P<m>\d{2})[-.](?P<d>\d{2})\)?[ \t]*$",
    re.MULTILINE,
)
RELEASE = re.compile(r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)? \(\d{4}-\d{2}-\d{2}\)")


def migrate(text: str, tags: set[str]) -> str:
    """The changelog with its headings in the new form.

    Raises
    ------
    ValueError
        If a ``##`` heading has no new form, or if the first release has no
        ``v``-prefixed tag, which would make the next merge to ``main`` release
        it again.
    """
    text = GUIDE.sub("", text)
    text = UNRELEASED.sub(f"## {UPCOMING}", text)
    text = OLD_RELEASE.sub(r"## \g<version> (\g<y>-\g<m>-\g<d>)", text)

    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    unknown = [h for h in headings if h != UPCOMING and not RELEASE.fullmatch(h)]
    if unknown:
        raise ValueError(
            "CHANGELOG.md has headings with no new form. Rewrite each as "
            '"## Upcoming version" or "## X.Y.Z (YYYY-MM-DD)", then update again: '
            + ", ".join(f'"## {h}"' for h in unknown)
        )

    releases = [h.split(" ")[0] for h in headings if RELEASE.fullmatch(h)]
    if releases and f"v{releases[0]}" not in tags:
        raise ValueError(
            f"{releases[0]} is the latest release in CHANGELOG.md but has no tag "
            f'"v{releases[0]}", so the next merge to main would release it again. '
            f"Tag the commit it was released from, then update again: "
            f"git tag v{releases[0]} <commit> && git push origin v{releases[0]}"
        )
    return text


def main() -> None:
    if not PATH.exists():
        return
    tags = subprocess.run(
        ["git", "tag", "--list"], capture_output=True, text=True, check=True
    ).stdout.split()
    try:
        PATH.write_text(migrate(PATH.read_text(), set(tags)))
    except ValueError as error:
        sys.exit(f"Migration v1.1.0 stopped: {error}")


if __name__ == "__main__":
    main()
