# Error Handling Rules

## Core Philosophy

**NEVER silently swallow errors.** This is the #1 code quality rule.

Every error must be:
1. **Detected** - Catch or detect the error
2. **Logged** - Record what happened with context
3. **Handled** - Take appropriate action
4. **Propagated** - Or return structured error result

## Error Handling Patterns

### ❌ FORBIDDEN - Silent Failure
```python
# Never do this - "Throw it in the ocean and hope it floats"
try:
    await operation()
except:
    pass  # Silently fails

try:
    await operation()
except Exception:
    return None  # Hides the error

try:
    data = fetch_data()
except:
    data = {}  # Silent fallback
```

### ✅ REQUIRED - Acknowledge Every Error
```python
# Option 1: Log and re-raise
try:
    await operation()
except Exception as e:
    logger.error(f"[Context] Operation failed: {e}")
    raise

# Option 2: Return structured error result
try:
    result = await operation()
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"[Context] Operation failed: {e}")
    return {"success": False, "error": str(e)}

# Option 3: Log with context and continue
try:
    data = fetch_data()
except Exception as e:
    logger.warning(f"[DataFetch] Failed to fetch data for {company_id}: {e}")
    data = {}  # Fallback with logged warning
```

## Exception Types

### Use Specific Exceptions
```python
# ❌ BAD - Catching everything
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ GOOD - Catch specific exceptions
from sqlalchemy.exc import IntegrityError, NoResultFound
from requests.exceptions import RequestException, Timeout

except IntegrityError as e:
    logger.error(f"[Database] Integrity error: {e}")
    raise DatabaseError(f"Failed to save {entity}") from e

except NoResultFound:
    logger.warning(f"[Database] Entity {entity_id} not found")
    return None

except Timeout:
    logger.error(f"[ExternalAPI] Request timeout after {timeout}s")
    raise ExternalAPIError("Service unavailable") from e
```

### Never Use Bare Except
```python
# ❌ FORBIDDEN - Bare except catches KeyboardInterrupt, SystemExit
except:
    pass

# ❌ FORBIDDEN - Catches BaseException
except BaseException:
    pass

# ✅ REQUIRED - Always specify exception type
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except TypeError as e:
    logger.error(f"Type mismatch: {e}")
except Exception as e:  # Only if truly generic needed
    logger.error(f"Unexpected error: {e}")
    raise
```

## Error Context

### Always Include Context
```python
# ❌ BAD - No context
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ GOOD - Rich context
except Exception as e:
    logger.error(
        f"[EnrichmentService] Failed to enrich company",
        extra={
            "company_id": company_id,
            "source": data_source,
            "operation": "fetch_financials",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
    )
```

## Structured Error Results

### Return Error Information
```python
from typing import TypedDict

class Result(TypedDict):
    success: bool
    data: dict | None
    error: str | None
    error_code: str | None

def process_company(company_id: str) -> Result:
    try:
        company = fetch_company(company_id)
        if not company:
            return {
                "success": False,
                "data": None,
                "error": f"Company {company_id} not found",
                "error_code": "NOT_FOUND"
            }
        
        enriched = enrich_company(company)
        return {
            "success": True,
            "data": enriched.to_dict(),
            "error": None,
            "error_code": None
        }
    except ValidationError as e:
        return {
            "success": False,
            "data": None,
            "error": f"Validation failed: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except Exception as e:
        logger.error(f"[ProcessCompany] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
```

## Async Error Handling

### Async Patterns
```python
# ✅ Handle errors in async functions
async def fetch_data_async(url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"[HTTP] Request failed for {url}: {e}")
        raise ExternalAPIError(f"Failed to fetch {url}") from e
    except asyncio.TimeoutError:
        logger.error(f"[HTTP] Timeout for {url}")
        raise ExternalAPIError(f"Timeout fetching {url}")

# ✅ Handle errors in gather
results = await asyncio.gather(
    *[fetch_data_async(url) for url in urls],
    return_exceptions=True  # Don't fail fast
)

for url, result in zip(urls, results):
    if isinstance(result, Exception):
        logger.error(f"[BatchFetch] Failed for {url}: {result}")
    else:
        process_result(result)
```

## Error Recovery

### Graceful Degradation
```python
def enrich_company(company_id: str) -> Company:
    company = Company()
    
    # Try primary source
    try:
        company.financials = fetch_from_sec_edgar(company_id)
    except Exception as e:
        logger.warning(f"[Enrichment] SEC EDGAR failed: {e}")
        
        # Try fallback
        try:
            company.financials = fetch_from_companies_house(company_id)
        except Exception as e2:
            logger.error(f"[Enrichment] Fallback failed: {e2}")
            company.financials = None  # Graceful degradation
    
    return company
```

## Error Logging Levels

### Use Appropriate Levels
```python
# DEBUG - Detailed information for debugging
debug_logger.debug(f"Processing item {item_id}")

# INFO - General operational information
info_logger.info(f"Enrichment completed for {company_id}")

# WARNING - Something unexpected but not an error
warning_logger.warning(f"Cache miss for {key}, fetching from source")

# ERROR - Something failed but operation can continue
error_logger.error(f"Failed to enrich {company_id} from {source}")

# CRITICAL - System-level failure
critical_logger.critical(f"Database connection lost: {e}")
```

## Testing Error Handling

### Test Error Paths
```python
def test_fetch_company_not_found():
    """Test handling of missing company."""
    with pytest.raises(CompanyNotFoundError):
        fetch_company("nonexistent-id")

def test_fetch_company_network_error():
    """Test handling of network failure."""
    with mock.patch('requests.get', side_effect=RequestException("Network error")):
        with pytest.raises(ExternalAPIError):
            fetch_company("valid-id")

def test_enrich_company_partial_failure():
    """Test graceful degradation when one source fails."""
    with mock.patch('fetch_from_sec_edgar', side_effect=Exception("SEC down")):
        with mock.patch('fetch_from_companies_house', return_value=mock_data):
            result = enrich_company("valid-id")
            assert result.financials is not None  # Fallback worked
```
