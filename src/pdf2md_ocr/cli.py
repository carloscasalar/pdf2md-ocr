"""CLI for pdf2md-ocr."""

import os

# Suppress verbose logging from marker dependencies
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

from pathlib import Path
import shutil
import click
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


def get_cache_dir() -> Path:
    """Get the model cache directory."""
    from platformdirs import user_cache_dir
    return Path(user_cache_dir("datalab")) / "models"


def get_cache_size(path: Path) -> int:
    """Get the size of a directory in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output markdown file (default: same name as input with .md extension)",
)
@click.option(
    "--show-cache-info",
    is_flag=True,
    help="Show cache location and size after conversion",
)
@click.version_option(version="0.0.3", prog_name="pdf2md-ocr")
def main(input_pdf: Path, output: Path | None, show_cache_info: bool):
    """Convert PDF to Markdown using Marker AI.
    
    First run downloads ~2-3GB of AI models (cached for future use).
    
    Cache management:
      --show-cache-info    Show where models are cached and how much space they use
    
    Example:
        pdf2md-ocr input.pdf -o output.md
        pdf2md-ocr input.pdf --show-cache-info
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
    
    # Show cache info if requested
    if show_cache_info:
        cache_dir = get_cache_dir()
        if cache_dir.exists():
            size = get_cache_size(cache_dir)
            click.echo(f"\nCache location: {cache_dir}")
            click.echo(f"Cache size: {format_size(size)}")
            click.echo(f"To clear cache: rm -rf '{cache_dir}'")
        else:
            click.echo(f"\nCache location: {cache_dir}")
            click.echo("Cache is empty")


if __name__ == "__main__":
    main()
