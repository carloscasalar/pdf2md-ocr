"""CLI for pdf2md-ocr."""

import os
from pathlib import Path
import shutil
import click


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


def _validate_page_range(start_page: int | None, end_page: int | None) -> None:
    """Validate page range parameters.

    Args:
        start_page: Starting page number (1-based).
        end_page: Ending page number (1-based).

    Raises:
        ValueError: If page numbers are invalid.
    """
    if start_page is not None and start_page < 1:
        raise ValueError("--start-page must be >= 1 (page numbering starts at 1)")
    if end_page is not None and end_page < 1:
        raise ValueError("--end-page must be >= 1 (page numbering starts at 1)")
    if start_page is not None and end_page is not None and start_page > end_page:
        raise ValueError(f"--start-page ({start_page}) cannot be greater than --end-page ({end_page})")


def _page_range_to_marker_format(start_page: int | None, end_page: int | None) -> str | None:
    """Convert 1-based page range to Marker's page_range format (0-based).

    Marker uses 0-based page numbering in its page_range parameter.

    Args:
        start_page: Starting page (1-based), inclusive.
        end_page: Ending page (1-based), inclusive.

    Returns:
        Page range string for Marker (e.g., "1-4" for pages 2-5 in 1-based), or None if no range.
    """
    if start_page is None and end_page is None:
        return None

    # Convert to 0-based for Marker
    marker_start = (start_page - 1) if start_page is not None else None
    marker_end = (end_page - 1) if end_page is not None else None

    if marker_start is None and marker_end is not None:
        # Only end specified: from beginning to end
        return "-" + str(marker_end)
    elif marker_start is not None and marker_end is None:
        # Only start specified: from start to end of document
        return str(marker_start) + "-"
    else:
        # Both specified
        return f"{marker_start}-{marker_end}"


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output markdown file (default: same name as input with .md extension)",
)
@click.option(
    "--stdout",
    is_flag=True,
    help="Write markdown to stdout instead of a file (ignores --output)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress progress messages (stderr only)",
)
@click.option(
    "--start-page",
    type=int,
    default=None,
    help="Start page number (1-based, inclusive). If omitted, starts from page 1.",
)
@click.option(
    "--end-page",
    type=int,
    default=None,
    help="End page number (1-based, inclusive). If omitted, goes to the last page.",
)
@click.option(
    "--show-cache-info",
    is_flag=True,
    help="Show cache location and size after conversion",
)
@click.version_option(version="1.0.0", prog_name="pdf2md-ocr")
def main(
    input_pdf: Path | None,
    output: Path | None,
    stdout: bool,
    quiet: bool,
    start_page: int | None,
    end_page: int | None,
    show_cache_info: bool,
):
    """Convert PDF to Markdown using Marker AI.

    First run downloads ~2-3GB of AI models (cached for future use).

    \b
    Page numbering starts at 1. Examples:
        pdf2md-ocr input.pdf  # Convert all pages
        pdf2md-ocr input.pdf --start-page 2 --end-page 3  # Pages 2 and 3 only
        pdf2md-ocr input.pdf --start-page 5  # From page 5 to end
        pdf2md-ocr input.pdf --end-page 10  # From beginning to page 10

    \b
    Output options:
        --stdout  Write markdown to stdout for piping
        --quiet   Suppress progress messages

    \b
    Cache management:
        --show-cache-info             Show cache location and size
        pdf2md-ocr --show-cache-info  View cache without converting
    """
    # Handle standalone --show-cache-info (no PDF conversion)
    if show_cache_info and input_pdf is None:
        cache_dir = get_cache_dir()
        if cache_dir.exists():
            size = get_cache_size(cache_dir)
            click.echo(f"Cache location: {cache_dir}")
            click.echo(f"Cache size: {format_size(size)}")
            click.echo(f"To clear cache: rm -rf '{cache_dir}'")
        else:
            click.echo(f"Cache location: {cache_dir}")
            click.echo("Cache is empty")
        return

    # INPUT_PDF is required for conversion
    if input_pdf is None:
        raise click.UsageError("INPUT_PDF is required unless using --show-cache-info")

    # Validate page range
    try:
        _validate_page_range(start_page, end_page)
    except ValueError as e:
        raise click.BadParameter(str(e))

    # Build page range string for Marker
    page_range = _page_range_to_marker_format(start_page, end_page)

    # Display conversion info (to stderr if --stdout, unless --quiet)
    pdf_name = input_pdf.name
    if not quiet:
        msg = f"Converting {pdf_name} (pages {start_page or 1} to {end_page or 'end'})..." if page_range else f"Converting {pdf_name}..."
        click.echo(msg, err=stdout)

    # Suppress verbose logging from marker dependencies
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"

    # Import marker modules only when needed (not on --help/--version)
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    # Load models (downloads ~2GB first time, then cached)
    models = create_model_dict()

    # Create converter with optional page range
    if page_range:
        from marker.config.parser import ConfigParser
        config_parser = ConfigParser({"page_range": page_range})
        converter = PdfConverter(
            artifact_dict=models,
            config=config_parser.generate_config_dict(),
        )
    else:
        converter = PdfConverter(artifact_dict=models)

    rendered = converter(str(input_pdf))

    # Extract markdown text (returns tuple: text, extension, images)
    markdown_text, _, _ = text_from_rendered(rendered)

    # Output handling
    if stdout:
        # Write to stdout for piping
        click.echo(markdown_text)
    else:
        # Save to file
        output_path = output or input_pdf.with_suffix(".md")
        output_path.write_text(markdown_text, encoding="utf-8")

        if not quiet:
            click.echo(f"✓ Converted to {output_path}", err=False)

    # Show cache info if requested
    if show_cache_info:
        cache_dir = get_cache_dir()
        if cache_dir.exists():
            size = get_cache_size(cache_dir)
            click.echo(f"\nCache location: {cache_dir}", err=stdout)
            click.echo(f"Cache size: {format_size(size)}", err=stdout)
            click.echo(f"To clear cache: rm -rf '{cache_dir}'", err=stdout)
        else:
            click.echo(f"\nCache location: {cache_dir}", err=stdout)
            click.echo("Cache is empty", err=stdout)


if __name__ == "__main__":
    main()
