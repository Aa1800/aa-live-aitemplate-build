# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python starter template managed with `uv`. Python 3.12 is required.

## Commands

```bash
# Run the main script
uv run main.py

# Add a dependency
uv add <package>

# Run a script/tool within the venv
uv run <script>

# Sync dependencies
uv sync
```

## Project Structure

- `main.py` — entry point
- `pyproject.toml` — project metadata and dependencies
- `uv.lock` — locked dependency versions (commit this file)
- `.python-version` — pins Python to 3.12
