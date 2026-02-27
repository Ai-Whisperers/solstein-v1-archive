# Draft: Supabase Professional Setup Plan

## User Requirements (Confirmed)
- **Goal**: Complete Supabase integration with dev/test/prod environments
- **Environments**: 3 (test, dev, prod)
- **Test Strategy**: Shared test database with cleanup between suites
- **Branching**: Use Supabase branches for development isolation
- **Scale**: Solo developer (only you)
- **Approach**: Professional, thorough, production-ready

## Key Decisions Made
1. **Test Database**: Single Supabase database with per-suite cleanup
2. **Development Isolation**: Use Supabase feature branches for zero-impact testing
3. **Environment Management**: .env.test / .env.dev / .env.prod files
4. **All Tests**: Use REAL Supabase, not mocks
5. **Automation**: GitHub Actions for CI/CD test runs

## Scope Inclusions (IN)
- Set up Supabase production project (if not exists)
- Create test database in Supabase
- Create dev branch in Supabase
- Database schema migrations
- pytest fixtures for Supabase connections
- Environment configuration files
- CI/CD GitHub Actions for test automation
- Documentation for environment setup
- Data cleanup/reset strategies

## Scope Exclusions (OUT)
- Do NOT touch existing refresh connector tests (Batch 1A)
- Do NOT modify api/ or core/ layers yet
- Do NOT change database models themselves
- Do NOT set up production monitoring/alerts yet

## Technical Approach
- Primary: Supabase (PostgreSQL 15+)
- Test Framework: pytest with real database
- Isolation: Supabase branches for dev, shared test DB with cleanup
- Migrations: Alembic for schema management
- CI/CD: GitHub Actions running tests on each commit

## Open Questions / Blockers
None - all requirements clear!
