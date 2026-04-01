#!/usr/bin/env python3
"""Validate that .env.example covers all Settings fields defined in config.py.

Parses the Pydantic Settings class and its nested models from config.py, then
checks that every top-level environment variable name appears in .env.example
(either as an active line or a commented-out line).

Exit codes:
    0 — all fields covered
    1 — one or more fields missing from .env.example

Usage:
    python scripts/validate_env_example.py
    python scripts/validate_env_example.py --config src/solstein/config.py --env .env.example
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Exclusions: Settings field names that intentionally have no entry in
# .env.example (internal implementation fields, not user-facing config).
# A false positive is acceptable; a false negative is not.
# ---------------------------------------------------------------------------
EXCLUSION_LIST: set[str] = {
    # Pydantic / BaseSettings internal
    "model_config",
}

# Sub-model fields that are nested under a Settings field (e.g. DATABASE__URL).
# These are covered by section comments in .env.example rather than individual
# top-level entries. The parent field (DATABASE, API, etc.) must be present.
NESTED_MODELS: set[str] = {
    "database",
    "api",
    "security",
    "logging",
    "data",
    "supabase",
    "http_timeouts",
    "circuit_breaker",
    "celery_timing",
}


def extract_settings_fields(config_path: Path) -> list[str]:
    """Parse field names from the Settings class in config.py.

    Uses regex to find all instance-level field declarations inside the
    Settings(BaseSettings) class body. Does not eval or import the module
    so it works without installing dependencies.
    """
    text = config_path.read_text(encoding="utf-8")

    # Isolate the Settings class body (stop at next top-level class or EOF)
    settings_match = re.search(
        r"^class Settings\(BaseSettings\):(.*?)^(?=class |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not settings_match:
        print("ERROR: Could not find 'class Settings(BaseSettings)' in config.py", file=sys.stderr)
        sys.exit(1)

    body = settings_match.group(1)

    # Match lines like "    field_name: SomeType = ..." (4 spaces indent, lower-snake)
    field_re = re.compile(r"^\s{4}([a-z_][a-z0-9_]*)\s*:", re.MULTILINE)
    fields = field_re.findall(body)

    # Filter out methods (def blocks), class-level dunder attrs, and exclusions
    method_names: set[str] = set(re.findall(r"def\s+([a-z_][a-z0-9_]*)\s*\(", body))
    return [
        f for f in fields
        if f not in method_names and f not in EXCLUSION_LIST
    ]


def extract_env_example_vars(env_path: Path) -> set[str]:
    """Return all variable names found in .env.example.

    Captures both active lines (VAR=value) and commented-out lines (# VAR=value).
    Variable names are returned in uppercase.
    """
    text = env_path.read_text(encoding="utf-8")
    var_re = re.compile(r"^#?\s*([A-Z_][A-Z0-9_]*(?:__[A-Z_][A-Z0-9_]*)*)=", re.MULTILINE)
    return {m.group(1).upper() for m in var_re.finditer(text)}


def field_to_env_var(field_name: str) -> str:
    """Convert a Pydantic field name to its expected environment variable name."""
    return field_name.upper()


def nested_section_covered(field_name: str, env_vars: set[str]) -> bool:
    """Check if a nested-model field has at least one sub-field entry in .env.example."""
    prefix = field_name.upper() + "__"
    return any(v.startswith(prefix) for v in env_vars)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("src/solstein/config.py"),
        help="Path to config.py (default: src/solstein/config.py)",
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=Path(".env.example"),
        help="Path to .env.example (default: .env.example)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print covered fields in addition to missing ones",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"ERROR: config file not found: {args.config}", file=sys.stderr)
        return 1

    if not args.env.exists():
        print(f"ERROR: .env.example not found: {args.env}", file=sys.stderr)
        return 1

    fields = extract_settings_fields(args.config)
    env_vars = extract_env_example_vars(args.env)

    missing: list[str] = []
    covered: list[str] = []

    for field in fields:
        env_var = field_to_env_var(field)

        if field in NESTED_MODELS:
            # Nested model: require at least one sub-field entry (PREFIX__SUB)
            if nested_section_covered(field, env_vars):
                covered.append(f"{field} (nested, prefix {env_var}__)")
            else:
                missing.append(f"{env_var}__* (nested model section missing)")
        else:
            # Flat field: the var name must appear directly
            if env_var in env_vars:
                covered.append(field)
            else:
                missing.append(env_var)

    if args.verbose:
        print(f"Covered ({len(covered)}):")
        for f in covered:
            print(f"  OK  {f}")
        print()

    if missing:
        print(f"FAIL: {len(missing)} field(s) missing from {args.env}:")
        for m in missing:
            print(f"  MISSING  {m}")
        print()
        print("Add the missing variable(s) to .env.example (commented-out is fine).")
        print("See the story STORY-140 for formatting guidelines.")
        return 1

    print(f"OK: all {len(covered)} Settings fields are documented in {args.env}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
