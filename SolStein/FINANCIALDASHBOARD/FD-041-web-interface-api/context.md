# FD-041 Context

**Last Updated**: 2026-02-17

## Technical Background

The competitive financial dashboard exists as Python scripts generating static Excel workbooks. FD-040 ports these to C#. This ticket builds on the C# data layer to create a web-based interactive dashboard with a REST API.

The target architecture:
- **API layer**: ASP.NET Core Web API with Swagger, authentication, caching
- **Frontend**: Blazor WASM or React+TypeScript SPA
- **Data layer**: Reuses FD-040 C# models and extraction services
- **Storage**: SQLite (dev) / SQL Server (prod) or file-based with caching
- **Export**: On-demand Excel/PDF generation reusing FD-040 report generator

## Current Focus

Ticket initialization and planning. No implementation work started yet. Depends on FD-040 for shared data models.

## Key Components

- **FD-040 shared library**: Data models, extraction logic, Excel generation
- **API project**: ASP.NET Core Web API controllers, services, middleware
- **Frontend project**: SPA with dashboard views, charts, interactive tables
- **Charting**: Chart.js, ApexCharts, or Blazor charting component library
- **Authentication**: JWT bearer or API key middleware

## Outstanding Issues

- Frontend framework not decided (Blazor WASM vs React+TypeScript)
- Hosting target not confirmed
- Authentication approach pending
- Database choice pending
- Scope boundary (Phase 1 only vs Phase 3 features) needs confirmation

## Next Steps

1. Wait for or start in parallel with FD-040 (shared data models)
2. Finalize technology decisions (frontend framework, hosting, auth, database)
3. Define OpenAPI spec for API contracts
4. Create ASP.NET Core project structure
