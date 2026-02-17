# FD-040: Tracker

## Phase A: Foundation (1-2 days)

- [ ] Create .NET solution structure (Console App + Class Library + Test Project)
- [ ] Add NuGet dependencies (ClosedXML, Serilog, System.CommandLine)
- [ ] Define data models (Competitor, FinancialMetrics, Classification enums)
- [ ] Implement configuration loading (appsettings.json)
- [ ] Set up structured logging

## Phase B: Data Extraction (1-2 days)

- [ ] Port file discovery and path resolution logic
- [ ] Port JSON/markdown competitor data parsing
- [ ] Port financial metrics extraction (revenue, funding, employees, CAGR)
- [ ] Port classification logic (Rocket/Established/Dinosaur)
- [ ] Port utility functions (formatting, calculations)
- [ ] Unit tests for data extraction

## Phase C: Report Generation (2-3 days)

- [ ] Port Executive Summary sheet writer
- [ ] Port Revenue Leaderboard sheet writer
- [ ] Port Funding Leaderboard sheet writer
- [ ] Port Employee Growth sheet writer
- [ ] Port SaaS Maturity sheet writer
- [ ] Port Classification Matrix sheet writer
- [ ] Port Efficiency & Profitability sheet writer
- [ ] Port Market Reach sheet writer
- [ ] Port Eneve vs Market sheet writer
- [ ] Port Methodology sheet writer
- [ ] Port Raw Data sheet writer
- [ ] Implement chart generation (bar charts, doughnut chart)
- [ ] Implement conditional formatting and styling
- [ ] Implement print layout and confidential footer
- [ ] Implement sparklines (or text fallback)
- [ ] Unit tests for report generation

## Phase D: Integration & Validation (1 day)

- [ ] CLI entry point with --input, --output, --help, --verbose
- [ ] End-to-end test: generate workbook from test data
- [ ] Visual comparison: Python output vs C# output
- [ ] Performance comparison
- [ ] XML documentation on all public types
- [ ] Final validation: zero warnings build
