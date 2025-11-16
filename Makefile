.PHONY: help install install-dev test test-verbose clean build lint format check

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install package in editable mode"
	@echo "  make install-dev    - Install package with dev dependencies"
	@echo "  make test           - Run tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make clean          - Remove build artifacts and cache"
	@echo "  make build          - Build distribution packages"
	@echo "  make run            - Run pdf2md-ocr CLI (requires PDF_FILE variable)"

# Install package in editable mode
install:
	uv pip install -e .

# Install package with dev dependencies
install-dev:
	uv pip install -e ".[dev]"

# Run tests
test:
	@if [ -f .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/; \
	else \
		pytest tests/; \
	fi

# Run tests with verbose output
test-verbose:
	@if [ -f .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/ -v; \
	else \
		pytest tests/ -v; \
	fi

# Clean build artifacts and cache
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf out/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Build distribution packages
build: clean
	python -m pip install --upgrade build
	python -m build

# Run the CLI (example: make run PDF_FILE=sample.pdf OUTPUT=output.md)
run:
	@if [ -z "$(PDF_FILE)" ]; then \
		echo "Error: PDF_FILE variable is required"; \
		echo "Usage: make run PDF_FILE=input.pdf [OUTPUT=output.md]"; \
		exit 1; \
	fi
	@if [ -n "$(OUTPUT)" ]; then \
		pdf2md-ocr "$(PDF_FILE)" -o "$(OUTPUT)"; \
	else \
		pdf2md-ocr "$(PDF_FILE)"; \
	fi
