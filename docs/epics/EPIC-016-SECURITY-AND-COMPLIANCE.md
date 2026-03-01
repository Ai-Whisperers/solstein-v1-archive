# EPIC-016: Security and Compliance

## Status: 🟡 HIGH
## Priority: P1 - Major Impact
## Effort: 5 story points
## Sprint: Required for production

---

## Problem Statement

The system has **security vulnerabilities** and lacks compliance measures needed for production use.

### Current Issues
- API keys stored in code
- No input sanitization
- No audit logging
- No access controls
- No data encryption

### Impact
- **Security breaches** possible
- **Compliance violations**
- **Data exposure** risk
- **Unauthorized access**

---

## Success Criteria

- [ ] API keys in environment variables only
- [ ] Input sanitization on all inputs
- [ ] Audit logging for all operations
- [ ] Access controls implemented
- [ ] Data encrypted at rest and in transit
- [ ] Security audit passed

---

## Stories

### Story 16.1: Secure API Key Management
**Priority:** P1 | **Effort:** 2 points

**Description:**
Move all API keys to secure environment-based configuration.

**Acceptance Criteria:**
- [ ] Remove all hardcoded API keys
- [ ] Use environment variables
- [ ] Add .env.example file
- [ ] Document key rotation process
- [ ] Add key validation on startup

**Implementation:**
```python
# config.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings with secure defaults."""
    
    # API Keys
    crunchbase_api_key: str = ""
    linkedin_api_key: str = ""
    news_api_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator('crunchbase_api_key', 'linkedin_api_key', 'news_api_key')
    def validate_api_key(cls, v):
        if v and len(v) < 10:
            raise ValueError("API key appears too short")
        return v

# .env.example
CRUNCHBASE_API_KEY=your_crunchbase_api_key_here
LINKEDIN_API_KEY=your_linkedin_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

---

### Story 16.2: Implement Input Sanitization
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add input sanitization to prevent injection attacks.

**Acceptance Criteria:**
- [ ] Sanitize all string inputs
- [ ] Validate numeric ranges
- [ ] Escape special characters
- [ ] Prevent SQL injection
- [ ] Prevent XSS in exports

**Implementation:**
```python
import html
import re
from typing import Any

class InputSanitizer:
    """Sanitize user inputs."""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input."""
        if not value:
            return ""
        
        # Remove control characters
        value = re.sub(r'[\x00-\x1F\x7F]', '', value)
        
        # Strip whitespace
        value = value.strip()
        
        # Limit length
        value = value[:1000]
        
        return value
    
    @staticmethod
    def sanitize_for_excel(value: str) -> str:
        """Sanitize for Excel export (prevent formula injection)."""
        if not value:
            return ""
        
        # Prevent formula injection
        if value.startswith(('=', '+', '-', '@')):
            value = "'" + value
        
        return value
    
    @staticmethod
    def sanitize_company_data(data: dict) -> dict:
        """Sanitize all company data fields."""
        sanitized = {}
        
        string_fields = ['company_name', 'description', 'industry', 'website']
        for field in string_fields:
            if field in data:
                sanitized[field] = InputSanitizer.sanitize_string(data[field])
        
        # Copy other fields as-is
        for key, value in data.items():
            if key not in sanitized:
                sanitized[key] = value
        
        return sanitized
```

---

### Story 16.3: Add Audit Logging
**Priority:** P1 | **Effort:** 1 point

**Description:**
Implement comprehensive audit logging for compliance.

**Acceptance Criteria:**
- [ ] Log all data access
- [ ] Log all modifications
- [ ] Log user actions
- [ ] Immutable audit logs
- [ ] Retention policy

**Implementation:**
```python
import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    """Compliance audit logging."""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_access(self, user: str, resource: str, action: str):
        """Log data access."""
        self._log({
            "timestamp": datetime.now().isoformat(),
            "event_type": "access",
            "user": user,
            "resource": resource,
            "action": action
        })
    
    def log_modification(self, user: str, resource: str, changes: dict):
        """Log data modification."""
        self._log({
            "timestamp": datetime.now().isoformat(),
            "event_type": "modification",
            "user": user,
            "resource": resource,
            "changes": changes
        })
    
    def _log(self, entry: dict):
        """Write audit log entry."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit-{date_str}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

---

## Definition of Done

- [ ] All API keys in environment variables
- [ ] Input sanitization implemented
- [ ] Audit logging working
- [ ] Security checklist passed
- [ ] Documentation updated
