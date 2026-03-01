# STORY-025: Define Abstract Repository Interfaces

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-007: Domain-Driven Design Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> The repository pattern exists by naming convention only. `infrastructure/company_repository.py` is a concrete implementation with no abstract interface. There is no `Protocol` or `ABC` defining the contract. Application services call the concrete class directly. Testing requires the real database.

## Problem Statement

Without abstract repository interfaces, application services are tightly coupled to concrete infrastructure implementations. The `CompanyRepository` is called directly — not through an interface — meaning:

1. Unit tests for application services require a real database connection (or must mock the concrete class's internal methods, which is fragile)
2. Changing the storage backend (e.g., from PostgreSQL to a document store, or adding a caching decorator) requires modifying every caller
3. The domain layer has an implicit dependency on SQLAlchemy, violating the dependency inversion principle
4. There is no documented contract for what a repository must provide — the contract is whatever the concrete class happens to implement today

## Impact

| Dimension | Effect |
|-----------|--------|
| **Testability** | Unit tests for application services require a real database connection |
| **Flexibility** | Changing the storage backend requires modifying all callers |
| **Architecture** | Infrastructure leaks into the application and domain layers |
| **Contract Clarity** | No documented repository contract — the interface is "whatever the concrete class does" |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/repositories.py` | Add | New module defining `CompanyRepository` Protocol |
| `src/solstein/infrastructure/company_repository.py` | Modify | Must implement the Protocol explicitly |
| All application service files that use repositories | Modify | Must depend on the Protocol, not the concrete class |
| Dependency injection configuration | Modify | Must wire concrete implementation to Protocol |

## Architectural Requirements

- **REQ-1**: A `CompanyRepository` Protocol must define the contract for all company persistence operations (create, read, update, delete, query)
- **REQ-2**: The concrete `company_repository.py` must implement the Protocol, and this must be verifiable by mypy (the concrete class must satisfy the Protocol structurally)
- **REQ-3**: All application services must depend on the `CompanyRepository` Protocol, not the concrete `SqlAlchemyCompanyRepository` class
- **REQ-4**: The dependency injection configuration (FastAPI dependencies or a DI container) must wire the concrete implementation to the Protocol at application startup

## Acceptance Criteria

- [ ] A `CompanyRepository` Protocol exists in the domain layer (`domain/repositories.py`)
- [ ] The concrete implementation satisfies the Protocol — verified by mypy with no type errors
- [ ] Application services type-hint their repository dependency as the Protocol, not the concrete class
- [ ] Application service unit tests can operate with a mock repository (a class satisfying the Protocol with in-memory storage)
- [ ] No application service file imports from `infrastructure/company_repository.py` directly

## Definition of Done

**Tests Required:**
- [ ] Unit test: application service works with a mock repository implementing the Protocol
- [ ] Type check: `mypy` confirms the concrete class satisfies the Protocol (zero type errors on repository files)
- [ ] Test: a second repository implementation (in-memory, for tests) also satisfies the Protocol

**Documentation Required:**
- [ ] Docstrings on the Protocol explaining each method's contract, parameters, return types, and error conditions
- [ ] Comment in DI configuration explaining the wiring

**Code Review Gate:**
- [ ] Reviewer confirms no application service imports the concrete repository class directly
- [ ] Reviewer confirms mypy passes on all repository-related files

## Notes

This story is independent of the other DDD stories and can be started immediately. It does not require Value Objects or a rich domain model — it is purely about decoupling the application layer from the infrastructure layer.

The Protocol approach (structural subtyping) is preferred over ABC (nominal subtyping) for Python repositories because it does not require the concrete class to inherit from a base class. The concrete class just needs to have the right methods with the right signatures.
