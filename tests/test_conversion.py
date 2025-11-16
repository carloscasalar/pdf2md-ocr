"""Test PDF to Markdown conversion."""

import os
from pathlib import Path
import tempfile
import pytest
from click.testing import CliRunner

from pdf2md_ocr.cli import main


def test_convert_only_text_pdf():
    """Test conversion of pdf-samples/only-text.pdf produces expected markdown content."""
    runner = CliRunner()
    
    # Use the sample PDF from the project
    project_root = Path(__file__).parent.parent
    input_pdf = project_root / "pdf-samples" / "only-text.pdf"
    
    # Verify the input file exists
    assert input_pdf.exists(), f"Test PDF not found at {input_pdf}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_md = Path(tmpdir) / "output.md"
        
        # Run the CLI command
        result = runner.invoke(main, [str(input_pdf), "-o", str(output_md)])
        
        # Check the command succeeded
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert output_md.exists(), "Output markdown file was not created"
        
        # Read the generated markdown
        content = output_md.read_text(encoding="utf-8")
        
        # Verify expected content is present
        # Based on the actual output from out/only-text.md
        expected_texts = [
            "Document Title",
            "First paragraph",
            "Some subtitle",
            "Paragraph in the subtitle"
        ]
        
        for expected_text in expected_texts:
            assert expected_text in content, (
                f"Expected text '{expected_text}' not found in output.\n"
                f"Generated content:\n{content}"
            )
        
        # Verify it's a non-trivial conversion (at least some reasonable length)
        assert len(content) > 50, f"Output too short ({len(content)} chars): {content}"


def test_convert_only_text_pdf_default_output():
    """Test conversion with default output filename (input name with .md extension)."""
    runner = CliRunner()
    
    project_root = Path(__file__).parent.parent
    input_pdf = project_root / "pdf-samples" / "only-text.pdf"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy PDF to temp dir to test default output location
        temp_pdf = Path(tmpdir) / "test.pdf"
        temp_pdf.write_bytes(input_pdf.read_bytes())
        
        # Run without -o flag (should create test.md in same directory)
        result = runner.invoke(main, [str(temp_pdf)])
        
        assert result.exit_code == 0
        
        # Check default output file was created
        expected_output = Path(tmpdir) / "test.md"
        assert expected_output.exists(), "Default output file was not created"
        
        content = expected_output.read_text(encoding="utf-8")
        assert "Document Title" in content
