"""CLI for pdf2md-ocr."""

import os

# Suppress verbose logging from marker dependencies
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

from pathlib import Path
import click
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output markdown file (default: same name as input with .md extension)",
)
@click.version_option(version="0.0.3", prog_name="pdf2md-ocr")
def main(input_pdf: Path, output: Path | None):
    """Convert PDF to Markdown using Marker AI.
    
    First run downloads ~2GB of AI models (cached for future use).
    
    Example:
        pdf2md-ocr input.pdf -o output.md
    """
    click.echo(f"Converting {input_pdf}...")
    
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


if __name__ == "__main__":
    main()
