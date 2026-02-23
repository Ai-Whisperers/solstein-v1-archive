#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ok() {
  printf '[OK] %s\n' "$1"
}

err() {
  printf '[ERR] %s\n' "$1"
}

run_smoke() {
  local name="$1"
  local cmd="$2"
  local logfile="/tmp/opencode-mcp-smoke-${name}.log"
  local rc=0

  timeout 6s bash -c "tail -f /dev/null | ${cmd}" >"$logfile" 2>&1 || rc=$?

  if [ "$rc" -eq 0 ]; then
    err "${name}: server exited early (expected to keep running)"
    return 1
  fi

  if [ "$rc" -eq 124 ]; then
    ok "${name}: server stayed active on stdio (timeout expected)"
    return 0
  fi

  err "${name}: unexpected exit code ${rc}; see ${logfile}"
  return 1
}

main() {
  local failures=0

  printf 'OpenCode MCP Smoke Test\n'
  printf 'Repo: %s\n\n' "$ROOT_DIR"

  run_smoke "filesystem" "npx -y @modelcontextprotocol/server-filesystem ." || failures=$((failures + 1))
  run_smoke "sequential-thinking" "npx -y @modelcontextprotocol/server-sequential-thinking" || failures=$((failures + 1))

  printf '\nOptional extras smoke tests:\n'
  run_smoke "memory" "npx -y @modelcontextprotocol/server-memory" || failures=$((failures + 1))
  run_smoke "playwright" "npx -y @playwright/mcp" || failures=$((failures + 1))
  run_smoke "github" "npx -y --package=github-mcp-server github-mcp-server-mcp" || failures=$((failures + 1))

  printf '\n'
  if [ "$failures" -eq 0 ]; then
    ok "All MCP servers are runnable and remain active over stdio."
    exit 0
  fi

  err "${failures} MCP smoke test(s) failed."
  exit 1
}

main "$@"
