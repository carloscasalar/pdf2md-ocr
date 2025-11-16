# PDF2MD-OCR: Simple CLI Tool Implementation Guide

## Goal

Create a **minimal** Python CLI tool that wraps marker-pdf library to convert PDFs to Markdown, installable via `uvx`.

## Related Documentation

- **[PYPI_CONFIG.md](./PYPI_CONFIG.md)** - Working PyPI Trusted Publisher configuration
- **[REFERENCE.md](./REFERENCE.md)** - Minimal code examples and technical details

## Starting Point

Building from scratch with these proven elements:
✅ PyPI publishing with Trusted Publishers (environment: release)
✅ marker-pdf library for conversion

## Requirements

### 1. Python CLI Command (`pdf2md-ocr`)

**Core Functionality:**

```python
# Wrap marker-pdf library call
from marker.convert import convert_single_pdf
from marker.models import load_all_models

# Show progress during model download (if not already cached)
# Allow specifying model cache directory
# Convert PDF to Markdown
```

**What it should do:**

1. Load marker-pdf models (auto-downloads ~2GB first time)
2. Convert PDF file to markdown
3. Save output markdown file
4. Show progress during processing

**Keep it SIMPLE:**

- Single Python file or minimal package structure
- Use click for CLI (already a dependency via marker-pdf)
- Use rich for progress display (already a dependency)
- No complex abstractions

### 2. Dependency Management via uv

**pyproject.toml requirements:**

```toml
[project]
name = "pdf2md-ocr"
version = "0.0.3"
dependencies = [
    "marker-pdf==1.10.1",
    "click",
    "rich",
]

[project.scripts]
pdf2md-ocr = "pdf2md_ocr.cli:main"
```

**Key points:**

- Use uv for all dependency management
- Pin marker-pdf version
- Don't over-specify transitive dependencies
- Use uv.lock for reproducible installs

### 3. PyPI Publishing (THIS WORKS - REUSE EXACTLY)

**Trusted Publisher Configuration:**

- Project: `pdf2md-ocr`
- Workflow: `publish-to-pypi.yml`
- Environment: `release` (CRITICAL - must match)

See PYPI_CONFIG.md for complete working workflow.

### 4. Version & Starting Point

**Start at version 0.0.3** because:

- 0.0.1: Successfully published to PyPI
- 0.0.2: Published but overly complex
- 0.0.3: Fresh start, minimal implementation

## Success Criteria

1. ✅ `uvx pdf2md-ocr@0.0.3 input.pdf -o output.md` works immediately
2. ✅ Publishes to PyPI automatically on tag push
3. ✅ Models cached properly (downloads once, reuses)
4. ✅ Code is simple enough to maintain without AI help
5. ✅ Installation is instant via `uvx` (no need for `pip install`)
6. Use semantic versioning and semantic commits

## What to AVOID

❌ Complex bash scripts with argument parsing
❌ Over-abstraction (interfaces, base classes, etc.)
❌ Pinning all transitive dependencies
❌ Multiple configuration formats
❌ Custom progress/logging frameworks

## Implementation Steps

1. Create minimal Python package structure
2. Simple CLI that wraps marker-pdf (see [REFERENCE.md](./REFERENCE.md) for example)
3. Basic pyproject.toml with uv
4. Use proven PyPI workflow (see [PYPI_CONFIG.md](./PYPI_CONFIG.md))
5. Test locally with `uvx` first, then publish

## Key Principle: KISS (Keep It Simple, Stupid)

- One library call shouldn't need a framework
- CLI args don't need custom interfaces
- Focus on the `uvx` use case - simple and immediate

**Remember:** marker-pdf already does the hard work. Just wrap it with a minimal CLI.
