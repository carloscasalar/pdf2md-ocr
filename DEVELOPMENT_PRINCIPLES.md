# Development Principles for pdf2md-ocr

This document captures key decisions and principles for developing this project. All contributions should follow these guidelines.

## Core Philosophy

**KISS (Keep It Simple, Stupid)**
- One library call shouldn't need a framework
- CLI args don't need custom interfaces
- Focus on the `uvx` use case - simple and immediate
- Minimal implementation that does the job without over-engineering

## Code Style & Quality

### Python & CLI Design
- Use `click` for CLI argument parsing (lightweight, proven)
- Use `rich` for formatted output (already a dependency)
- Single responsibility: wrap marker-pdf library efficiently
- Prefer functional, procedural code over unnecessary abstractions
- No complex bash scripts with custom argument parsing

### Testing
- **Every feature change must have corresponding tests**
- Tests are implementation details, not features to document in CHANGELOG
- Test organization:
  - Unit tests for pure functions (validation, conversion logic)
  - Integration tests for CLI behavior
  - Functional tests for end-to-end PDF conversion
- All tests must pass before code is considered complete

### Page Numbering Convention
- **User-facing page numbers start at 1** (human-friendly, standard PDF convention)
- Internal conversion to 0-based indexing is implementation detail
- Error messages must always refer to 1-based numbering
- CLI help text must explicitly state "page numbering starts at 1"

## Feature Design

### CLI Options
- Prefer separate options over combined flags when they allow partial specification
  - Good: `--start-page N` and `--end-page M` (either, both, or neither)
  - Less good: `--page-range 2-5` (requires both or special syntax)
- Options should be flexible: allow omitting start or end
- Validation should be comprehensive with user-friendly error messages

### Error Handling
- Validate inputs early with clear error messages
- Error messages should:
  - Explicitly mention page numbering convention when relevant
  - Show the invalid values for debugging
  - Suggest valid alternatives where appropriate

## Documentation

### README
- Include examples showing all usage patterns
- Explicitly document non-obvious behavior (e.g., "page numbering starts at 1")
- Keep it minimal but complete

### CHANGELOG
- Document new features and breaking changes
- Do NOT list tests or internal improvements (they're prerequisites, not features)
- Use semantic versioning
- Include date and version tags

### Version Management
- Semantic versioning: MAJOR.MINOR.PATCH
- Update version in:
  - `pyproject.toml` ([project].version)
  - `src/pdf2md_ocr/__init__.py` (__version__)
  - CLI help text (@click.version_option)

## Dependency Management

- Use `uv` for all dependency management
- Pin marker-pdf version (stability)
- Don't over-specify transitive dependencies
- Maintain `uv.lock` for reproducible installs
- Keep dependencies minimal

## Git & Version Control

### Commit Messages
- Use semantic commits: `feat:`, `fix:`, `docs:`, `test:`, etc.
- Descriptive but concise
- Include context about implementation decisions

### Branch Management
- Create feature branches with descriptive names (e.g., `feature/page-range`)
- Include tests and documentation in the same branch
- Ensure all tests pass before pushing

## Publishing & Release

- Use PyPI Trusted Publisher workflow (proven configuration)
- Tag releases with format `v0.0.X` corresponding to version in pyproject.toml
- Builds and publishes automatically on tag push
- One public release at a time (no pre-releases without reason)

## Principles in Action

When adding a new feature:

1. ✅ Implement the feature with minimal code
2. ✅ Add comprehensive tests covering normal and error cases
3. ✅ Update CLI help text with examples (page numbering convention if applicable)
4. ✅ Update README with usage examples
5. ✅ Update CHANGELOG with feature description (no test mentions)
6. ✅ Bump version numbers in all three places
7. ✅ Commit with semantic message
8. ✅ Run full test suite before push
9. ✅ Push feature branch and create merge request

## When in Doubt

- Refer to existing code style in the project
- Check how similar features in marker-pdf handle page ranges
- Keep it simple: if you need to explain it extensively, simplify the design
- Remember: users want to do one thing simply with `uvx pdf2md-ocr input.pdf -o output.md`
