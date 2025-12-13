# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2025-12-13

### Fixed

- Fixed hanging issue when running `--help` or `--version` commands
  - Lazy-load marker modules only when actually converting PDFs
  - Commands like `uvx pdf2md-ocr --help` now run instantly instead of trying to load AI models

[0.0.5]: https://github.com/carloscasalar/pdf2md-ocr/releases/tag/v0.0.5

## [0.0.4] - 2025-11-20

### Added

- Page range extraction feature: convert only specific pages from a PDF
  - `--start-page N`: Start conversion from page N (1-based, inclusive)
  - `--end-page M`: End conversion at page M (1-based, inclusive)
  - Both options are optional and can be combined for flexible page selection
  - Page numbering starts at 1 (not 0)

[0.0.4]: https://github.com/carloscasalar/pdf2md-ocr/releases/tag/v0.0.4

## [0.0.3] - 2025-11-16

### Added

- Changed to a simpler implementation of `pdf2md-ocr`:
  - Optional output path specification with `-o` flag
  - Automatic output filename generation (input name with .md extension)
  - Option to show cache info so the user can easily clean it `--show-cache-info`
  - Version command `--version`
  - Help command `--help`
- Comprehensive test suite with pytest
- Tests for PDF conversion functionality
- Tests for default output path behavior

### Technical Details

- Uses marker-pdf v1.10.1 for PDF conversion
- Built with Python 3.10+ support
- Uses uv for dependency management
- Uses hatchling as build backend
- Implements PyPI Trusted Publishers for secure publishing
- GPL-3.0-or-later licensed (required by marker-pdf dependency)

## Note on Versions 0.0.1 and 0.0.2

Versions 0.0.1 and 0.0.2 were part of a failed start and existed in a deleted repository.
Version 0.0.3 represents the first official release of this project.

[0.0.3]: https://github.com/carloscasalar/pdf2md-ocr/releases/tag/v0.0.3
