# SPDX-FileCopyrightText: 2026 copier-template-python-open-source contributors
#
# SPDX-License-Identifier: MIT

"""Rewrite the ``license`` answer to the SPDX identifier the template now asks for.

Runs in the project being updated, before copier applies the template diff.
Standard library only, because copier runs it on its own Python.
"""

import re
from pathlib import Path

PATH = Path(".copier-answers.yml")
SPDX = {"BSD": "BSD-3-Clause", "GPL-v3": "GPL-3.0-or-later"}
ANSWER = re.compile(r"^license: (?P<value>\S+)$", re.MULTILINE)


def migrate(text: str) -> str:
    """The answers with an old ``license`` value replaced by its SPDX identifier."""
    return ANSWER.sub(
        lambda match: f"license: {SPDX.get(match['value'], match['value'])}", text
    )


def main() -> None:
    PATH.write_text(migrate(PATH.read_text()))


if __name__ == "__main__":
    main()
