# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2025-11-16

### Added
- Initial minimal CLI implementation wrapping marker-pdf library
- Command-line interface with `pdf2md-ocr` command
- Support for PDF to Markdown conversion
- Optional output path specification with `-o` flag
- Automatic output filename generation (input name with .md extension)
- Version command `--version`
- Help command `--help`
- Comprehensive test suite with pytest
- Tests for PDF conversion functionality
- Tests for default output path behavior
- GitHub Actions workflow for automated PyPI publishing using Trusted Publishers
- README with usage instructions and examples
- Project documentation (PROMPT.md, PYPI_CONFIG.md, REFERENCE.md)
- Sample PDF file for testing (pdf-samples/only-text.pdf)

### Changed
- **BREAKING**: License changed from MIT to GPL-3.0-or-later for compliance with marker-pdf dependency

### Fixed
- Correct handling of `text_from_rendered()` tuple return value (text, extension, images)
- Suppress verbose logging from marker-pdf dependencies (GRPC, GLOG)

### Technical Details
- Uses marker-pdf v1.10.1 for PDF conversion
- Built with Python 3.10+ support
- Uses uv for dependency management
- Uses hatchling as build backend
- Implements PyPI Trusted Publishers for secure publishing
- GPL-3.0-or-later licensed (required by marker-pdf dependency)

[0.0.3]: https://github.com/carloscasalar/pdf2md-ocr/releases/tag/v0.0.3
