# FD-040: Rewrite Financial Dashboard Scripts to C#

**Part of**: [FINANCIALDASHBOARD](../plan.md) -- Phase 6 (C# Migration)

## Objective

Rewrite the Python-based competitive financial dashboard scripts (`extract_competitor_data.py`, `generate_excel_report.py`, `competitor_utils.py`) to C# as a .NET library/application. This brings the dashboard tooling into the main .NET ecosystem, enabling tighter integration with eBase, better type safety, and long-term maintainability by the core development team.

## Background

The current dashboard is built with three Python scripts using `openpyxl` for Excel generation. Phase 1 is complete (8 sheets, charts, styling, sparklines). The Python scripts work but are isolated from the main .NET codebase. Migrating to C# enables:

- Integration with the eBase .NET ecosystem
- Shared data models and services
- Type safety and compile-time checks
- NuGet dependency management
- Unit testing with xUnit/NUnit
- Serving as the data layer for the future Web Interface (FD-041)

## Requirements

- Rewrite `extract_competitor_data.py` to C# -- data extraction from competitor JSON/markdown files
- Rewrite `generate_excel_report.py` to C# -- Excel workbook generation with all Phase 1 sheets, charts, styling
- Rewrite `competitor_utils.py` to C# -- shared utility functions, classification logic, formatting helpers
- Use ClosedXML (or EPPlus) for Excel generation
- Produce identical Excel output to the Python version (sheet-for-sheet, chart-for-chart)
- Maintain all existing features: executive summary, charts, sparklines, conditional formatting, print layout
- Support CLI execution (dotnet run / compiled exe) with same --help interface
- Structured logging (Serilog or Microsoft.Extensions.Logging)
- Configuration via appsettings.json for file paths, thresholds, styling parameters

## Acceptance Criteria

- [ ] C# solution compiles with zero warnings (`dotnet build /warnaserror`)
- [ ] CLI produces Excel workbook matching Python output (same sheets, same data, same charts)
- [ ] All Phase 1 features preserved: Executive Summary, Charts, Sparklines, Styling, Methodology
- [ ] Unit tests with 60%+ code coverage (xUnit)
- [ ] ClosedXML (or EPPlus) used for Excel generation
- [ ] Structured logging with configurable log levels
- [ ] Configuration externalized to appsettings.json
- [ ] Solution follows clean architecture (separation of data extraction, report generation, utilities)
- [ ] XML documentation on all public types and methods
- [ ] No hardcoded file paths -- all paths configurable

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Full rewrite of 3 Python scripts to C# with Excel library migration, requiring architecture decisions, library evaluation, and feature parity verification across all sheets and charts.

**Criteria Met**:
- Root Cause: N/A (new implementation, not a fix)
- Files Affected: 10+ new C# files (models, services, CLI entry point, tests)
- Lines Changed: 2000+ lines of new C# code
- Risk Level: Medium (must achieve feature parity with working Python)
- Solution Pattern: Known (.NET console app with Excel library)

**Effort**: 5-8 days
**Risk**: Medium -- Excel library differences may require workarounds for sparklines, conditional formatting, chart types

## Implementation Strategy

### Phase A: Foundation (1-2 days)
1. Create .NET solution structure (Console App + Class Library + Test Project)
2. Add NuGet dependencies (ClosedXML, Serilog, System.CommandLine)
3. Define data models (Competitor, FinancialMetrics, Classification, etc.)
4. Implement configuration loading from appsettings.json

### Phase B: Data Extraction (1-2 days)
5. Port `extract_competitor_data.py` logic to C# `CompetitorDataExtractor` service
6. JSON/markdown file parsing with System.Text.Json
7. Data validation and null-safety handling
8. Unit tests for extraction logic

### Phase C: Report Generation (2-3 days)
9. Port `generate_excel_report.py` to C# `ExcelReportGenerator` service
10. Implement each sheet writer (Executive Summary, Revenue, Funding, Employee, SaaS, etc.)
11. Chart generation using ClosedXML charting API
12. Conditional formatting, styling, print layout
13. Sparklines (evaluate ClosedXML support, fallback to text sparklines if needed)

### Phase D: Integration & Validation (1 day)
14. CLI entry point with System.CommandLine (--input, --output, --help)
15. End-to-end test: generate Excel from same input data as Python
16. Visual comparison of Python vs C# Excel output
17. Performance comparison

## Testing Strategy

- **Unit tests**: xUnit with FluentAssertions, 60%+ coverage
- **Integration tests**: End-to-end Excel generation from test data
- **Comparison tests**: Automated sheet/cell comparison between Python and C# output
- **Manual validation**: Visual inspection of charts, styling, print layout

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ClosedXML lacks sparkline support | Charts degraded | Use text-based sparklines (same fallback as Python) |
| Chart API differences between openpyxl and ClosedXML | Visual mismatch | Accept minor visual differences; match data accuracy |
| Configuration/path handling differences Win/Linux | Portability issues | Use Path.Combine, configurable base paths |
| Scope creep into Phase 3 features | Delays | Strict Phase 1 feature parity only |

## Questions

- [ ] Preferred Excel library: ClosedXML (MIT, free) vs EPPlus (commercial license for v5+)?
- [ ] Target .NET version: .NET 8 LTS or .NET 9?
- [ ] Should this be a standalone console app or a class library callable from eBase?
- [ ] Naming convention: `Eneve.CompetitiveIntelligence.Dashboard` or simpler?

## Status

Planning
