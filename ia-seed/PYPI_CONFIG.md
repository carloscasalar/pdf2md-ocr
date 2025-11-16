# PyPI Trusted Publisher Config (PROVEN TO WORK)

## PyPI Project Settings

https://pypi.org/manage/project/pdf2md-ocr/settings/publishing/

**Configuration:**

- Owner: carloscasalar
- Repository name: pdf2md-ocr
- Workflow name: publish-to-pypi.yml
- Environment name: release

**No secrets or tokens needed** - OIDC Trusted Publishers handle everything.

## Working Workflow Template

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release # MUST MATCH PYPI CONFIG
    permissions:
      contents: read
      id-token: write # FOR OIDC

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Build package
        run: |
          python -m pip install build
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No credentials needed - uses Trusted Publisher
```

## Git Tag Format

```bash
git tag -a v0.0.3 -m "Release v0.0.3: Clean reboot"
git push origin v0.0.3
```

## Test Installation

**Recommended (instant, no install needed):**

```bash
uvx pdf2md-ocr@0.0.3 --version
uvx pdf2md-ocr@0.0.3 input.pdf -o output.md
```

**Traditional:**

```bash
pip install pdf2md-ocr==0.0.3
pdf2md-ocr --version
```
