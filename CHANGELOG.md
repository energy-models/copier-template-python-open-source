<!--
SPDX-FileCopyrightText: copier-template-python-open-source contributors
SPDX-License-Identifier: CC-BY-4.0
-->
<!---
Changelog headings can be any of:

Added: for new features.
Changed: for changes in existing functionality.
Deprecated: for soon-to-be removed features.
Removed: for now removed features.
Fixed: for any bug fixes.
Security: in case of vulnerabilities.

Release headings should be of the form:
## [X.Y.Z] - YEAR-MONTH-DAY
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

In this release, we have aligned to current practice in https://github.com/energy-models/datarecord.

### Added

- Reference index page.
- Extra mkdocs features.
- mkdocs theme palette, language, & icon.
- extra socials buttons for GH & pypi.
- Mkdocs v2 warning suppressor in pixi.toml.
- Release on merge, ported from https://github.com/energy-models/mathspec:
  a PR that puts a version heading on top of `CHANGELOG.md` tags, releases and publishes that version (`release.yml`, `tools/changelog.py`, `RELEASING.md`).
- `Changelog line` and `Conventional commit subject` PR checks.
- A `ci` pixi task that runs every gate CI runs: `lint`, `test` and `docs-build`, ported from https://github.com/energy-models/mathspec.
- `workflow_dispatch` on the CI workflow.
- A pull request template.
- Tests in generated projects for `tools/changelog.py`, the package's `__all__` and the docs navigation.
- `pytest-xdist`; `pixi run test` runs `pytest -n auto`.
- PEP 639 license metadata, project URLs and a `Development Status` classifier in `pyproject.toml`.
- AGENTS.md rules on merging, AI-written PR bodies, gates, worktrees, tests and PR descriptions.
- An all-contributors section in `README.md`, prefilled with the project author, for the all-contributors bot to update.
- A "The home page" section in the docs-writing skill, from https://github.com/energy-models/datarecord and https://github.com/energy-models/math-spec, that sets the order of the docs home page and the rules for its graphical abstract.
  The skill's `project.md` has a slot for the project's own home page and abstract.
- `copier update` no longer touches `CHANGELOG.md`, `docs/index.md` or `tests/conftest.py` once they exist, because a project fills in these stubs.

### Changed

- Accelerate REUSE check in pre-commit.
- template tests to include only a conftest.py file and an import smoke test, so that a new project's test suite passes.
- AGENTS.md, to include more verbose instructions.
- **Breaking**: the package version comes from the git tag through hatch-vcs, not from a `sed` over `pyproject.toml`.
- **Breaking**: `CHANGELOG.md` uses one `## Upcoming version` heading above `## X.Y.Z (YYYY-MM-DD)` release headings.
  CI refuses any other heading.
- `build.yml` no longer publishes on a tag push; `release.yml` calls it.
- CI is one `CI` job that runs every gate on pull requests; the OS by Python version pytest matrix runs only on a push to `main` or by hand.
- setup-pixi installs from `pixi.lock` with `locked: true`.
- **Breaking**: the docs build with zensical (`python -m zensical build --strict`) instead of mkdocs and mkdocs-material.
  `docs/static/hooks.py` is removed: the Python API page is `docs/reference/api.md` and the changelog page is `docs/reference/changelog.md`.
- **Breaking**: pyrefly replaces mypy as the type checker, in `strict` mode.
- The ruff rule set is wider, and ruff and pyrefly are pinned to exact versions.
- **Breaking**: docstrings use the Google style instead of numpydoc, and ruff's `D` rules check them under the package directory.
- `pixi-build-python` is exempt from `exclude-newer`.
- **Breaking**: the `license` answers `BSD` and `GPL-v3` are now the SPDX identifiers `BSD-3-Clause` and `GPL-3.0-or-later`; a migration rewrites the answer.

### Fixed

- Read the Docs installs the `default` environment; the `doc` environment it asked for does not exist.
- The lockfile update PR title passes the `Conventional commit subject` check.
- The README snippet section that the docs home page includes is named `docs-preamble`, as `docs/index.md` asks for.
- `.all-contributorsrc` is valid JSON: the first contributor's `login` and `name` are quoted.

## v1.0.0 (2026.08.17)

This is the first release since forking from https://github.com/quantco/copier-template-python-open-source.

### Added

- docs with mkdocs.
- changelog.
- issue templates.
- REUSE license headers.
- all-contributors config.
