#!/usr/bin/env bash
# OpenCode MCP Smoke Test v2.0
# Compatible with OpenCode v1.0+
# https://docs.opencode.ai/mcp/troubleshooting

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ok() {
  printf "${GREEN}[OK]${NC} %s\n" "$1"
}

err() {
  printf "${RED}[ERR]${NC} %s\n" "$1"
}

warn() {
  printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

info() {
  printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

run_smoke() {
  local name="$1"
  local cmd="$2"
  local logfile="/tmp/opencode-mcp-smoke-${name}.log"
  local rc=0

  info "Testing $name MCP server..."
  
  # Run with timeout - expect it to stay running (timeout = success)
  timeout 6s bash -c "tail -f /dev/null | ${cmd}" >"$logfile" 2>&1 || rc=$?

  if [ "$rc" -eq 0 ]; then
    err "${name}: server exited early (expected to keep running)"
    if [ -f "$logfile" ]; then
      err "  See log: $logfile"
    fi
    return 1
  fi

  if [ "$rc" -eq 124 ]; then
    ok "${name}: server stayed active on stdio (timeout expected ✓)"
    rm -f "$logfile"
    return 0
  fi

  err "${name}: unexpected exit code ${rc}"
  if [ -f "$logfile" ]; then
    err "  See log: $logfile"
    tail -n 5 "$logfile" | sed 's/^/    /'
  fi
  return 1
}

run_quick_test() {
  local name="$1"
  local test_cmd="$2"
  local logfile="/tmp/opencode-mcp-smoke-${name}.log"
  local rc=0

  info "Quick test for $name..."
  
  eval "$test_cmd" >"$logfile" 2>&1 || rc=$?

  if [ "$rc" -eq 0 ]; then
    ok "${name}: quick test passed ✓"
    rm -f "$logfile"
    return 0
  else
    warn "${name}: quick test failed (may still work in OpenCode)"
    rm -f "$logfile"
    return 0  # Don't fail on quick test
  fi
}

main() {
  local failures=0

  printf '╔═══════════════════════════════════════════════════════════╗\n'
  printf '║           OpenCode MCP Smoke Test v2.0                    ║\n'
  printf '║           Compatible with OpenCode v1.0+                  ║\n'
  printf '╚═══════════════════════════════════════════════════════════╝\n'
  printf 'Repo: %s\n\n' "$ROOT_DIR"

  # Required MCP servers
  info "Testing REQUIRED MCP servers..."
  printf '\n'
  
  run_smoke "filesystem" "npx -y @modelcontextprotocol/server-filesystem ." || failures=$((failures + 1))
  run_smoke "sequential-thinking" "npx -y @modelcontextprotocol/server-sequential-thinking" || failures=$((failures + 1))

  printf '\n'
  info "Testing OPTIONAL MCP servers..."
  printf '\n'
  
  # Optional MCP servers - don't fail if they don't work
  run_smoke "memory" "npx -y @modelcontextprotocol/server-memory" || warn "memory server failed (optional)"
  run_smoke "playwright" "npx -y @playwright/mcp" || warn "playwright server failed (optional)"
  run_smoke "github" "npx -y --package=github-mcp-server github-mcp-server-mcp" || warn "github server failed (optional)"

  printf '\n'
  
  if [ "$failures" -eq 0 ]; then
    printf '╔═══════════════════════════════════════════════════════════╗\n'
    printf '║  ✓ All required MCP servers are runnable!                 ║\n'
    printf '╚═══════════════════════════════════════════════════════════╝\n'
    printf '\nOpenCode v1.0+ Integration Ready!\n'
    printf '\nQuick Start:\n'
    printf '  opencode                    # Start OpenCode CLI\n'
    printf '  opencode --version          # Check version\n'
    printf '  opencode provider list      # See available providers\n'
    printf '\nFor help: https://docs.opencode.ai\n'
    exit 0
  fi

  err "${failures} required MCP smoke test(s) failed."
  printf '\nTroubleshooting:\n'
  printf '  1. Ensure Node.js 18+ is installed\n'
  printf '  2. Run: npm install -g npx\n'
  printf '  3. Check network connectivity for npm packages\n'
  printf '  4. Run: ./scripts/opencode-mcp-doctor.sh for detailed diagnostics\n'
  exit 1
}

main "$@"
