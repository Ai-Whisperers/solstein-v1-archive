#!/usr/bin/env bash
# Smoke test suite for post-deploy verification.
#
# Runs minimal HTTP checks against a deployed Solstein API to verify
# the deployment is healthy. Designed to complete in <30 seconds.
#
# Usage:
#   ./scripts/ci/smoke_test.sh <BASE_URL>
#   ./scripts/ci/smoke_test.sh https://staging.solstein.app
#
# Exit codes:
#   0 — all smoke tests passed
#   1 — one or more smoke tests failed

set -euo pipefail

BASE_URL="${1:?Usage: smoke_test.sh <BASE_URL>}"
PASS=0
FAIL=0
TOTAL=0

check() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    TOTAL=$((TOTAL + 1))

    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

    if [ "$status" = "$expected_status" ]; then
        echo "  PASS  $name (HTTP $status)"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $name (expected HTTP $expected_status, got $status)"
        FAIL=$((FAIL + 1))
    fi
}

check_json() {
    local name="$1"
    local url="$2"
    TOTAL=$((TOTAL + 1))

    local response
    response=$(curl -s --max-time 10 "$url" 2>/dev/null || echo "")

    if [ -z "$response" ]; then
        echo "  FAIL  $name (empty response)"
        FAIL=$((FAIL + 1))
        return
    fi

    # Verify it's valid JSON
    if echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        echo "  PASS  $name (valid JSON)"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $name (invalid JSON response)"
        FAIL=$((FAIL + 1))
    fi
}

echo "Smoke Test Suite"
echo "================"
echo "Target: $BASE_URL"
echo ""

# 1. Health endpoint
echo "--- Health ---"
check "GET /health" "$BASE_URL/health"

# 2. API health (may include DB connectivity check)
check "GET /api/v1/health" "$BASE_URL/api/v1/health"

# 3. Companies endpoint returns valid JSON
echo "--- API ---"
check "GET /api/v1/companies" "$BASE_URL/api/v1/companies"
check_json "GET /api/v1/companies (JSON)" "$BASE_URL/api/v1/companies"

# 4. OpenAPI docs accessible
check "GET /docs" "$BASE_URL/docs"

echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"

if [ "$FAIL" -gt 0 ]; then
    echo "SMOKE TESTS FAILED"
    exit 1
fi

echo "ALL SMOKE TESTS PASSED"
exit 0
