# Minimal Implementation Reference

## Example Working Code

The **essence** of what works (stripped of complexity):

```python
from pathlib import Path
import click
from marker.convert import convert_single_pdf
from marker.models import load_all_models

@click.command()
@click.argument('input_pdf', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output markdown file')
def main(input_pdf, output):
    """Convert PDF to Markdown using Marker AI."""

    # Load models (downloads ~2GB first time, then cached)
    model_list = load_all_models()

    # Convert PDF
    full_text, images, metadata = convert_single_pdf(
        input_pdf,
        model_list
    )

    # Save output
    output_path = Path(output or f"{Path(input_pdf).stem}.md")
    output_path.write_text(full_text)

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
