#!/usr/bin/env python3
"""Print safe rollback overrides for EPIC-017 feature flags.

This is read-only and does not mutate environment or files.
"""

from __future__ import annotations

from solstein.core.rollback_profile import default_safe_rollback_profile


def main() -> int:
    profile = default_safe_rollback_profile()
    print("== EPIC-017 Safe Rollback Overrides ==")
    for key, value in profile.as_env_overrides().items():
        print(f"export {key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
