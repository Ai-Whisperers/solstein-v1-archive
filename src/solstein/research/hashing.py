"""Canonical JSON serialization and hashing.

STORY-247: Core logic moved to solstein.shared.canonicalize.
Re-exported here for backward compatibility.
"""

from solstein.shared.canonicalize import (  # noqa: F401
    canonical_json_dumps,
    sha256_canonical_json,
)
