# Task 8: Migrate All Services to Async Repos - Detailed Breakdown

**Status**: IN PROGRESS  
**Priority**: HIGH  
**Estimated Time**: 2-3 hours  
**Files to Modify**: 3 files  

---

## Files to Update

### 1. `src/solstein/api/dependencies.py` (CRITICAL)

**Current State**:
- Line 11: Imports JsonFileRepository and SupabaseRepository
- Line 19-31: `get_repository()` function returns sync repositories
- Problem: Returns JsonFileRepository or SupabaseRepository (both sync)

**Required Changes**:
```python
# REMOVE:
from ..data.repositories import JsonFileRepository, SupabaseRepository

# ADD:
from ..infrastructure.company_repository import CompanyRepository

# REPLACE get_repository() function with:
async def get_company_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRepository:
    """Get async CompanyRepository instance."""
    return CompanyRepository(session)
```

**Impact**: All endpoints using `get_repository()` must be updated to use `get_company_repository()`

---

### 2. `src/solstein/analytics/activities.py`

**Current State**:
- Line 17: Imports JsonFileRepository
- Line 25, 29: Returns JsonFileRepository() in methods

**Required Changes**:
```python
# REMOVE:
from ..data.repositories import JsonFileRepository, SupabaseRepository

# ADD:
from ..infrastructure.company_repository import CompanyRepository
from sqlalchemy.ext.asyncio import AsyncSession

# REPLACE methods to accept AsyncSession and return CompanyRepository:
async def get_company_repository(session: AsyncSession) -> CompanyRepository:
    return CompanyRepository(session)
```

**Impact**: All activity methods must be async and accept AsyncSession

---

### 3. `src/solstein/api/routers/export.py`

**Current State**:
- Line 144: Imports JsonFileRepository
- Line 146: Checks `isinstance(repo, JsonFileRepository)`

**Required Changes**:
```python
# REMOVE:
from ...data.repositories import JsonFileRepository

# REPLACE isinstance check with:
# Check if repo is CompanyRepository instead
if not isinstance(repo, CompanyRepository):
    # Handle non-database repositories
    pass
```

**Impact**: Export logic must work with async repositories

---

## Step-by-Step Migration Process

### Step 1: Update dependencies.py
1. Remove JsonFileRepository and SupabaseRepository imports
2. Add CompanyRepository import
3. Replace `get_repository()` with `get_company_repository()`
4. Make it async and accept AsyncSession dependency
5. Return CompanyRepository(session)

### Step 2: Update activities.py
1. Remove JsonFileRepository import
2. Add CompanyRepository and AsyncSession imports
3. Update all methods to be async
4. Accept AsyncSession as parameter
5. Return CompanyRepository(session)

### Step 3: Update export.py
1. Remove JsonFileRepository import
2. Update isinstance checks to use CompanyRepository
3. Ensure all repository calls are awaited

### Step 4: Update all endpoints using get_repository()
1. Find all endpoints that use `get_repository()`
2. Replace with `get_company_repository()`
3. Make endpoints async if not already
4. Add `await` before all repository calls

### Step 5: Test
```bash
pytest tests/ -v
mypy src/solstein --strict
```

---

## Code Examples

### Before (Sync)
```python
def get_repository() -> CompanyRepository:
    return JsonFileRepository()

@router.get("/companies")
def get_companies(repo: CompanyRepository = Depends(get_repository)):
    return repo.get_all()  # Sync call
```

### After (Async)
```python
async def get_company_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRepository:
    return CompanyRepository(session)

@router.get("/companies")
async def get_companies(
    repo: CompanyRepository = Depends(get_company_repository),
):
    return await repo.get_all()  # Async call
```

---

## Verification Checklist

- [ ] All JsonFileRepository imports removed
- [ ] All SupabaseRepository imports removed
- [ ] CompanyRepository imported in all files
- [ ] get_repository() replaced with get_company_repository()
- [ ] All repository methods called with await
- [ ] All endpoints using repositories are async
- [ ] Test collection passes (1434 items)
- [ ] No import errors
- [ ] No type errors with mypy

---

## Common Issues & Solutions

### Issue: "RuntimeError: no running event loop"
**Cause**: Calling async function without await
**Solution**: Add `await` before all repository method calls

### Issue: "TypeError: object is not awaitable"
**Cause**: Repository method is not async
**Solution**: Ensure CompanyRepository methods are async

### Issue: "AttributeError: 'NoneType' object"
**Cause**: Repository method returned None
**Solution**: Check that repository methods return proper objects

### Issue: Test failures
**Cause**: Tests not using async fixtures
**Solution**: Ensure tests use async fixtures from conftest.py

---

## Files That Will Need Updates After Task 8

### Endpoints using get_repository()
- `src/solstein/api/routers/companies.py`
- `src/solstein/api/routers/analysis.py`
- `src/solstein/api/routers/export.py`
- Any other routers using get_repository()

### Services using repositories
- `src/solstein/api/services/enrichment_service.py`
- `src/solstein/api/services/drill_down_service.py`
- `src/solstein/data/enrichment_service.py`

---

## Success Criteria

✅ All JsonFileRepository usages removed  
✅ All SupabaseRepository usages removed  
✅ All services use CompanyRepository  
✅ All repository calls are async  
✅ All endpoints are async  
✅ Test collection passes (1434 items)  
✅ No import errors  
✅ No type errors  

---

## Next Task (Task 9)

After Task 8 is complete:
1. Run full test suite: `pytest tests/ -v`
2. Verify all tests pass
3. Check for any remaining issues
4. Mark Task 9 as complete

---

**End of Task 8 Breakdown**
