# Solstein - Troubleshooting Guide

Common issues and their solutions when working with Solstein and Supabase.

## Database Connection Issues

### "Connection refused" or "Timeout"

**Symptoms**:
```
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solutions**:

1. **Verify your DATABASE__URL** (note: double underscore — pydantic-settings nested model convention)
   ```bash
   echo $DATABASE__URL
   # Should be: postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
   ```

2. **Check Supabase status**
   - Go to [status.supabase.com](https://status.supabase.com)
   - Verify no outages

3. **Verify IP allowlist**
   - Supabase Dashboard → Database → Network
   - Add your IP if not already allowed

4. **Test with psql**
   ```bash
   psql "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require"
   ```

### "SSL required"

**Symptoms**:
```
FATAL: SSL connection is required
```

**Solution**: Add `sslmode=require` to your connection URL:
```bash
DATABASE__URL="postgresql://...?sslmode=require"
```

### "Too many connections"

**Symptoms**:
```
asyncpg.exceptions.TooManyConnectionsError: sorry, too many clients already
```

**Solutions**:

1. **Reduce pool size in conftest.py**:
   ```python
   engine = create_async_engine(
       url,
       pool_size=3,  # Reduce from 5
       max_overflow=5,  # Reduce from 10
   )
   ```

2. **Close connections properly**:
   ```python
   await engine.dispose()  # Always dispose after use
   ```

3. **Check active connections in Supabase**:
   - Dashboard → Database → Connections

## Test Failures

### "Event loop is closed"

**Symptoms**:
```
RuntimeError: Event loop is closed
```

**Cause**: Mixing sync and async fixtures or improper event loop handling.

**Solution**:
- Ensure `pytest.ini` has:
  ```ini
  asyncio_mode = auto
  asyncio_default_fixture_loop_scope = function
  ```
- Don't manually create event loops in tests
- Use `@pytest.mark.asyncio` on test classes/methods

### "Fixture not found"

**Symptoms**:
```
Fixture 'db_session' not found
```

**Solution**:
1. Check conftest.py exists in tests/ directory
2. Verify conftest.py is being loaded:
   ```bash
   pytest --fixtures  # List all available fixtures
   ```
3. Ensure imports are correct in conftest.py

### "Module not found" errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'solstein'
```

**Solution**:
```bash
# Use uv run which handles PYTHONPATH
uv run pytest tests/unit/test_fact_repository.py

# Or set PYTHONPATH manually
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Tests pass locally but fail in CI

**Symptoms**:
- Tests pass on your machine
- Fail in GitHub Actions

**Common causes**:

1. **Missing environment variables**
   - Check GitHub Secrets are set correctly
   - Verify secret names match workflow file

2. **Different database state**
   - CI uses fresh database
   - You may have test data locally
   - Run `await cleanup_test_database(session)` in setup

3. **Timing issues**
   - CI may be slower
   - Increase timeouts if needed
   - Use `pytest.mark.slow` for slow tests

### "IntegrityError" or FK violations

**Symptoms**:
```
sqlalchemy.exc.IntegrityError: foreign key violation
```

**Cause**: Creating records with invalid foreign keys.

**Solution**:
```python
# Create dependencies first
batch = await create_test_batch(db_session, "comp-123")

