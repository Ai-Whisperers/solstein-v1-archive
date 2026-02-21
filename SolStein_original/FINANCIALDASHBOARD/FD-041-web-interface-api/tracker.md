# FD-041: Tracker

## Phase A: API Foundation (2-3 days)

- [ ] Create ASP.NET Core Web API project
- [ ] Define OpenAPI spec / API contracts
- [ ] Implement data access layer (reuse FD-040 models)
- [ ] `/api/competitors` -- list all competitors with basic info
- [ ] `/api/competitors/{id}` -- competitor detail with all metrics
- [ ] `/api/summary` -- executive summary KPIs
- [ ] `/api/health` -- health check endpoint
- [ ] Swagger UI at `/swagger`
- [ ] Unit tests for controllers and services

## Phase B: API Enrichment (2-3 days)

- [ ] Filtering: classification, geography, revenue range, employee count
- [ ] Sorting and pagination for list endpoints
- [ ] `/api/charts/revenue` -- pre-aggregated revenue chart data
- [ ] `/api/charts/funding` -- pre-aggregated funding chart data
- [ ] `/api/charts/employees` -- pre-aggregated employee chart data
- [ ] `/api/charts/saas` -- SaaS maturity chart data
- [ ] `/api/classifications` -- classification matrix data
- [ ] `/api/geographic` -- geographic distribution data
- [ ] Caching layer (IMemoryCache)
- [ ] Authentication middleware (API key or JWT)
- [ ] CORS configuration
- [ ] Integration tests for all endpoints

## Phase C: Web Frontend Foundation (3-4 days)

- [ ] Set up frontend project (Blazor WASM or React+TypeScript)
- [ ] Layout: navigation, header, sidebar
- [ ] Executive Summary dashboard page with KPI cards
- [ ] Competitor list page (table with filter/sort/search)
- [ ] Competitor detail page (full profile, all metrics)
- [ ] Responsive CSS (Tailwind CSS or MudBlazor)
- [ ] Loading states, error handling, empty states

## Phase D: Charts & Visualizations (2-3 days)

- [ ] Integrate charting library
- [ ] Revenue bar chart (matches Excel Revenue Leaderboard)
- [ ] Funding bar chart (matches Excel Funding Leaderboard)
- [ ] Employee growth chart (matches Excel Employee Growth)
- [ ] SaaS maturity chart (matches Excel SaaS Maturity)
- [ ] Classification matrix (interactive grid/heatmap)
- [ ] Eneve vs Market comparison chart
- [ ] Efficiency scatter plot

## Phase E: Polish & Integration (1-2 days)

- [ ] Excel export endpoint (reuse FD-040 ExcelReportGenerator)
- [ ] PDF export for executive summary
- [ ] Dark/light theme toggle
- [ ] Performance optimization (lazy loading, virtualized lists)
- [ ] End-to-end tests (Playwright or Cypress)
- [ ] Deployment configuration (Docker / IIS / Azure)
- [ ] Final validation: zero warnings build
