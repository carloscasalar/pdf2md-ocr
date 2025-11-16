# Minimal Implementation Reference

## Example Working Code (marker-pdf v1.10.1)

The **essence** of what works (stripped of complexity):

```python
import os
# Suppress verbose logging
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

from pathlib import Path
import click
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

@click.command()
@click.argument('input_pdf', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output markdown file')
def main(input_pdf: Path, output: Path | None):
    """Convert PDF to Markdown using Marker AI."""

    # Load models (downloads ~2GB first time, then cached)
    models = create_model_dict()

    # Create converter and convert PDF
    converter = PdfConverter(artifact_dict=models)
    rendered = converter(str(input_pdf))

    # Extract markdown text (returns tuple: text, extension, images)
    markdown_text, _, _ = text_from_rendered(rendered)

    # Save output
    output_path = output or input_pdf.with_suffix(".md")
    output_path.write_text(markdown_text, encoding="utf-8")

    click.echo(f"✓ Converted to {output_path}")
```

## What NOT to Add

❌ Custom progress bars (marker-pdf has its own)
❌ Metadata JSON files
❌ Image extraction to folders
❌ Complex error handling
❌ Logging frameworks

## Model Caching

Marker automatically caches models to:

- `$HF_HOME` (default: `~/.cache/huggingface`)
- `$TRANSFORMERS_CACHE` (default: `~/.cache/transformers`)

First run downloads ~2GB of models, then reuses them forever.

## Dependencies (from pyproject.toml)

```toml
dependencies = [
    "marker-pdf==1.10.1",  # Does all the heavy lifting
    "click",               # CLI (transitive from marker)
    "rich",                # Progress (transitive from marker)
]
```

That's it. Everything else is transitive and managed by uv.

## Usage Example

```bash
# Install and run in one command (recommended)
uvx pdf2md-ocr input.pdf -o output.md

# Or install traditionally
pip install pdf2md-ocr
pdf2md-ocr input.pdf -o output.md
```

First run downloads models (~2GB) which are then cached for future runs.
