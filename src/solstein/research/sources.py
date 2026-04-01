"""URL canonicalization and detection utilities.

STORY-247: Core logic moved to solstein.shared.canonicalize.
Re-exported here for backward compatibility.
"""

from solstein.shared.canonicalize import canonicalize_url, is_probably_url  # noqa: F401
