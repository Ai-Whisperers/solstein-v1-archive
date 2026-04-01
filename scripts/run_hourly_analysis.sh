#!/bin/bash
# Solstein Hourly Codebase Analysis Runner
# This script runs the comprehensive codebase analysis every hour

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
OUTPUT_DIR="$REPO_DIR/.analysis-output"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

echo "[$TIMESTAMP] Starting Solstein codebase analysis..."

# Create timestamped output directory
mkdir -p "$OUTPUT_DIR/runs/$TIMESTAMP"

# Run Claude Code analysis
cd "$REPO_DIR"
claude -p "
You are a senior software architect performing a comprehensive codebase analysis on the Solstein project.

YOUR TASK:
Perform a deep, critical analysis of this Python codebase (src/solstein/) to identify:

1. CODE QUALITY ISSUES:
   - Anti-patterns (god objects, tight coupling, circular deps, etc.)
   - Code smells (long functions, deep nesting, primitive obsession)
   - Architecture violations (layer bleeding, mixed concerns)
   - Testing gaps (missing tests, untestable code)

2. DESIGN PATTERNS MISSING:
   - Where factories/abstract factories would help
   - Repository pattern gaps
   - Strategy/Command/Observer opportunities
   - Dependency injection needs

3. MODULARIZATION OPPORTUNITIES:
   - Files that should be split
   - Modules with mixed responsibilities
   - Common functionality that should be centralized
   - Interfaces that should be extracted

4. PERFORMANCE & SCALABILITY:
   - Blocking I/O in async contexts
   - N+1 query problems
   - Memory leaks or high memory usage
   - Missing caching opportunities

5. SECURITY ISSUES:
   - Input validation gaps
   - Authentication/authorization weaknesses
   - Secret handling issues
   - Injection vulnerabilities

DELIVERABLES:
Create markdown files in .analysis-output/runs/$TIMESTAMP/:

1. COMPREHENSIVE_CODEBASE_ANALYSIS.md
   - Executive summary of findings
   - Detailed analysis by category
   - Prioritized recommendations

2. ANTIPATTERNS_CATALOG.md
   - Catalog of all anti-patterns found
   - File locations and severity
   - Refactoring suggestions

3. EPIC_*.md files (create 3-5 new EPICs)
   - Follow the existing EPIC format
   - Include stories with acceptance criteria
   - Estimate story points

4. STORY_*.md files (create 10-15 stories)
   - Atomic, actionable stories
   - Link to parent EPICs
   - Clear acceptance criteria

Focus on changes since last analysis. Be brutally honest.
Output summary when finished.
" > "$OUTPUT_DIR/runs/$TIMESTAMP/analysis.log" 2>&1

echo "[$TIMESTAMP] Analysis complete. Results in: $OUTPUT_DIR/runs/$TIMESTAMP/"

# Optional: Send notification
# openclaw system event --text "Solstein analysis complete: $TIMESTAMP" --mode now
