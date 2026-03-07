# Story 18.1: Unify Logging Pipeline

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P0
> **Effort**: 3 story points
> **Dependencies**: None
> **Related**: Story 18.2, Story 18.4

---

## Description

Consolidate all logging to use a single Loguru pipeline. Route stdlib logging through Loguru's `InterceptHandler`, remove stdlib logger usage across the codebase, and ensure consistent formatting and configuration.

### Current Broken State

```python
# utils/logging.py - Loguru setup
def setup_logging(level="INFO", json_format=False, ...):
    # ... configures loguru

# api/middleware/security.py - Uses stdlib
import logging
logger = logging.getLogger(__name__)
logger.debug("Security headers added")

# infrastructure/outbox_worker.py - Uses stdlib
import logging
logger = logging.getLogger(__name__)
logger.exception("Failed processing outbox record", extra={...})

# core/error_handler.py - Uses stdlib AuditLogger
class AuditLogger:
    def __init__(self, log_file="logs/audit.log"):
        self.logger = logging.getLogger("audit")
```

**Problems:**
- Different log formats between Loguru and stdlib
- Context (request_id, correlation_id) lost in stdlib logs
- Configuration split between two systems
- `extra={...}` dicts in stdlib vs `.bind()` in Loguru

---

## Acceptance Criteria

- [ ] All stdlib `logging.getLogger()` calls replaced with Loguru `from loguru import logger`
- [ ] `InterceptHandler` properly configured to capture ALL stdlib logs (including third-party)
- [ ] `setup_logging()` accepts JSON format for production
- [ ] All logs include consistent base fields: timestamp, level, name, function, line
- [ ] Stdlib logging imports removed from:
  - `api/middleware/security.py`
  - `infrastructure/outbox_worker.py`
  - `infrastructure/research_dual_write.py`
  - `core/error_handler.py`
  - `data/error_logging.py`
  - Any other modules using stdlib
- [ ] Configuration for third-party loggers (uvicorn, fastapi, sqlalchemy) routed through Loguru
- [ ] Documentation updated with new logging approach

---

## Implementation

### Step 1: Update `utils/logging.py`

```python
import sys
import logging
from typing import Any
from loguru import logger

class InterceptHandler(logging.Handler):
    """Intercept stdlib logging and route to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller frame (skip logging internals)
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Log with exception info if present
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def format_record(record: dict[str, Any]) -> str:
    """Format log record with extra context."""
    base_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    )

    # Add any extra context fields
    extra = record.get("extra", {})
    if extra:
        extra_str = " | ".join(f"<magenta>{k}</magenta>=<yellow>{v}</yellow>"
                               for k, v in extra.items() if k not in ("correlation_id", "request_id"))
        if extra_str:
            base_format += " | " + extra_str

    base_format += " - <level>{message}</level>\n{exception}"
    return base_format

def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: str | None = None,
    rotation: str = "500 MB",
    retention: str = "30 days"
) -> None:
    """Configure unified logging with Loguru.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for production
        log_file: Optional file path for logging
        rotation: Log rotation size
        retention: Log retention period
    """
    # Remove default handler
    logger.remove()

    # Configure serialization for JSON
    serialize = json_format

    # Add stdout handler
    if json_format:
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,
            format="{message}",  # JSON serialization handles format
        )
    else:
        logger.add(
            sys.stdout,
            level=level,
            format=format_record,
            colorize=True,
        )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="gz",
            serialize=json_format,
            format="{message}" if json_format else format_record,
        )

    # Intercept stdlib logging - CRITICAL for unified pipeline
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=logging.NOTSET,  # Let Loguru handle filtering
        force=True,
    )

    # Configure third-party loggers to use our handler
    for log_name in ("uvicorn", "uvicorn.access", "fastapi", "sqlalchemy"):
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(
        "Logging system initialized",
        level=level,
        json_format=json_format,
        log_file=log_file,
    )
```

### Step 2: Migrate `api/middleware/security.py`

