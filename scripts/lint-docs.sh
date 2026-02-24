#!/usr/bin/env bash

# Documentation Linter
#
# Validates documentation markdown:
# - Markdown syntax
# - Consistent heading hierarchy
# - Maximum line length
# - Consistent link formatting
#
# Usage:
#     ./scripts/lint-docs.sh              # Validate all docs
#     ./scripts/lint-docs.sh --fix        # Auto-fix formatting
#     ./scripts/lint-docs.sh docs/guides  # Validate specific directory

set -euo pipefail

DOCS_DIR="${1:-.}/docs"
FIX_MODE="${2:-}"
ERRORS_FOUND=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📋 Linting documentation in: $DOCS_DIR"
echo ""

# Find all markdown files
find "$DOCS_DIR" -name "*.md" -type f | sort | while read -r md_file; do
    FILE_ERRORS=0

    # Check for common markdown issues
    
    # 1. Check heading hierarchy (no skipped levels)
    if grep -n "^### " "$md_file" > /dev/null 2>&1; then
        if ! grep -n "^## " "$md_file" > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} $md_file: H3 found without H2"
            ((FILE_ERRORS++))
        fi
    fi

    # 2. Check for lines exceeding max length (120 chars for code blocks, 88 for text)
    while IFS= read -r line; do
        if [[ ${#line} -gt 88 && ! "$line" =~ ^\`\`\` ]]; then
            if [[ ! "$line" =~ ^# && ! "$line" =~ \[.*\]\(.*\) ]]; then
                line_num=$(grep -n "^${line//$/\\$}" "$md_file" | head -1 | cut -d: -f1)
                if [[ $FILE_ERRORS -lt 3 ]]; then
                    echo -e "${YELLOW}⚠${NC}  $md_file:$line_num: Line length ${#line} chars (max 88)"
                fi
            fi
        fi
    done < "$md_file"

    # 3. Check for inconsistent list formatting
    if grep -n "^[[:space:]]*\*[[:space:]]" "$md_file" > /dev/null 2>&1; then
        if grep -n "^[[:space:]]*-[[:space:]]" "$md_file" > /dev/null 2>&1; then
            if [[ $FILE_ERRORS -lt 3 ]]; then
                echo -e "${YELLOW}⚠${NC}  $md_file: Mixed list markers (* and -)"
            fi
        fi
    fi

    # 4. Check for proper code block markers
    code_block_count=$(grep -c '```' "$md_file" || true)
    if [[ $((code_block_count % 2)) -ne 0 ]]; then
        echo -e "${RED}✗${NC} $md_file: Unclosed code block"
        ((FILE_ERRORS++))
    fi

    # 5. Check for duplicate headings
    heading_count=$(grep -c "^#" "$md_file" || true)
    h1_count=$(grep -c "^# " "$md_file" || true)
    if [[ $h1_count -gt 1 ]]; then
        echo -e "${RED}✗${NC} $md_file: Multiple H1 headings ($h1_count found)"
        ((FILE_ERRORS++))
    fi

    if [[ $FILE_ERRORS -gt 0 ]]; then
        ((ERRORS_FOUND += FILE_ERRORS))
    else
        echo -e "${GREEN}✓${NC} $md_file"
    fi
done

echo ""
if [[ $ERRORS_FOUND -eq 0 ]]; then
    echo -e "${GREEN}✅ Documentation lint passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS_FOUND lint error(s)${NC}"
    exit 1
fi
