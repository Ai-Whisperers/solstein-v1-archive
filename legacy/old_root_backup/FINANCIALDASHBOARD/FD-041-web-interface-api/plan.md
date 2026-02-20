# FD-041: Web Interface and API Service for Financial Dashboard

**Part of**: [FINANCIALDASHBOARD](../plan.md) -- Phase 7 (Web Interface & API)

## Objective

Build a web-based interactive dashboard and REST API service that serves the competitive financial intelligence data currently locked in Excel. This enables real-time access, interactive filtering, drill-down capabilities, and multi-user access without distributing Excel files -- transforming the static workbook into a living intelligence platform.

## Background

The financial dashboard currently exists as:
- Python scripts generating a static Excel workbook (Phase 1, complete)
- C# rewrite planned (FD-040, Phase 6)

A web interface unlocks:
- **Real-time updates**: Refresh data without regenerating Excel
- **Interactive exploration**: Filter by classification, geography, metric, time period
- **Multi-user access**: CTO, Board, analysts access simultaneously
- **Drill-down**: Click a competitor to see full profile, click a metric to see trend
- **Alerting**: Notify when competitor metrics cross thresholds
- **Export**: Generate Excel/PDF on demand from live data
- **Integration**: Embed in existing internal tools, link from JIRA/Confluence

## Requirements

### API Service
- RESTful API built with ASP.NET Core Web API
- Endpoints for: competitors, metrics, classifications, charts data, executive summary KPIs
- Filtering: by classification (Rocket/Established/Dinosaur), geography, revenue range, employee count
- Sorting and pagination for list endpoints
- Authentication and authorization (JWT or API key for internal use)
- Swagger/OpenAPI documentation auto-generated
- Health check endpoint for monitoring
- CORS configuration for frontend consumption
- Caching layer for expensive calculations (in-memory or Redis)

### Web Interface
- Modern SPA frontend (Blazor Server/WASM or React + TypeScript)
- Dashboard home page with executive summary KPIs (matching Excel Executive Summary sheet)
- Interactive charts (bar charts, scatter plots, heatmaps) using a charting library
- Competitor list with filtering, sorting, search
- Competitor detail page with full profile and metrics
- Classification matrix view (visual grid)
- Geographic view (map or matrix)
- Responsive design for desktop and tablet
- Dark/light theme support
- Export to Excel/PDF from any view

### Data Layer
- Reuse C# data models and extraction logic from FD-040
- Database storage (SQLite for dev, SQL Server for prod) or file-based with caching
- Data refresh mechanism (manual trigger or scheduled)
- Audit logging for data access

## Acceptance Criteria

- [ ] ASP.NET Core Web API running with Swagger UI at `/swagger`
- [ ] Minimum 8 API endpoints covering all major data areas
- [ ] API returns JSON matching the data from all Phase 1 Excel sheets
- [ ] Web frontend displays executive summary dashboard with KPIs
- [ ] Interactive charts render for Revenue, Funding, Employee, SaaS metrics
- [ ] Competitor list with filter/sort/search functional
- [ ] Competitor detail page shows full profile
- [ ] Classification matrix visualized interactively
- [ ] Authentication implemented (at minimum API key)
- [ ] Responsive on desktop and tablet viewports
- [ ] Excel export from dashboard produces workbook matching Phase 1 output
- [ ] Health check endpoint returns 200
- [ ] API response times < 200ms for list endpoints, < 500ms for aggregate calculations
- [ ] Unit tests with 60%+ coverage on API layer
- [ ] Integration tests for critical API endpoints
- [ ] Zero build warnings

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Full-stack application with API service, web frontend, data layer, authentication, and interactive visualizations. Multiple technology decisions, architectural patterns, and significant new code.

**Criteria Met**:
- Root Cause: N/A (new feature, not a fix)
- Files Affected: 30+ new files (API controllers, services, models, frontend components, tests)
- Lines Changed: 5000+ lines of new code
- Risk Level: Medium-High (full-stack, multiple integration points)
- Solution Pattern: Known (ASP.NET Core + SPA) but complex assembly

**Effort**: 10-15 days
**Risk**: Medium-High -- scope must be carefully managed to avoid feature creep

## Implementation Strategy

### Phase A: API Foundation (2-3 days)
1. Create ASP.NET Core Web API project within the solution from FD-040
2. Define API contracts (OpenAPI spec first)
3. Implement data access layer (reuse FD-040 models and extraction)
4. Implement core API endpoints: `/api/competitors`, `/api/metrics`, `/api/summary`
5. Add Swagger documentation
6. Add health check endpoint
7. Unit tests for controllers and services

### Phase B: API Enrichment (2-3 days)
8. Add filtering, sorting, pagination to list endpoints
9. Add chart-data endpoints (pre-aggregated data for frontend charts)
10. Add classification and geographic endpoints
11. Implement caching (IMemoryCache or IDistributedCache)
12. Add authentication (JWT bearer or API key middleware)
13. CORS configuration
14. Integration tests

### Phase C: Web Frontend Foundation (3-4 days)
15. Choose and set up frontend framework (Blazor WASM or React+TypeScript)
16. Implement layout: navigation, header, sidebar
17. Executive Summary dashboard page with KPI cards
18. Competitor list page with table, filters, search
19. Competitor detail page
20. Responsive CSS framework (Tailwind CSS or MudBlazor)

### Phase D: Charts & Visualizations (2-3 days)
21. Integrate charting library (Chart.js, ApexCharts, or Blazor equivalent)
22. Revenue bar chart
23. Funding bar chart
24. Employee growth chart
25. SaaS maturity chart
26. Classification matrix (interactive grid/heatmap)
27. Eneve vs Market comparison chart

### Phase E: Polish & Integration (1-2 days)
28. Excel export endpoint (reuse FD-040 report generator)
29. Dark/light theme toggle
30. Loading states, error handling, empty states
31. Performance optimization (lazy loading, virtualized lists)
32. End-to-end testing
33. Deployment configuration (Docker, IIS, or Azure App Service)

## Testing Strategy

- **Unit tests**: xUnit for API, Jest/bUnit for frontend -- 60%+ coverage
- **Integration tests**: API endpoint tests with WebApplicationFactory
- **E2E tests**: Playwright or Cypress for critical user flows
- **Performance tests**: k6 or similar for API load testing
- **Manual testing**: Visual inspection of charts, responsive layouts, export accuracy

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontend framework choice delays | Decision paralysis | Default to Blazor WASM (stays in .NET ecosystem) |
| Chart library limitations | Missing chart types | Evaluate libraries early; fallback to simpler visualizations |
| Scope creep into Phase 3+ features | Timeline blows up | Strict Phase 1 feature parity first; Phase 3 sheets as future backlog |
| Authentication complexity | Delays MVP | Start with API key (simplest); upgrade to JWT later |
| Data refresh mechanism complexity | Over-engineering | Start with manual refresh button; add scheduling later |

## Dependencies

- **FD-040** (C# Rewrite): Data models, extraction logic, and Excel generation reused as shared library
- Phase 1 Python scripts: Reference implementation for data accuracy validation

## Questions

- [ ] Frontend preference: Blazor WASM (C# everywhere) or React+TypeScript (industry standard)?
- [ ] Hosting target: Internal IIS, Azure App Service, Docker container?
- [ ] Authentication: Internal-only (API key) or SSO integration needed?
- [ ] Database: SQLite (simple, file-based) or SQL Server (production-grade)?
- [ ] Should this include Phase 3 sheets (AI Maturity, M&A, etc.) or strictly Phase 1 parity?

## Status

Planning
