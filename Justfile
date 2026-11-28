# Use PowerShell on Windows so recipes work in CMD, PowerShell, and Git Bash
set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

# Install dependencies into .venv
sync:
    uv sync

# Format, lint and type-check
lint:
    uv run ruff check . --fix
    uv run ruff format .
    uv run basedpyright

# Unit tests with coverage
test:
    uv run pytest --cov --cov-report=term-missing

# Serve the documentation with live reload
docs:
    uv run --group docs sphinx-autobuild docs docs/_build/html

# Build the documentation the way CI does (warnings are errors)
docs-build:
    uv run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html
