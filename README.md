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

# Show help
pdf2md-ocr --help

# Show version
pdf2md-ocr --version
```

## First Run

The first time you run pdf2md-ocr, it will download ~2GB of AI models from Hugging Face. These models are cached locally (in `~/.cache/huggingface` by default) and reused for all future conversions.

Subsequent runs will be much faster since the models are already cached.

## Requirements

- Python 3.10 or higher
- ~2GB disk space for AI models (one-time download)

## How It Works

This tool is a minimal wrapper around the excellent [marker-pdf](https://github.com/VikParuchuri/marker) library, which uses AI models to:

1. Detect text, tables, and equations in PDFs
2. Extract content with proper formatting
3. Convert to clean Markdown

## License

MIT
