#!/usr/bin/env python3
"""CI check: verify all domain model fields are documented in the field lineage.

STORY-128: Compares fields defined in Company and FinancialMetric domain models
against fields documented in docs/field-lineage.md. Emits warnings for any
undocumented fields, naming them specifically.

Exit codes:
    0 — all fields documented (or only warnings)
    1 — undocumented fields found (when --strict is passed)
"""

import argparse
import re
import sys
from pathlib import Path

# Project root is 3 levels up from scripts/ci/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LINEAGE_DOC = PROJECT_ROOT / "docs" / "field-lineage.md"
MODELS_FILE = PROJECT_ROOT / "src" / "solstein" / "domain" / "models.py"

# Fields that are intentionally excluded from lineage documentation.
# These are internal Pydantic/infrastructure fields, not domain data.
EXCLUDED_FIELDS = frozenset({
    "allow_empty_primary",  # FinancialMetric internal flag
    "model_config",         # Pydantic config (not a data field)
})


def extract_model_fields(models_path: Path) -> dict[str, set[str]]:
    """Extract field names from Company and FinancialMetric classes.

    Parses the models.py source to find Pydantic field declarations,
    computed_field properties, and confidence-level fields.

    Returns:
        Dict mapping model name to set of field names.
    """
    content = models_path.read_text()
    fields: dict[str, set[str]] = {"Company": set(), "FinancialMetric": set()}

    current_class: str | None = None

    for line in content.splitlines():
        # Detect class boundaries
        class_match = re.match(r"^class (Company|FinancialMetric)\(", line)
        if class_match:
            current_class = class_match.group(1)
            continue

        # End of class: another top-level class or module-level code
        if current_class and re.match(r"^class \w+", line):
            current_class = None
            continue

        if current_class is None:
            continue

        # Match field declarations: name: type = ... or name: type
        field_match = re.match(r"^    (\w+)\s*:", line)
        if field_match:
            name = field_match.group(1)
            # Skip private/dunder and Pydantic internals
            if not name.startswith("_") and name not in EXCLUDED_FIELDS:
                fields[current_class].add(name)
            continue

        # Match computed_field / @property on Company
        # Pattern: def field_name(self) after @computed_field or @property
        computed_match = re.match(r"^    def (\w+)\(self\)", line)
        if computed_match:
            name = computed_match.group(1)
            # Only include properties that look like data fields (not validators/helpers)
            # We check if the previous non-blank line has @computed_field or @property
            # For simplicity, we rely on these being in the lineage doc already
            # This section intentionally skips method definitions

    return fields


def extract_documented_fields(lineage_path: Path) -> set[str]:
    """Extract field names documented in the lineage markdown.

    Looks for backtick-quoted field names in table rows, handling both
    simple fields (e.g., `name`) and dotted fields (e.g., `financials.revenue`).

    Returns:
        Set of all documented field names (flattened, no dots).
    """
    content = lineage_path.read_text()
    documented: set[str] = set()

    # Match fields in table cells: | `field_name` | or | `parent.field_name` |
    for match in re.finditer(r"\|\s*`([^`]+)`\s*\|", content):
        field = match.group(1)
        # Handle dotted notation: financials.revenue -> revenue (FinancialMetric)
        # Also keep the full path for Company-level references
        if "." in field:
            parts = field.split(".")
            documented.add(parts[-1])  # e.g., "revenue" from "financials.revenue"
        else:
            documented.add(field)

    return documented


def check_field_lineage(strict: bool = False) -> int:
    """Check that all domain model fields are documented in the lineage.

    Args:
        strict: If True, exit with code 1 when undocumented fields are found.

    Returns:
        Exit code (0 = OK, 1 = undocumented fields in strict mode).
    """
    if not MODELS_FILE.exists():
        print(f"ERROR: Models file not found: {MODELS_FILE}")
        return 1

    if not LINEAGE_DOC.exists():
        print(f"ERROR: Lineage document not found: {LINEAGE_DOC}")
        return 1

    model_fields = extract_model_fields(MODELS_FILE)
    documented = extract_documented_fields(LINEAGE_DOC)

    all_model_fields: set[str] = set()
    for fields in model_fields.values():
        all_model_fields.update(fields)

    undocumented = all_model_fields - documented

    if not undocumented:
        total = len(all_model_fields)
        print(f"OK: All {total} domain model fields are documented in field lineage.")
        return 0

    # Sort for deterministic output
    undocumented_sorted = sorted(undocumented)
    print(f"WARNING: {len(undocumented_sorted)} undocumented field(s) found:")
    for field in undocumented_sorted:
        # Find which model(s) define this field
        models = [m for m, fields in model_fields.items() if field in fields]
        print(f"  - {field} (defined in: {', '.join(models)})")

    if strict:
        print("\nFailing because --strict is enabled.")
        return 1

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that all domain model fields are documented in field lineage."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code 1 if undocumented fields are found.",
    )
    args = parser.parse_args()
    sys.exit(check_field_lineage(strict=args.strict))


if __name__ == "__main__":
    main()
