"""Test PDF to Markdown conversion."""

import os
from pathlib import Path
import tempfile
import pytest
from click.testing import CliRunner
from pypdf import PdfReader

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
        """Test conversion when only start_page is specified (requires total_pages)."""
        # Pages 3 to end of 10-page doc (1-based) -> "2-9" (0-based for Marker)
        assert _page_range_to_marker_format(3, None, total_pages=10) == "2-9"
        assert _page_range_to_marker_format(1, None, total_pages=5) == "0-4"
        assert _page_range_to_marker_format(10, None, total_pages=15) == "9-14"

    def test_only_end_specified(self):
        """Test conversion when only end_page is specified."""
        # Pages 1 to 5 (1-based) -> "0-4" (0-based for Marker)
        assert _page_range_to_marker_format(None, 5) == "0-4"
        assert _page_range_to_marker_format(None, 1) == "0-0"
        assert _page_range_to_marker_format(None, 10) == "0-9"

    def test_neither_specified(self):
        """Test conversion when neither is specified."""
        # All pages -> None
        assert _page_range_to_marker_format(None, None) is None

    def test_only_start_specified_missing_total_pages(self):
        """Test that start_page without end_page requires total_pages."""
        with pytest.raises(ValueError, match="total_pages is required"):
            _page_range_to_marker_format(5, None)


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


class TestStdoutAndQuietOptions:
    """Test --stdout and --quiet CLI options."""

    def test_stdout_writes_to_stdout(self):
        """Test that --stdout writes markdown to stdout instead of file."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [str(input_pdf), "--stdout"])

        assert result.exit_code == 0
        # Markdown content should be in stdout
        assert "Document Title" in result.output
        assert len(result.output) > 100  # Should have substantial content

    def test_stdout_with_quiet_suppresses_progress(self):
        """Test that --stdout --quiet only outputs markdown."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        result = runner.invoke(main, [str(input_pdf), "--stdout", "--quiet"])

        assert result.exit_code == 0
        # Should NOT have progress messages
        assert "Converting" not in result.output
        assert "✓" not in result.output
        # Should have markdown content
        assert "Document Title" in result.output

    def test_quiet_suppresses_file_output_messages(self):
        """Test that --quiet suppresses progress when writing to file."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_md = Path(tmpdir) / "output.md"
            result = runner.invoke(main, [str(input_pdf), "-o", str(output_md), "--quiet"])

            assert result.exit_code == 0
            assert output_md.exists()
            # Should NOT have progress messages in output
            assert "Converting" not in result.output
            assert "✓ Converted" not in result.output

    def test_stdout_ignores_output_flag(self):
        """Test that --stdout ignores --output flag."""
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "only-text.pdf"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_md = Path(tmpdir) / "output.md"
            result = runner.invoke(main, [
                str(input_pdf),
                "--stdout",
                "-o", str(output_md)
            ])

            assert result.exit_code == 0
            # File should NOT be created when using --stdout
            assert not output_md.exists()
            # Content should be in stdout
            assert "Document Title" in result.output


class TestStandaloneCacheInfo:
    """Test --show-cache-info without INPUT_PDF."""

    def test_show_cache_info_standalone(self):
        """Test that --show-cache-info works without INPUT_PDF."""
        runner = CliRunner()
        result = runner.invoke(main, ["--show-cache-info"])

        assert result.exit_code == 0
        # Should show cache location
        assert "Cache location:" in result.output
        # Should show either cache size or "empty" message
        assert "Cache size:" in result.output or "Cache is empty" in result.output

    def test_no_input_pdf_without_show_cache_info_fails(self):
        """Test that running without INPUT_PDF and without --show-cache-info fails."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code == 2
        assert "INPUT_PDF is required" in result.output


