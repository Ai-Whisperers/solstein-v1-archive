#!/usr/bin/env bash
# OpenCode MCP Doctor v2.0
# Compatible with OpenCode v1.0+
# https://docs.opencode.ai/mcp/troubleshooting

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_FILE="$ROOT_DIR/.mcp.json"
OPENCONFIG_FILE="$ROOT_DIR/opencode.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ok() {
  printf "${GREEN}[OK]${NC} %s\n" "$1"
}

warn() {
  printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

err() {
  printf "${RED}[ERR]${NC} %s\n" "$1"
}

info() {
  printf "${BLUE}[INFO]${NC} %s\n" "$1"
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

check_opencode_version() {
  info "Checking OpenCode version..."
  
  if command -v opencode >/dev/null 2>&1; then
    local version
    version=$(opencode --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
    
    # Check minimum version for security (CVE-2026-22812)
    if [[ "$version" != "unknown" ]]; then
      local major minor patch
      IFS='.' read -r major minor patch <<< "$version"
      
      if [[ $major -gt 1 ]] || [[ $major -eq 1 && $minor -gt 0 ]] || [[ $major -eq 1 && $minor -eq 0 && $patch -ge 216 ]]; then
        ok "OpenCode version $version (>= 1.0.216 ✓ - CVE-2026-22812 fixed)"
      else
        err "OpenCode version $version (⚠️  Update to 1.0.216+ required for security)"
        return 1
      fi
    else
      warn "Could not determine OpenCode version"
    fi
  else
    warn "OpenCode CLI not found in PATH"
    return 1
  fi
}

check_mcp_config() {
  info "Checking MCP configuration..."
  
  if [ -f "$MCP_FILE" ]; then
    ok "Found MCP config: $MCP_FILE"
    
    # Validate JSON syntax
    if python3 -c "import json; json.load(open('$MCP_FILE'))" 2>/dev/null; then
      ok "MCP config is valid JSON"
    else
      err "MCP config is invalid JSON"
      return 1
    fi
    
    # Check for version field (OpenCode v1.0+)
    if python3 -c "import json; data=json.load(open('$MCP_FILE')); exit(0 if 'version' in data else 1)" 2>/dev/null; then
      ok "MCP config has version field (v2.0 format)"
    else
      warn "MCP config missing version field (consider upgrading to v2.0 format)"
    fi
    
    # Check for permissions (OpenCode v1.0+)
    if python3 -c "import json; data=json.load(open('$MCP_FILE')); exit(0 if 'permissions' in data else 1)" 2>/dev/null; then
      ok "MCP config has granular permissions (v1.0+ feature)"
    else
      warn "MCP config missing granular permissions (consider upgrading to v1.0+ format)"
    fi
  else
    err "Missing MCP config: $MCP_FILE"
    return 1
  fi
}

check_opencode_config() {
  info "Checking OpenCode configuration..."
  
  if [ -f "$OPENCONFIG_FILE" ]; then
    ok "Found opencode.yml: $OPENCONFIG_FILE"
    
    # Validate YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('$OPENCONFIG_FILE'))" 2>/dev/null; then
      ok "opencode.yml is valid YAML"
    else
      warn "Could not validate opencode.yml (PyYAML may not be installed)"
    fi
  else
    warn "Missing opencode.yml (recommended for v1.0+)"
  fi
  
  if [ -d "$ROOT_DIR/.opencode" ]; then
    ok "Found .opencode/ directory"
    
    if [ -f "$ROOT_DIR/.opencode/settings.json" ]; then
      ok "Found team settings: .opencode/settings.json"
    else
      warn "Missing .opencode/settings.json"
    fi
  else
    warn "Missing .opencode/ directory (optional but recommended)"
  fi
}

main() {
  local failures=0

  printf '╔═══════════════════════════════════════════════════════════╗\n'
  printf '║           OpenCode MCP Doctor v2.0                        ║\n'
  printf '║           Compatible with OpenCode v1.0+                  ║\n'
  printf '╚═══════════════════════════════════════════════════════════╝\n'
  printf 'Repo: %s\n\n' "$ROOT_DIR"

  # Check required commands
  info "Checking system dependencies..."
  require_cmd node || failures=$((failures + 1))
  require_cmd npm || failures=$((failures + 1))
  require_cmd npx || failures=$((failures + 1))
  require_cmd python3 || failures=$((failures + 1))
  
  # Check OpenCode version (important for security)
  check_opencode_version || failures=$((failures + 1))
  
  printf '\n'
  
  # Check configuration files
  check_mcp_config || failures=$((failures + 1))
  check_opencode_config || failures=$((failures + 1))
  
  printf '\n'
  
  # Check MCP packages
  info "Checking MCP server packages..."
  check_npm_pkg "@modelcontextprotocol/server-filesystem" || failures=$((failures + 1))
  check_npm_pkg "@modelcontextprotocol/server-sequential-thinking" || failures=$((failures + 1))

  printf '\n'
  info "Checking optional packages..."
  check_npm_pkg "@modelcontextprotocol/server-memory" || true
  check_npm_pkg "@playwright/mcp" || true
  check_npm_pkg "github-mcp-server" || true

  printf '\n'
  
  if [ "$failures" -eq 0 ]; then
    printf '╔═══════════════════════════════════════════════════════════╗\n'
    printf '║  ✓ MCP tooling baseline looks healthy                     ║\n'
    printf '╚═══════════════════════════════════════════════════════════╝\n'
    printf '\nNext steps:\n'
    printf '  1. Ensure OpenCode v1.0.216+ is installed\n'
    printf '  2. Run: ./scripts/opencode-mcp-smoke-test.sh\n'
    printf '  3. Start coding with: opencode\n'
    exit 0
  fi

  err "Found $failures issue(s). Fix them, then run this script again."
  exit 1
}

main "$@"
