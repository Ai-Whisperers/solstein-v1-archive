#!/bin/bash
# SolStein Platform Setup Script

echo "🚀 Setting up SolStein Competitive Intelligence Platform"

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo "Installing Python dependencies..."
cd SolStein/.cursor/scripts/analysis/market/
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest -v

# Extract sample data
echo "Extracting sample data..."
python extract_competitor_data.py --input ../../COMPETITION/ --output sample_data.json

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review business documentation: cat ../SOLSTEIN/README.md"
echo "2. Explore competitor data: jq '. | length' sample_data.json"
echo "3. Generate dashboard: python generate_excel_report.py --input sample_data.json --output test_dashboard.xlsx"