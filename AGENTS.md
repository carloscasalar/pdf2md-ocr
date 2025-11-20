# AGENTS Guide for `pdf2md-ocr`

This file defines how AI/code agents should behave when working in this repository. It encodes project-specific preferences plus general Python best practices.

## 1. Mission & Scope

- **Primary goal:** Maintain a _minimal_, reliable CLI wrapper around `marker-pdf` to convert PDFs to Markdown, optimized for `uvx` usage.
- **Things to avoid:** Building frameworks, custom orchestration layers, or complex infrastructure around the core conversion.
- **Scope:**
  - Source code under `src/pdf2md_ocr/`
  - Tests under `tests/`
  - Project metadata (`pyproject.toml`, `README.md`, `CHANGELOG.md`)
  - Dev tooling and docs relevant to this package

## 2. Core Principles

1. **KISS (Keep It Simple, Stupid)**

   - Prefer straightforward procedural Python over extra layers of abstraction.
   - One CLI command around `marker-pdf` is the main product, not a framework.

2. **CLI-First UX**

   - Optimized for `uvx pdf2md-ocr input.pdf -o output.md`.
   - No mandatory global configuration files or complex setup.

3. **Tests Are Mandatory, Not Features**

   - Every behavioral change **must** be covered by tests.
   - Tests are not listed as features in the `CHANGELOG.md`.

4. **Minimal Surface Area**

   - Keep public APIs small and predictable.
   - Avoid adding options unless they have clear user value.

5. **Respect Existing Style & Decisions**

- Follow the conventions set in `cli.py` and `tests/test_conversion.py`.

## 3. Python & CLI Conventions

- **Language:** Python 3.10+ only.
- **CLI:**
  - Use `click` for all argument parsing.
  - Use clear, explicit option names (e.g., `--start-page`, `--end-page`).
  - Document examples in `--help` and `README.md`.
- **Page Numbering:**
  - User-facing pages are **1-based** and inclusive.
  - Internal conversions to 0-based are implementation details.
  - Error messages and docs must explicitly state "page numbering starts at 1" when relevant.

## 4. Testing Rules

- **Coverage expectations:**
  - Unit tests for pure functions (e.g., validation, conversions) in `tests/test_conversion.py` or new test modules if they grow.
  - CLI integration tests using `click.testing.CliRunner`.
  - Functional tests using sample PDFs under `pdf-samples/`.
- **When adding/changing behavior:**
  - Add or update tests in the same branch.
  - Ensure `uv run pytest` (or equivalent) passes before asking for merge.

## 5. Documentation & Changelog

- **README (`README.md`):**
  - Show typical and advanced usage examples.
  - Clearly explain any non-obvious behavior (e.g., page range semantics).
- **CHANGELOG (`CHANGELOG.md`):**
  - Follow Keep a Changelog + Semantic Versioning.
  - Record _features, changes, deprecations, fixes_.
  - Do **not** mention tests as separate bullet points—tests are expected.

## 6. Dependencies & Tooling

- **Dependency manager:** `uv`.
- **Core deps:**
  - `marker-pdf` (pinned, e.g., `==1.10.1`)
  - `click`
  - `rich`
- **Guidelines:**
  - Avoid introducing new dependencies unless they add clear user value.
  - Never pin every transitive dependency; keep `pyproject.toml` clean.
  - Keep `uv.lock` updated when dependency graph changes.
  - Use 2-space indentation for YAML files (CI workflows, configs), enforced via `.editorconfig`.

## 7. Versioning & Releases

- Use **Semantic Versioning** (`MAJOR.MINOR.PATCH`).
- When changing behavior:
  - Update version in `pyproject.toml`, `src/pdf2md_ocr/__init__.py`, and the CLI version option.
  - Add an entry to `CHANGELOG.md` with date and version.
- Publishing is handled via the existing PyPI Trusted Publisher workflow; do not reinvent.

## 8. Git & Branching

- **Branches:**
  - Use descriptive names: `feature/...`, `fix/...`, `docs/...`.
- **Commits:**
  - Use semantic prefixes: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, etc.
  - Include tests and docs updates in the same feature commit/PR when relevant.

## 9. Agent Behavior Checklist

When an agent makes changes, it should:

1. Understand the current behavior by reading relevant files.
2. Design the change to be minimal and consistent with existing patterns.
3. Implement the feature/change in `src/`.
4. Add/adjust tests in `tests/` to fully cover the new behavior.
5. Run tests via `uv run pytest` (or a narrower subset when iterating).
6. Update `README.md` and `CHANGELOG.md` for user-visible changes.
7. Update version numbers when releasing a new version.
8. Keep commits focused and messages semantic.

## 10. What Agents Should Avoid

- Adding complex frameworks, plugin systems, or multi-layer abstractions.
- Introducing global mutable configuration without strong justification.
- Duplicating functionality that `marker-pdf` already provides.
- Over-documenting internals that are obvious from the code.
- Creating unnecessary markdowns. Only create the documents that the human specifically asked for.

---

Agents should treat this file as the source of truth for how to behave in this repository. If a conflict arises, **simplicity and user experience** (especially via `uvx`) take precedence.
