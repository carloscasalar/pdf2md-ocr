# Minimal Docker image for pdf2md-ocr using uvx
FROM ghcr.io/astral-sh/uv:debian

# Install minimal system dependencies required by marker-pdf and pdfium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgobject-2.0-0 \
    libpango-1.0-0 \
    libssl3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m -u 1000 pdf2md

# Set working directory
WORKDIR /workspace

# Change to non-root user
USER pdf2md

# Warm uv cache so first run is fast
RUN uvx pdf2md-ocr --help

# Use uvx to run pdf2md-ocr - this ensures the latest version is always used
ENTRYPOINT ["uvx", "pdf2md-ocr"]

# Default command (can be overridden)
CMD ["--help"]
