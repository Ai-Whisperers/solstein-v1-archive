"""Solstein CLI — first-class API client entrypoint.

STORY-118: The CLI is a proper package entrypoint registered in pyproject.toml.
All commands call the API via HTTP rather than importing domain layers directly.

Usage:
    solstein --help
    solstein login
    solstein companies list
    solstein research "Company X"
    solstein export <company_id> --format excel
    solstein status <job_id>
"""

from solstein.cli.app import cli, main

__all__ = ["cli", "main"]