class TestStartPageWithoutEndPage:
    """Test --start-page without --end-page functionality."""

    def test_pypdf_reads_page_count_correctly(self):
        """Test that pypdf can read the page count from a multi-page PDF."""
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "three-page.pdf"
        
        # Verify the input file exists
        assert input_pdf.exists(), f"Test PDF not found at {input_pdf}"
        
        # Read page count with pypdf
        pdf_reader = PdfReader(str(input_pdf))
        total_pages = len(pdf_reader.pages)
        
        # Verify the three-page.pdf has 3 pages
        assert total_pages == 3, f"Expected 3 pages, got {total_pages}"

    def test_page_range_conversion_with_start_only(self):
        """Test that _page_range_to_marker_format correctly converts start-page-only range."""
        # Test with start_page=2 on a 3-page document
        # Should convert to "1-2" (0-based, from page 2 to page 3)
        result = _page_range_to_marker_format(2, None, total_pages=3)
        assert result == "1-2", f"Expected '1-2', got '{result}'"
        
        # Test with start_page=1 on a 5-page document
        # Should convert to "0-4" (0-based, from page 1 to page 5)
        result = _page_range_to_marker_format(1, None, total_pages=5)
        assert result == "0-4", f"Expected '0-4', got '{result}'"

    def test_start_page_without_end_page_invalid_pdf(self):
        """Test error handling when pypdf cannot read the PDF page count."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake PDF file that's not actually a valid PDF
            fake_pdf = Path(tmpdir) / "invalid.pdf"
            fake_pdf.write_text("This is not a PDF file")

            output_md = Path(tmpdir) / "output.md"

            # Run the CLI command with only --start-page
            result = runner.invoke(main, [
                str(fake_pdf),
                "-o", str(output_md),
                "--start-page", "2"
            ])

            # Should fail with appropriate error message
            assert result.exit_code != 0, "Should fail when PDF cannot be read"
            assert "Failed to read PDF page count" in result.output, (
                f"Expected error message about reading PDF, got: {result.output}"
            )
            assert "Please specify both --start-page and --end-page" in result.output, (
                f"Expected helpful message about specifying both pages, got: {result.output}"
            )

    def test_start_page_without_end_page_nonexistent_file(self):
        """Test error handling when the PDF file doesn't exist."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Reference a file that doesn't exist
            nonexistent_pdf = Path(tmpdir) / "nonexistent.pdf"
            output_md = Path(tmpdir) / "output.md"

            # Run the CLI command with only --start-page
            result = runner.invoke(main, [
                str(nonexistent_pdf),
                "-o", str(output_md),
                "--start-page", "2"
            ])

            # Should fail with appropriate error message
            # Click validates file existence before we try to read it with pypdf
            assert result.exit_code != 0, "Should fail when PDF file doesn't exist"
            assert "does not exist" in result.output, (
                f"Expected error message about file not existing, got: {result.output}"
            )

    @pytest.mark.slow
    def test_start_page_without_end_page_processes_to_end(self):
        """Test that specifying only --start-page processes from that page to the end of the document.
        
        This is an integration test that requires network access to download ML models.
        """
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "three-page.pdf"

        # Verify the input file exists
        assert input_pdf.exists(), f"Test PDF not found at {input_pdf}"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_md = Path(tmpdir) / "output.md"

            # Run the CLI command with only --start-page=2 (should process pages 2-3)
            result = runner.invoke(main, [
                str(input_pdf),
                "-o", str(output_md),
                "--start-page", "2"
            ])

            # Check the command succeeded
            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert output_md.exists(), "Output markdown file was not created"

            # Read the generated markdown
            content = output_md.read_text(encoding="utf-8")

            # Verify page 1 content is NOT present
            assert "**Page 1**" not in content, (
                "Page 1 content should not be present when starting from page 2.\n"
                f"Generated content:\n{content}"
            )

            # Verify pages 2 and 3 content IS present
            assert "**Page 2**" in content, (
                "Page 2 content should be present when starting from page 2.\n"
                f"Generated content:\n{content}"
            )
            assert "**Page 3**" in content, (
                "Page 3 content should be present when starting from page 2.\n"
                f"Generated content:\n{content}"
            )

            # Verify it's a non-trivial conversion
            assert len(content) > 50, f"Output too short ({len(content)} chars): {content}"

    @pytest.mark.slow
    def test_start_page_without_end_page_single_page(self):
        """Test that specifying --start-page on the last page works correctly.
        
        This is an integration test that requires network access to download ML models.
        """
        runner = CliRunner()
        project_root = Path(__file__).parent.parent
        input_pdf = project_root / "pdf-samples" / "three-page.pdf"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_md = Path(tmpdir) / "output.md"

            # Run the CLI command with only --start-page=3 (should process only page 3)
            result = runner.invoke(main, [
                str(input_pdf),
                "-o", str(output_md),
                "--start-page", "3"
            ])

            # Check the command succeeded
            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert output_md.exists(), "Output markdown file was not created"

            # Read the generated markdown
            content = output_md.read_text(encoding="utf-8")

            # Verify pages 1 and 2 content are NOT present
            assert "**Page 1**" not in content, (
                "Page 1 content should not be present when starting from page 3.\n"
                f"Generated content:\n{content}"
            )
            assert "**Page 2**" not in content, (
                "Page 2 content should not be present when starting from page 3.\n"
                f"Generated content:\n{content}"
            )

            # Verify page 3 content IS present
            assert "**Page 3**" in content, (
                "Page 3 content should be present when starting from page 3.\n"
                f"Generated content:\n{content}"
            )
