#!/usr/bin/env bash
# Install Solstein systemd service by generating concrete files from templates.
#
# Usage:
#   ./scripts/install-service.sh [--prefix /path/to/project]
#
# Environment variables:
#   PROJECT_ROOT      - Override the detected project root
#   PYTHON_EXECUTABLE - Override the detected Python interpreter (default: python3)
#   SYSTEMD_DIR       - Override the systemd unit destination (default: ~/.config/systemd/user)

set -euo pipefail

# Resolve project root from script location if not provided
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE:-$(command -v python3 || echo python3)}"
SYSTEMD_DIR="${SYSTEMD_DIR:-$HOME/.config/systemd/user}"

echo "Installing Solstein service"
echo "  PROJECT_ROOT      = $PROJECT_ROOT"
echo "  PYTHON_EXECUTABLE = $PYTHON_EXECUTABLE"
echo "  SYSTEMD_DIR       = $SYSTEMD_DIR"

mkdir -p "$SYSTEMD_DIR"

for template in "$PROJECT_ROOT/bin/"*.service.template "$PROJECT_ROOT/bin/"*.timer.template; do
    [ -f "$template" ] || continue
    unit_name="$(basename "$template" .template)"
    dest="$SYSTEMD_DIR/$unit_name"

    sed \
        -e "s|\${PROJECT_ROOT}|$PROJECT_ROOT|g" \
        -e "s|\${PYTHON_EXECUTABLE}|$PYTHON_EXECUTABLE|g" \
        "$template" > "$dest"

    echo "  Generated: $dest"
done

if command -v systemctl &>/dev/null; then
    systemctl --user daemon-reload
    echo "Systemd user daemon reloaded."
    echo "Enable with: systemctl --user enable --now solstein-agents.timer"
fi
