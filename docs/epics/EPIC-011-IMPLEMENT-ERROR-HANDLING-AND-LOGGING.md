# EPIC-011: Implement Error Handling and Logging

## Status: 🟡 HIGH
## Priority: P1 - Major Impact
## Effort: 5 story points
## Sprint: Required for production stability

---

## Problem Statement

The system has **inadequate error handling and logging**, making it difficult to debug issues and recover from failures.

### Current Broken State
```python
# In run_eneve_199.py - No error handling
def main():
    companies = []
    for raw in companies_raw:
        company = convert_json_to_company(raw)  # No try/except
        companies.append(company)

# Silent failures
# No logging of conversion errors
# No tracking of which companies failed
# No recovery mechanism
```

### Impact
- **Silent failures** - errors go unnoticed
- **No debugging information** when issues occur
- **Cannot recover** from partial failures
- **No audit trail** of data processing

---

## Success Criteria

- [ ] All error-prone operations have try/except blocks
- [ ] Comprehensive logging at INFO, DEBUG, and ERROR levels
- [ ] Failed companies tracked and reported
- [ ] Recovery mechanisms for partial failures
- [ ] Audit log of all data transformations
- [ ] Alerting for critical errors

---

## Technical Analysis

### Root Causes
1. **No error handling** in data conversion loops
2. **No logging** of processing steps
3. **Silent failures** - exceptions caught and ignored
4. **No recovery** - all-or-nothing processing

### Affected Files
- `scripts/run_eneve_199.py`
- `src/solstein/analytics/scoring.py`
- `src/solstein/exporters/excel.py`
- All data pipeline files

---

## Stories

### Story 11.1: Add Comprehensive Logging
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add structured logging throughout the ENEVE workflow.

**Acceptance Criteria:**
- [ ] Add logging to all major processing steps
- [ ] Log at appropriate levels (DEBUG, INFO, ERROR)
- [ ] Include context in log messages (company name, ID)
- [ ] Configure log output (file + console)
- [ ] Add correlation IDs for request tracking

**Implementation:**
```python
import logging
from contextvars import ContextVar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eneve.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('eneve')

# Context for correlation
correlation_id = ContextVar('correlation_id', default=None)

class CompanyProcessor:
    def __init__(self):
        self.logger = logging.getLogger('eneve.processor')
    
    def process_company(self, company_data: dict) -> Optional[Company]:
        """Process single company with logging."""
        company_name = company_data.get('company_name', 'Unknown')
        cid = correlation_id.get()
        
        self.logger.info(
            f"Processing company: {company_name}",
            extra={
                'correlation_id': cid,
                'company_name': company_name,
                'stage': 'conversion'
            }
        )
        
        try:
            company = self._convert(company_data)
            self.logger.info(
                f"Successfully converted: {company_name}",
                extra={
                    'correlation_id': cid,
                    'company_name': company_name,
                    'company_id': company.id,
                    'stage': 'conversion'
                }
            )
            return company
        except Exception as e:
            self.logger.error(
                f"Failed to convert: {company_name} - {str(e)}",
                extra={
                    'correlation_id': cid,
                    'company_name': company_name,
                    'error': str(e),
                    'stage': 'conversion'
                },
                exc_info=True
            )
            return None
```

---

### Story 11.2: Implement Error Recovery
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add error handling and recovery mechanisms to prevent total failures.

**Acceptance Criteria:**
- [ ] Process continues if single company fails
- [ ] Track failed companies separately
- [ ] Generate report of failures
- [ ] Allow retry of failed companies
- [ ] Partial output saved even if some fail

**Implementation:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProcessingResult:
    """Result of company processing."""
    company: Optional[Company]
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0

class BatchProcessor:
    """Process companies with error recovery."""
    
    def __init__(self):
        self.results: list[ProcessingResult] = []
        self.failed_companies: list[dict] = []
    
    async def process_batch(
        self,
        companies_raw: list[dict]
    ) -> tuple[list[Company], ProcessingReport]:
        """Process batch with error recovery."""
        successful = []
        failed = []
        
        for company_data in companies_raw:
            result = await self._process_with_recovery(company_data)
            
            if result.success and result.company:
                successful.append(result.company)
            else:
                failed.append({
                    'data': company_data,
                    'error': result.error_message
                })
        
        report = ProcessingReport(
            total=len(companies_raw),
            successful=len(successful),
            failed=len(failed),
            failures=failed
        )
        
        return successful, report
    
    async def retry_failed(
        self,
        failed: list[dict]
    ) -> tuple[list[Company], ProcessingReport]:
        """Retry failed companies."""
        return await self.process_batch(failed)

@dataclass
class ProcessingReport:
    """Report of batch processing."""
    total: int
    successful: int
    failed: int
    failures: list[dict]
    
    def to_dict(self) -> dict:
        return {
            'total': self.total,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': self.successful / self.total if self.total > 0 else 0,
            'failures': self.failures
        }
```

---

### Story 11.3: Add Audit Logging
**Priority:** P1 | **Effort:** 1 point

**Description:**
Add audit logging to track all data transformations.

**Acceptance Criteria:**
- [ ] Log all data transformations
- [ ] Log field mappings and changes
- [ ] Log scoring calculations
- [ ] Log enrichment operations
- [ ] Immutable audit log

**Implementation:**
```python
import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    """Immutable audit logging for data transformations."""
    
    def __init__(self, log_dir: str = 'logs/audit'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'audit_{self.session_id}.jsonl'
    
    def log_transformation(
        self,
        company_id: str,
        operation: str,
        input_data: dict,
        output_data: dict,
        metadata: dict = None
    ):
        """Log a data transformation."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'company_id': company_id,
            'operation': operation,
            'input': input_data,
            'output': output_data,
            'metadata': metadata or {}
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def log_scoring(
        self,
        company_id: str,
        component: str,
        base_score: float,
        adjustments: list,
        final_score: float
    ):
        """Log scoring calculation."""
        self.log_transformation(
            company_id=company_id,
            operation=f'scoring_{component}',
            input_data={'base_score': base_score},
            output_data={
                'final_score': final_score,
                'adjustments': adjustments
            }
        )

# Usage
audit = AuditLogger()
audit.log_transformation(
    company_id='eneve',
    operation='json_to_company',
    input_data={'company_name': 'Eneve', 'revenue': 5.0},
    output_data={'id': 'eneve', 'name': 'Eneve', 'financials': {'revenue': 5.0}}
)
```

---

## Dependencies

- Story 11.1 should be done first
- Stories 11.2 and 11.3 can be done in parallel

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Logging impacts performance | Medium | Async logging, configurable levels |
| Audit logs grow too large | Medium | Log rotation, compression |

## Definition of Done

- [ ] Comprehensive logging in place
- [ ] Error recovery working
- [ ] Audit logs capturing transformations
- [ ] Processing reports generated
- [ ] Documentation updated
