# pdf2md-ocr

Simple CLI tool to convert PDFs to Markdown using [Marker AI](https://github.com/VikParuchuri/marker).

## Quick Start

**Recommended (no installation needed):**

```bash
uvx pdf2md-ocr input.pdf -o output.md
```

**Traditional installation:**

```bash
pip install pdf2md-ocr
pdf2md-ocr input.pdf -o output.md
```

## Usage

```bash
# Convert PDF to Markdown (output same name with .md extension)
pdf2md-ocr document.pdf

# Specify output file
pdf2md-ocr document.pdf -o result.md

# Show cache location and size
pdf2md-ocr document.pdf --show-cache-info

# Show help
pdf2md-ocr --help

# Show version
pdf2md-ocr --version
```

## First Run

The first time you run pdf2md-ocr, it will download ~2-3GB of AI models. These models are cached locally and reused for all future conversions.

**To see where models are cached:**

```bash
pdf2md-ocr input.pdf --show-cache-info
```

This will show the cache location and size after conversion. Cache locations, typically:
- macOS: `~/Library/Caches/datalab/models/`
- Linux: `~/.cache/datalab/models/`
- Windows: `%LOCALAPPDATA%\datalab\models\`

**To clear the cache:** Simply delete the cache directory shown in the info above, or use `make clean-cache` if developing locally.

Subsequent runs will be much faster since the models are already cached.

## Requirements

- Python 3.10 or higher
- ~2GB disk space for AI models (one-time download)

## Development

For development, a Makefile is provided with common tasks:

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Run tests with verbose output
make test-verbose

# Clean build artifacts
make clean

# Clear AI model cache (frees ~3GB disk space)
make clean-cache

# Build distribution packages
make build

# See all available commands
make help
```

## How It Works

This tool is a minimal wrapper around the excellent [marker-pdf](https://github.com/VikParuchuri/marker) library, which uses AI models to:

1. Detect text, tables, and equations in PDFs
2. Extract content with proper formatting
3. Convert to clean Markdown

## License

GPL-3.0-or-later

This project is licensed under the GNU General Public License v3.0 or later to comply with the [marker-pdf](https://github.com/VikParuchuri/marker) library license (GPL-3.0-or-later).
