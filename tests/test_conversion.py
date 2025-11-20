"""Test PDF to Markdown conversion."""

import os
from pathlib import Path
import tempfile
import pytest
from click.testing import CliRunner

from pdf2md_ocr.cli import main, _validate_page_range, _page_range_to_marker_format


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


def test_convert_three_page_pdf_with_page_range():
    """Test conversion of three-page.pdf with page range (pages 2-3) restricts output correctly."""
    runner = CliRunner()
    
    project_root = Path(__file__).parent.parent
    input_pdf = project_root / "pdf-samples" / "three-page.pdf"
    
    # Verify the input file exists
    assert input_pdf.exists(), f"Test PDF not found at {input_pdf}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_md = Path(tmpdir) / "output.md"
        
        # Run the CLI command with page range 2-3 (1-based page numbering)
        result = runner.invoke(main, [
            str(input_pdf),
            "-o", str(output_md),
            "--start-page", "2",
            "--end-page", "3"
        ])
        
        # Check the command succeeded
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert output_md.exists(), "Output markdown file was not created"
        
        # Read the generated markdown
        content = output_md.read_text(encoding="utf-8")
        
        # Verify page 1 content is NOT present
        # The markdown should NOT contain "**Page 1**" or its specific content
        assert "**Page 1**" not in content, (
            "Page 1 content should not be present when limiting to pages 2-3.\n"
            f"Generated content:\n{content}"
        )
        
        # Verify pages 2 and 3 content IS present
        assert "**Page 2**" in content, (
            "Page 2 content should be present when limiting to pages 2-3.\n"
            f"Generated content:\n{content}"
        )
        assert "**Page 3**" in content, (
            "Page 3 content should be present when limiting to pages 2-3.\n"
            f"Generated content:\n{content}"
        )
        
        # Verify it's a non-trivial conversion
        assert len(content) > 50, f"Output too short ({len(content)} chars): {content}"


class TestPageRangeValidation:
    """Test page range validation logic."""

    def test_validate_page_range_valid_both_specified(self):
        """Test validation passes when both start and end are valid and in order."""
        # Should not raise
        _validate_page_range(1, 5)
        _validate_page_range(2, 3)
        _validate_page_range(1, 1)

    def test_validate_page_range_valid_only_start(self):
        """Test validation passes when only start is specified."""
        # Should not raise
        _validate_page_range(1, None)
        _validate_page_range(5, None)

    def test_validate_page_range_valid_only_end(self):
        """Test validation passes when only end is specified."""
        # Should not raise
        _validate_page_range(None, 1)
        _validate_page_range(None, 10)

    def test_validate_page_range_valid_neither(self):
        """Test validation passes when neither is specified."""
        # Should not raise
        _validate_page_range(None, None)

    def test_validate_page_range_start_zero(self):
        """Test validation fails when start_page is 0."""
        with pytest.raises(ValueError, match="--start-page must be >= 1"):
            _validate_page_range(0, 5)

    def test_validate_page_range_start_negative(self):
        """Test validation fails when start_page is negative."""
        with pytest.raises(ValueError, match="--start-page must be >= 1"):
            _validate_page_range(-1, 5)

    def test_validate_page_range_end_zero(self):
        """Test validation fails when end_page is 0."""
        with pytest.raises(ValueError, match="--end-page must be >= 1"):
            _validate_page_range(1, 0)

    def test_validate_page_range_end_negative(self):
        """Test validation fails when end_page is negative."""
        with pytest.raises(ValueError, match="--end-page must be >= 1"):
            _validate_page_range(1, -1)

    def test_validate_page_range_start_greater_than_end(self):
        """Test validation fails when start_page > end_page."""
        with pytest.raises(ValueError, match="--start-page .* cannot be greater than --end-page"):
            _validate_page_range(5, 2)

    def test_validate_page_range_start_equal_to_end(self):
        """Test validation passes when start_page == end_page."""
        # Should not raise
        _validate_page_range(3, 3)


class TestPageRangeFormatConversion:
    """Test page range format conversion from 1-based to Marker's 0-based format."""

    def test_both_specified(self):
        """Test conversion when both start and end are specified."""
        # Pages 2-5 (1-based) -> "1-4" (0-based for Marker)
        assert _page_range_to_marker_format(2, 5) == "1-4"
        assert _page_range_to_marker_format(1, 1) == "0-0"
        assert _page_range_to_marker_format(1, 3) == "0-2"

    def test_only_start_specified(self):
        """Test conversion when only start_page is specified."""
        # Pages 3 to end (1-based) -> "2-" (0-based for Marker)
        assert _page_range_to_marker_format(3, None) == "2-"
        assert _page_range_to_marker_format(1, None) == "0-"
        assert _page_range_to_marker_format(10, None) == "9-"

    def test_only_end_specified(self):
        """Test conversion when only end_page is specified."""
        # Pages 1 to 5 (1-based) -> "-4" (0-based for Marker)
        assert _page_range_to_marker_format(None, 5) == "-4"
        assert _page_range_to_marker_format(None, 1) == "-0"
        assert _page_range_to_marker_format(None, 10) == "-9"

    def test_neither_specified(self):
        """Test conversion when neither is specified."""
        # All pages -> None
        assert _page_range_to_marker_format(None, None) is None


class TestPageRangeCliValidation:
    """Test page range validation through the CLI interface."""

    def test_cli_invalid_start_page_zero(self):
        """Test CLI error when start_page is 0."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [
            str(input_pdf),
            "--start-page", "0"
        ])

        assert result.exit_code == 2
        assert "page numbering starts at 1" in result.output

    def test_cli_invalid_start_page_negative(self):
        """Test CLI error when start_page is negative."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [
            str(input_pdf),
            "--start-page", "-5"
        ])

        assert result.exit_code == 2
        assert "page numbering starts at 1" in result.output

    def test_cli_invalid_end_page_zero(self):
        """Test CLI error when end_page is 0."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [
            str(input_pdf),
            "--end-page", "0"
        ])

        assert result.exit_code == 2
        assert "page numbering starts at 1" in result.output

    def test_cli_invalid_start_greater_than_end(self):
        """Test CLI error when start_page > end_page."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [
            str(input_pdf),
            "--start-page", "5",
            "--end-page", "2"
        ])

        assert result.exit_code == 2
        assert "cannot be greater than" in result.output
