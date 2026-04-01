#!/bin/bash
# Solstein Complete Flow Runner for Client: Eneve
# With comprehensive logging and debugging

set -e

echo "🚀 Starting Solstein Complete Flow for Client: ENEVE"
echo "======================================================"

# Parse arguments
FULL_DATASET=false
if [ "$1" == "--full" ] || [ "$1" == "-f" ]; then
    FULL_DATASET=true
    echo "Mode: FULL DATASET (199 companies)"
else
    echo "Mode: Dutch Market Only (4 companies)"
    echo "Use --full flag to run with all 199 companies"
fi
echo ""

# Create log directory
mkdir -p data/output/logs
mkdir -p data/output/exports
mkdir -p data/output/debug

# Set environment — derive PROJECT_ROOT from this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG

source .venv/bin/activate

if [ "$FULL_DATASET" = true ]; then
    echo "📊 Step 1: Load and Score All 199 Companies"
    echo "--------------------------------------------"
    python -c "
from solstein.data.loaders import CompetitorDataLoader
from solstein.analytics.scoring import GrowthScorer
import json

loader = CompetitorDataLoader()
companies = loader.load_companies()
print(f'📥 Loaded {len(companies)} companies from competitor_data.json')

scorer = GrowthScorer()
scored = [scorer.calculate_scores(c) for c in companies]
print(f'📈 Scored {len(scored)} companies')

output_path = 'data/output/exports/eneve_full_199_scored.json'
data = [c.model_dump(mode='json') for c in scored]
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2, default=str)
print(f'💾 Saved scored data to {output_path}')
"

    echo ""
    echo "📈 Step 2: Analyze Full Market"
    echo "-------------------------------"
    python -m solstein.cli analyze-market \
        data/output/exports/eneve_full_199_scored.json \
        --market-name "European Energy Software (Full)"

    echo ""
    echo "📊 Step 3: Export Full Market to Excel Dashboard"
    echo "-------------------------------------------------"
    python -m solstein.cli export-excel \
        data/output/exports/eneve_full_199_scored.json \
        data/output/exports/eneve_full_199_dashboard.xlsx

    echo ""
    echo "📝 Step 4: Generate Intelligence Report for Eneve"
    echo "--------------------------------------------------"
    python -m solstein.cli generate-report \
        "eneve" \
        --output data/output/exports/

    echo ""
    echo "✅ Complete Flow Finished (FULL DATASET) for Client: ENEVE"
    echo "==========================================================="
    echo ""
    echo "📁 Output Files:"
    echo "  • Scored Data (199): data/output/exports/eneve_full_199_scored.json"
    echo "  • Excel Dashboard:   data/output/exports/eneve_full_199_dashboard.xlsx (199 companies)"
    echo "  • Intelligence Report: data/output/exports/eneve-(formerly-energy21)/"

else
    echo "📊 Step 1: Extract Data from Dutch Market Markdown"
    echo "---------------------------------------------------"
    python -m solstein.cli extract \
        data/input/custom_market_runs/2026-02-23/dutch_market \
        --output data/output/exports/eneve_dutch_4_extracted.json \
        --pattern "*.md"

    echo ""
    echo "🎯 Step 2: Score Dutch Market Companies"
    echo "----------------------------------------"
    python -m solstein.cli score \
        data/output/exports/eneve_dutch_4_extracted.json \
        --output data/output/exports/eneve_dutch_4_scored.json

    echo ""
    echo "📈 Step 3: Analyze Dutch Market"
    echo "--------------------------------"
    python -m solstein.cli analyze-market \
        data/output/exports/eneve_dutch_4_scored.json \
        --market-name "Dutch Energy Software (4 companies)"

    echo ""
    echo "📊 Step 4: Export to Excel Dashboard"
    echo "-------------------------------------"
    python -m solstein.cli export-excel \
        data/output/exports/eneve_dutch_4_scored.json \
        data/output/exports/eneve_dutch_4_dashboard.xlsx

    echo ""
    echo "📝 Step 5: Generate Intelligence Report for Eneve"
    echo "--------------------------------------------------"
    python -m solstein.cli generate-report \
        "eneve" \
        --input data/output/exports/eneve_dutch_4_scored.json \
        --output data/output/exports/

    echo ""
    echo "✅ Complete Flow Finished (DUTCH MARKET) for Client: ENEVE"
    echo "=========================================================="
    echo ""
    echo "📁 Output Files:"
    echo "  • Extracted Data: data/output/exports/eneve_dutch_4_extracted.json"
    echo "  • Scored Data:    data/output/exports/eneve_dutch_4_scored.json"
    echo "  • Excel Dashboard: data/output/exports/eneve_dutch_4_dashboard.xlsx (4 companies)"
    echo "  • Intelligence Report: data/output/exports/eneve-(formerly-energy21)/"
    echo ""
    echo "💡 Tip: Use --full flag to run with all 199 companies:"
    echo "   ./run_eneve_complete_flow.sh --full"
fi

echo ""
