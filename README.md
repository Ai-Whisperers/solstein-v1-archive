# SolStein Competitive Intelligence Platform

**AI-Powered Competitive Intelligence for Venture Capital & Private Equity**

> *The Viking sunstone revealed the sun through clouds. Solstein reveals the competitive landscape through market fog.*

## 🚀 Overview

SolStein is an AI-powered competitive intelligence system that gives PE and VC firms a complete view of any market landscape -- in **days, not months**, at a **fraction of consulting costs**.

It replaces the traditional model of hiring McKinsey or BCG for a EUR 500K-1.5M engagement that delivers a static PDF three months later. SolStein delivers deeper, wider, refreshable intelligence on demand.

## 📊 What's Included

This repository contains the complete SolStein platform:

### 1. **Business Documentation** (`SolStein/SOLSTEIN/`)
- `README.md` - Product overview and value proposition
- `case-study.md` - Real engagement: 29 competitors in European energy software
- `modules.md` - 5-module intelligence pipeline
- `pricing.md` - Pricing tiers (€500K-5M engagements)
- `why-now.md` - Market timing and opportunity analysis

### 2. **Competitor Data** (`SolStein/COMPETITION/`)
- **29 companies** profiled across European energy software market
- **Structured JSON** (212KB) with consistent schema
- **Excel dashboards** with automated reporting
- **Market protocol mappings** for 15+ European countries
- **Competitive overlap analysis** with matrix visualization

### 3. **Automation Tools** (`SolStein/.cursor/`)
- **Python scripts** for data extraction and processing
- **AI prompt templates** for reproducible research
- **Example outputs** and research templates
- **Testing infrastructure** with pytest

### 4. **Development Tracking** (`SolStein/FINANCIALDASHBOARD/`)
- **42 feature tickets** with context/plan/progress
- **Completed features** (FD-001 to FD-009)
- **In-progress development** (FD-010 to FD-042)
- **Roadmap** for future enhancements

## 🔧 Technical Stack

- **Python 3.10+** - Data processing and automation
- **OpenPyXL** - Excel report generation
- **Rich** - Terminal output and progress bars
- **Pytest** - Comprehensive testing suite
- **Markdown/JSON** - Structured documentation and data

## 🏗️ Architecture

### Core Modules:
1. **Competitor Deep Analysis** - Structured profiles across 8 dimensions
2. **Financial Growth Scoring** - Growth Scorecards (1-10) with Rocket/Dinosaur classification
3. **Corporate Genealogy** - Full M&A family trees with diagrams
4. **Financial Dashboard** - Cross-competitor rankings, charts, leaderboards
5. **Market Protocol Mapping** - Protocol-to-company matrix revealing hidden competitors

### Automation Pipeline:
```bash
# Extract data from markdown files
python extract_competitor_data.py --input COMPETITION/ --output competitor_data.json

# Generate Excel dashboard
python generate_excel_report.py --input competitor_data.json --output dashboard.xlsx

# Generate markdown report
python generate_markdown_dashboard.py --input competitor_data.json --output dashboard.md
```

## 📈 Business Model

| Tier | Price | What You Get |
|------|-------|--------------|
| **Single Assessment** | EUR 500K-1M | Full landscape for 1 portfolio company, 30 competitors, delivered in 1-2 weeks |
| **Portfolio-Wide** | EUR 2-3M + 300K/yr | Up to 10 portfolio companies, quarterly refresh, vertical customization |
| **Enterprise License** | EUR 3-5M + 500K/yr | Unlimited companies, 3+ verticals, full architecture transfer + training |
| **SaaS (Future)** | EUR 100-200K/yr per firm | Self-service platform, target 100+ firms = EUR 10-100M ARR |

## 🎯 Use Cases

### For Private Equity:
- **Exit preparation** - Comprehensive competitive positioning
- **Due diligence** - Deep market analysis for acquisition targets
- **Portfolio optimization** - Cross-company benchmarking

### For Venture Capital:
- **Investment evaluation** - Market landscape for potential investments
- **Portfolio support** - Competitive intelligence for portfolio companies
- **Market timing** - Identifying emerging trends and opportunities

### For Corporate Strategy:
- **Competitive positioning** - Understanding market dynamics
- **M&A strategy** - Identifying acquisition targets
- **Product development** - Market gap analysis

## 🚀 Getting Started

### 1. Explore the Data
```bash
# View competitor data
cat SolStein/COMPETITION/competitor_data.json | jq '. | length'
# Output: 29 (number of companies analyzed)

# View financial dashboard
open SolStein/COMPETITION/financial-dashboard.xlsx
```

### 2. Run the Automation
```bash
cd SolStein/.cursor/scripts/analysis/market/

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Extract data
python extract_competitor_data.py --input ../../COMPETITION/ --output test.json
```

### 3. Review Business Case
```bash
# Read the product documentation
cat SolStein/SOLSTEIN/README.md
cat SolStein/SOLSTEIN/case-study.md
```

## 📋 Analysis Report

See [ANALYSIS.md](ANALYSIS.md) for comprehensive technical and business analysis including:
- Architecture review
- Code quality assessment
- Market opportunity analysis
- Recommendations for improvement

## 📄 License

This repository contains proprietary competitive intelligence tools and data. For licensing and commercial use, contact the AI Whisperers team.

## 🤝 Contributing

This is a proprietary platform. For internal development:
1. Create feature branches from `master`
2. Follow the FD-XXX ticket format for new features
3. Add tests for new functionality
4. Update documentation accordingly

## 📞 Contact

**AI Whisperers** - Building the future of AI-powered business intelligence.

---

*Confidential. For internal and investor discussions only.*
