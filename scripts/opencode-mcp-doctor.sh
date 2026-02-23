#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_FILE="$ROOT_DIR/.mcp.json"

ok() {
  printf '[OK] %s\n' "$1"
}

warn() {
  printf '[WARN] %s\n' "$1"
}

err() {
  printf '[ERR] %s\n' "$1"
}

require_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "Found command: $cmd"
  else
    err "Missing command: $cmd"
    return 1
  fi
}

check_npm_pkg() {
  local pkg="$1"
  if npm view "$pkg" version >/dev/null 2>&1; then
    ok "Resolvable npm package: $pkg"
  else
    warn "Cannot resolve npm package: $pkg"
    return 1
  fi
}

main() {
  local failures=0

  printf 'OpenCode MCP Doctor\n'
  printf 'Repo: %s\n\n' "$ROOT_DIR"

  require_cmd node || failures=$((failures + 1))
  require_cmd npm || failures=$((failures + 1))
  require_cmd npx || failures=$((failures + 1))

  if [ -f "$MCP_FILE" ]; then
    ok "Found MCP config: $MCP_FILE"
  else
    err "Missing MCP config: $MCP_FILE"
    failures=$((failures + 1))
  fi

  check_npm_pkg "@modelcontextprotocol/server-filesystem" || failures=$((failures + 1))
  check_npm_pkg "@modelcontextprotocol/server-sequential-thinking" || failures=$((failures + 1))

  printf '\nOptional extras (non-blocking checks):\n'
  check_npm_pkg "@modelcontextprotocol/server-memory" || true
  check_npm_pkg "@playwright/mcp" || true
  check_npm_pkg "github-mcp-server" || true

  printf '\n'
  if [ "$failures" -eq 0 ]; then
    ok "MCP tooling baseline looks healthy."
    printf 'Next: configure your client to load %s\n' "$MCP_FILE"
    exit 0
  fi

  err "Found $failures issue(s). Fix them, then run this script again."
  exit 1
}

main "$@"
