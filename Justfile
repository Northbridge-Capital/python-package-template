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
