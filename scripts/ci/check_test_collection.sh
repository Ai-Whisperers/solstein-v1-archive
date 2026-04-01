#!/usr/bin/env bash
# STORY-254: Verify pytest collection succeeds without manual DATABASE__URL injection.
# This script unsets all runtime env vars and runs --collect-only to confirm
# no module-level side effects break collection.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Test Collection Hermetic Check ==="
echo "Unsetting runtime env vars and running pytest --collect-only ..."

(
    unset DATABASE__URL 2>/dev/null || true
    unset SECURITY__SECRET_KEY 2>/dev/null || true
    unset GITHUB_TOKEN 2>/dev/null || true
    unset COMPANIES_HOUSE_API_KEY 2>/dev/null || true

    cd "$PROJECT_ROOT"
    PYTHONPATH=src python3 -m pytest tests/ --collect-only -q 2>&1
)

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "PASS: Test collection succeeded without runtime env vars."
else
    echo ""
    echo "FAIL: Test collection failed without runtime env vars (exit code $EXIT_CODE)."
    echo "This likely means a module-level import triggers config/database loading."
    echo "Fix: defer heavy imports into fixtures or wrap with try/except + pytest.skip."
    exit 1
fi