# Then create dependent records
fact = await create_test_fact(
    db_session,
    batch_id=str(batch.batch_id),  # Use valid batch_id
    company_id="comp-123"
)
```

## Import and Dependency Issues

### "No module named 'asyncpg'"

**Solution**:
```bash
uv add asyncpg
```

### "No module named 'pytest_asyncio'"

**Solution**:
```bash
uv add pytest-asyncio
```

### SQLAlchemy version conflicts

**Symptoms**:
```
AttributeError: 'AsyncSession' object has no attribute 'execute'
```

**Solution**: Ensure SQLAlchemy 2.0+ is installed:
```bash
uv add "sqlalchemy>=2.0"
```

## Performance Issues

### Tests are very slow

**Symptoms**: Each test takes 5+ seconds

**Solutions**:

1. **Check for N+1 queries**:
   ```python
   # Bad: N+1 queries
   for fact in facts:
       print(fact.batch.status)  # Triggers query for each fact
   
   # Good: Eager load
   result = await session.execute(
       select(Fact).options(selectinload(Fact.batch))
   )
   ```

2. **Reduce test data size**:
   - Don't create 1000 records in tests
   - Create minimal data needed for the test

3. **Use connection pooling**:
   - Already configured in conftest.py
   - Verify pool settings are appropriate

### Memory issues during tests

**Symptoms**: Tests run out of memory

**Solutions**:

1. **Limit result sets**:
   ```python
   result = await session.execute(select(Fact).limit(100))
   ```

2. **Use streaming** for large queries:
   ```python
   async with session.stream(select(Fact)) as result:
       async for fact in result:
           process(fact)
   ```

## GitHub Actions Issues

### Workflow not triggering

**Symptoms**: Push to main doesn't trigger workflow

**Solution**:
1. Check workflow file is in `.github/workflows/`
2. Verify branch names match:
   ```yaml
   on:
     push:
       branches: [main, develop]  # Your branch names
   ```
3. Check if Actions are enabled in repository settings

### Secrets not working

**Symptoms**: `secrets.DATABASE_URL_TEST` is empty

**Solution**:
1. Verify secret is set: Settings → Secrets → Actions
2. Check secret name matches exactly (case-sensitive)
3. Secrets aren't available for forks in PRs

### Workflow timeout

**Symptoms**: Workflow cancelled after 360 minutes

**Solution**:
```yaml
jobs:
  test:
    timeout-minutes: 30  # Set appropriate timeout
```

## Supabase-Specific Issues

### "Project not found"

**Symptoms**:
```
FATAL: database "postgres" does not exist
```

**Solution**: Your project reference is wrong. Check:
```
postgresql://postgres:[password]@db.[PROJECT-REF].supabase.co:5432/postgres
#                          ^^^^^^^^^^^
#                          This must match your project
```

### Row Level Security blocking queries

**Symptoms**: Queries return no results or permission denied

**Solution**:
1. Check RLS policies in Supabase Dashboard
2. Disable RLS for testing (not recommended for production):
   ```sql
   ALTER TABLE companies DISABLE ROW LEVEL SECURITY;
   ```

### Database paused

**Symptoms**: Connection timeouts after period of inactivity

**Solution**:
- Supabase pauses free tier projects after 7 days of inactivity
- Go to Supabase Dashboard and resume the project
- Consider upgrading to prevent auto-pausing

## Environment Setup Issues

### uv not found

**Symptoms**: `command not found: uv`

**Solution**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Virtual environment issues

**Symptoms**: 
```
ModuleNotFoundError even after uv sync
```

**Solution**:
```bash
# Clean and reinstall
rm -rf .venv
uv sync
```

### Permission denied errors

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Fix permissions
chmod +x $(find . -name "*.sh")
```

## Debugging Tips

### Enable SQL logging

```python
engine = create_async_engine(
    url,
    echo=True,  # Log all SQL queries
)
```

### Check database state during tests

```python
async def test_debug(db_session):
    # Add breakpoint or print
    result = await db_session.execute(select(Fact))
    facts = result.scalars().all()
    print(f"Found {len(facts)} facts: {facts}")
    
    # Or use pdb
    import pdb; pdb.set_trace()
```

### Test database connection

```bash
# Quick connection test
python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('your-url')
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print(result.scalar_one())
    await engine.dispose()

asyncio.run(test())
"
```

## Getting Help

If you're stuck:

1. **Check the evidence files**:
   ```bash
   ls -la .sisyphus/evidence/
   ```

2. **Review the plan**:
   ```bash
   cat .sisyphus/plans/supabase-professional-setup.md
   ```

3. **Check Supabase documentation**:
   - [supabase.com/docs](https://supabase.com/docs)
   - [Database connection docs](https://supabase.com/docs/guides/database/connecting-to-postgres)

4. **Check SQLAlchemy documentation**:
   - [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

5. **Enable verbose pytest output**:
   ```bash
   uv run pytest -v --tb=long --capture=no
   ```

## Quick Fixes Checklist

- [ ] Database URL correct with `sslmode=require`
- [ ] Environment variables exported: `export DATABASE__URL="..."`
- [ ] Using `uv run` not direct python
- [ ] All dependencies installed: `uv sync`
- [ ] Supabase project is active (not paused)
- [ ] IP is allowlisted in Supabase
- [ ] pytest.ini has `asyncio_mode = auto`
- [ ] Tests use `@pytest.mark.asyncio`
- [ ] Fixtures use `db_session` from conftest.py
- [ ] Foreign keys created before dependent records
