.PHONY: help install install-dev test test-verbose clean clean-cache build lint format check

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install package in editable mode"
	@echo "  make install-dev    - Install package with dev dependencies"
	@echo "  make test           - Run tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make clean          - Remove build artifacts and cache"
	@echo "  make clean-cache    - Remove AI model cache (~3GB)"
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

# Clean AI model cache (frees ~3GB of disk space)
clean-cache:
	@echo "This will delete the AI model cache (~3GB)."
	@echo "Models will be re-downloaded on next run."
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		if [ -f .venv/bin/python ]; then \
			CACHE_DIR=$$(.venv/bin/python -c "from platformdirs import user_cache_dir; from pathlib import Path; print(Path(user_cache_dir('datalab')) / 'models')"); \
		else \
			CACHE_DIR=$$(python -c "from platformdirs import user_cache_dir; from pathlib import Path; print(Path(user_cache_dir('datalab')) / 'models')"); \
		fi; \
		if [ -d "$$CACHE_DIR" ]; then \
			echo "Removing $$CACHE_DIR..."; \
			rm -rf "$$CACHE_DIR"; \
			echo "Cache cleared successfully!"; \
		else \
			echo "Cache directory not found: $$CACHE_DIR"; \
		fi; \
	else \
		echo "Cancelled."; \
	fi

# Build distribution packages
build: clean
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python -m pip install --upgrade build; \
		.venv/bin/python -m build; \
	else \
		python -m pip install --upgrade build; \
		python -m build; \
	fi

# Run the CLI (example: make run PDF_FILE=sample.pdf OUTPUT=output.md)
run:
	@if [ -z "$(PDF_FILE)" ]; then \
		echo "Error: PDF_FILE variable is required"; \
		echo "Usage: make run PDF_FILE=input.pdf [OUTPUT=output.md]"; \
		exit 1; \
	fi
	@if [ -f .venv/bin/pdf2md-ocr ]; then \
		if [ -n "$(OUTPUT)" ]; then \
			.venv/bin/pdf2md-ocr "$(PDF_FILE)" -o "$(OUTPUT)"; \
		else \
			.venv/bin/pdf2md-ocr "$(PDF_FILE)"; \
		fi; \
	else \
		if [ -n "$(OUTPUT)" ]; then \
			pdf2md-ocr "$(PDF_FILE)" -o "$(OUTPUT)"; \
		else \
			pdf2md-ocr "$(PDF_FILE)"; \
		fi; \
	fi
