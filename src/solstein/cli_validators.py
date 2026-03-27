"""
STORY-172: Structured input validation for CLI commands.

Provides actionable error messages for all foreseeable failure modes:
file-not-found, empty file, malformed JSON, unrecognised structure,
unknown company name, and unwritable output directory.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from .domain.models import Company

# Keys we accept in a wrapped JSON object
_WRAPPER_KEYS = ("competitors", "companies", "data")


def validate_input_file(path: Path) -> None:
    """Validate that *path* is a readable, non-empty, well-formed JSON file
    with a recognised company-list structure.

    Raises ``click.UsageError`` on the first failure found so the user gets
    one clear, actionable message instead of a raw Python traceback.

    Checks (in order):
    1. Path exists on disk.
    2. Path refers to a regular file (not a directory).
    3. File has non-zero size.
    4. Content is valid JSON.
    5. Top-level value is a list, or a dict with one of the known wrapper
       keys (``competitors``, ``companies``, ``data``) whose value is a list.
    """
    if not path.exists():
        raise click.UsageError(f"Input file '{path}' not found.")

    if not path.is_file():
        raise click.UsageError(f"'{path}' is a directory, not a file.")

    if path.stat().st_size == 0:
        raise click.UsageError(f"Input file '{path}' is empty.")

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise click.UsageError(f"Cannot read '{path}': {exc}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise click.UsageError(
            f"Invalid JSON in '{path}': {exc.msg} (line {exc.lineno}, col {exc.colno})"
        ) from exc

    _validate_company_list_structure(data, path)


def _validate_company_list_structure(data: object, source: Path) -> None:
    """Check that *data* is a list or a wrapped dict; raise UsageError otherwise."""
    if isinstance(data, list):
        return

    if isinstance(data, dict):
        for key in _WRAPPER_KEYS:
            if isinstance(data.get(key), list):
                return
        known = "', '".join(_WRAPPER_KEYS)
        raise click.UsageError(
            f"Unsupported JSON structure in '{source}'. "
            f"Expected a list of companies, or an object with a '{known}' key."
        )

    raise click.UsageError(
        f"Unsupported JSON structure in '{source}'. "
        "Expected a JSON array or an object containing a list of companies."
    )


def validate_company_exists(companies: list[Company], name: str) -> Company:
    """Find a company by *name* and return it.

    Matching strategy (first match wins):
    1. Exact ``id`` match.
    2. Exact ``name`` match (case-insensitive).
    3. Case-insensitive substring match (unique result).

    Raises ``click.UsageError`` with a helpful message when:
    - No company matches at all (includes a "did you mean?" suggestion).
    - The substring match is ambiguous (multiple results).
    """
    # 1. ID match
    for company in companies:
        if company.id == name:
            return company

    # 2. Exact name match (case-insensitive)
    name_lower = name.lower()
    exact = [c for c in companies if c.name.lower() == name_lower]
    if exact:
        return exact[0]

    # 3. Substring match
    partial = [c for c in companies if name_lower in c.name.lower()]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        suggestions = ", ".join(c.name for c in partial[:5])
        raise click.UsageError(
            f"Company '{name}' is ambiguous — multiple matches found: {suggestions}. "
            "Please use a more specific name or the exact company ID."
        )

    # No match — show available names and a "did you mean?" hint
    all_names = [c.name for c in companies]
    available = ", ".join(all_names[:10])
    if len(all_names) > 10:
        available += f", … ({len(all_names) - 10} more)"

    close = difflib.get_close_matches(name, all_names, n=3, cutoff=0.5)
    msg = f"Company '{name}' not found.\nAvailable companies: {available}"
    if close:
        msg += f"\nDid you mean: {', '.join(close)}?"
    raise click.UsageError(msg)


def validate_output_dir(path: Path) -> Path:
    """Ensure *path* exists as a writable directory.

    Creates the directory (and any missing parents) if it does not already
    exist.  Raises ``click.UsageError`` if the directory cannot be created or
    is not writable.

    Returns *path* for convenient chaining.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise click.UsageError(
            f"Cannot create output directory '{path}': {exc}"
        ) from exc

    # Verify write permission with a probe file
    probe = path / ".solstein_write_probe"
    try:
        probe.touch()
        probe.unlink()
    except OSError as exc:
        raise click.UsageError(
            f"Output directory '{path}' is not writable: {exc}"
        ) from exc

    return path