```python
# BEFORE
import logging
logger = logging.getLogger(__name__)

# AFTER
from loguru import logger
# ... remove getLogger line

# Replace:
logger.debug("Security headers added")
# With:
logger.debug("Security headers added")

# Replace:
logger.warning("Authentication failed", extra={"code": "AUTH_001"})
# With:
logger.bind(code="AUTH_001").warning("Authentication failed")
```

### Step 3: Migrate `infrastructure/outbox_worker.py`

```python
# BEFORE
import logging
logger = logging.getLogger(__name__)

# AFTER
from loguru import logger

# Replace:
logger.exception(
    "Failed processing outbox record",
    extra={"event_key": record.event_key, "event_type": record.event_type}
)
# With:
logger.bind(event_key=record.event_key, event_type=record.event_type).exception(
    "Failed processing outbox record"
)
```

### Step 4: Migrate `core/error_handler.py`

The `AuditLogger` needs special consideration as it writes to a separate audit log file. Options:

**Option A: Keep stdlib for audit, intercept everything else**
```python
# Only stdlib logger allowed - for audit separation
class AuditLogger:
    def __init__(self, log_file="logs/audit.log"):
        self.logger = logging.getLogger("audit")
        # Ensure audit logger doesn't get intercepted
        self.logger.propagate = False
```

**Option B: Use Loguru with separate sink**
```python
# Add audit-specific logger with separate file
audit_logger = logger.bind(audit=True)
audit_logger.add("logs/audit.log", filter=lambda r: "audit" in r.get("extra", {}))
```

**Recommended: Option B** for true unification.

---

## Testing

```python
# tests/unit/test_logging.py
import pytest
from loguru import logger
from unittest.mock import MagicMock
from solstein.utils.logging import setup_logging, InterceptHandler

def test_intercept_handler_routes_stdlib():
    """Test that stdlib logs are routed to Loguru."""
    import logging

    # Setup interception
    setup_logging(level="DEBUG")

    # Capture Loguru output
    captured = []
    logger.remove()
    logger.add(lambda msg: captured.append(msg), level="DEBUG")

    # Log via stdlib
    stdlib_logger = logging.getLogger("test")
    stdlib_logger.warning("Test message from stdlib")

    assert any("Test message from stdlib" in str(m) for m in captured)

def test_json_format():
    """Test JSON serialization for production."""
    import json
    captured = []

    def capture_json(message):
        captured.append(json.loads(message))

    logger.remove()
    logger.add(capture_json, serialize=True, level="INFO")

    logger.info("Test message", extra_field="value")

    assert len(captured) == 1
    assert captured[0]["text"] == "Test message"
    assert captured[0]["extra"]["extra_field"] == "value"
```

---

## Verification Steps

1. **Check for remaining stdlib imports:**
   ```bash
   grep -r "import logging" src/solstein --include="*.py" | grep -v "InterceptHandler"
   ```
   Expected: Only `utils/logging.py` should import stdlib logging

2. **Verify unified output:**
   ```python
   # Run in Python shell
   from solstein.utils.logging import setup_logging
   setup_logging()

   import logging
   logging.getLogger("test").info("stdlib message")
   # Should appear in same format as Loguru logs
   ```

3. **Check JSON format:**
   ```python
   setup_logging(json_format=True)
   logger.info("test", key="value")
   # Should output valid JSON with all fields
   ```

---

## Rollout Plan

1. **Phase 1**: Update `utils/logging.py` with enhanced `InterceptHandler`
2. **Phase 2**: Migrate each module one at a time (security → outbox → research_dual_write → core → data)
3. **Phase 3**: Remove all stdlib logging imports except in `utils/logging.py`
4. **Phase 4**: Enable JSON format in staging and verify with log aggregator

---

## Related Files

- `src/solstein/utils/logging.py` - Main configuration
- `src/solstein/api/middleware/security.py` - Security middleware
- `src/solstein/infrastructure/outbox_worker.py` - Outbox worker
- `src/solstein/infrastructure/research_dual_write.py` - Research persistence
- `src/solstein/core/error_handler.py` - Error handling
- `src/solstein/data/error_logging.py` - Error logging utilities
