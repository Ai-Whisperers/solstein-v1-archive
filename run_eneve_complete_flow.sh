#!/bin/bash
# Solstein Complete Flow Runner for Client: Eneve
# With comprehensive logging and debugging

set -e

echo "🚀 Starting Solstein Complete Flow for Client: ENEVE"
echo "======================================================"

# Create log directory
mkdir -p data/output/logs
mkdir -p data/output/exports
mkdir -p data/output/debug

# Set environment
export PYTHONPATH=/home/ai-whisperers/solstein/src:$PYTHONPATH
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG

echo ""
echo "📊 Step 1: Extract Data from Eneve Markdown"
echo "---------------------------------------------"
source .venv/bin/activate
python -m solstein.cli extract \
    data/input/custom_market_runs/2026-02-23/dutch_market \
    --output data/output/exports/eneve_extracted.json \
    --pattern "*.md" \
    --verbose

echo ""
echo "🎯 Step 2: Score Eneve Company"
echo "------------------------------"
python -m solstein.cli score \
    data/output/exports/eneve_extracted.json \
    --output data/output/exports/eneve_scored.json \
    --verbose

echo ""
echo "📈 Step 3: Analyze Market (Dutch Energy Software)"
echo "--------------------------------------------------"
python -m solstein.cli analyze-market \
    data/output/exports/eneve_scored.json \
    --output data/output/exports/eneve_market_analysis.json \
    --verbose

echo ""
echo "📊 Step 4: Export to Excel Dashboard"
echo "-------------------------------------"
python -m solstein.cli export-excel \
    data/output/exports/eneve_scored.json \
    data/output/exports/eneve_dashboard.xlsx \
    --verbose

echo ""
echo "📝 Step 5: Generate Intelligence Report for Eneve"
echo "--------------------------------------------------"
python -m solstein.cli generate-report \
    "eneve" \
    --input-dir data/input/custom_market_runs/2026-02-23/dutch_market \
    --output data/output/exports/eneve_report.md \
    --verbose

echo ""
echo "✅ Complete Flow Finished for Client: ENEVE"
echo "============================================"
echo ""
echo "📁 Output Files:"
echo "  • Extracted Data: data/output/exports/eneve_extracted.json"
echo "  • Scored Data:    data/output/exports/eneve_scored.json"
echo "  • Market Analysis: data/output/exports/eneve_market_analysis.json"
echo "  • Excel Dashboard: data/output/exports/eneve_dashboard.xlsx"
echo "  • Intelligence Report: data/output/exports/eneve_report.md"
echo ""
