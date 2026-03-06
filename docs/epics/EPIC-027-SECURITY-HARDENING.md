# Epic: Security Hardening & Compliance Audit (EPIC-027)

## Overview
Conduct comprehensive security audit, implement hardening measures, and achieve compliance certifications. Protect sensitive competitive intelligence data and ensure the platform meets industry security standards.

## Background
Current security posture:
- Basic authentication implemented
- No formal security audit conducted
- Compliance status unknown
- Secrets management informal
- No penetration testing history
- Vulnerability scanning not automated

## Goals
- [ ] Pass comprehensive security audit
- [ ] SOC 2 Type II compliance
- [ ] GDPR compliance for EU customers
- [ ] Zero critical/high vulnerabilities
- [ ] Automated security scanning in CI/CD
- [ ] Incident response plan tested

## Compliance Standards
- **SOC 2 Type II:** Security, Availability, Confidentiality
- **GDPR:** Data protection for EU users
- **ISO 27001:** Information security management
- **OWASP Top 10:** Web application security

---

## Stories

### Story 1: Comprehensive Security Audit
**Points:** 13
**Priority:** P0

Conduct full security assessment.

**Audit Components:**

**1. Automated Vulnerability Scanning:**
```bash
# Dependency scanning
pip-audit --format=json --output=vulnerability-report.json

# Static analysis
bandit -r src/ -f json -o bandit-report.json

# Secrets scanning
git-secrets --scan

trufflehog filesystem --directory=.
```

**2. Manual Code Review:**
- Authentication/authorization flows
- Data validation and sanitization
- Cryptographic implementations
- Session management
- Error handling (information disclosure)

**3. Infrastructure Review:**
- Cloud security configuration (AWS/GCP/Azure)
- Network security groups
- Database access controls
- Encryption at rest and in transit

**4. Third-Party Assessment:**
- Hire external penetration testing firm
- OWASP ZAP automated scan
- Burp Suite professional assessment

**Deliverables:**
```markdown
# Security Audit Report

## Executive Summary
- Critical: 0
- High: 3
- Medium: 12
- Low: 25

## Critical Findings
1. [ ] Database credentials in logs (HIGH)
2. [ ] Missing rate limiting on auth endpoints (HIGH)
3. [ ] XSS vulnerability in report export (HIGH)

## Remediation Plan
[Detailed plan with timelines]
```

---

### Story 2: Secrets Management Overhaul
**Points:** 5
**Priority:** P0

Implement enterprise secrets management.

**Current State:** Environment variables, some hardcoded

**Target State:** HashiCorp Vault

**Implementation:**
```python
from solstein.security.secrets import get_secret

# Before
api_key = os.getenv("API_KEY")  # Vulnerable to exposure

# After
api_key = await get_secret("llm/openai/api_key")
# - Automatic rotation
# - Audit logging
# - Access control
# - No plaintext in environment
```

**Vault Configuration:**
```hcl
# Vault policy
path "secret/data/solstein/*" {
  capabilities = ["read"]
}

path "secret/data/solsten/production/*" {
  capabilities = ["read"]
  allowed_parameters = {
    "environment" = ["production"]
  }
}
```

**Secret Rotation:**
- Automatic rotation every 90 days
- API keys rotated monthly
- Database credentials rotated quarterly
- Emergency rotation capability

**Tasks:**
- [ ] Deploy HashiCorp Vault
- [ ] Migrate all secrets
- [ ] Implement rotation automation
- [ ] Audit logging
- [ ] Access control policies

---

### Story 3: Authentication & Authorization Hardening
**Points:** 8
**Priority:** P0

Strengthen auth mechanisms.

**Multi-Factor Authentication (MFA):**
```python
from solstein.security.auth import require_mfa

@router.post("/admin/critical-action")
@require_mfa
async def critical_action():
    # Requires MFA code in addition to API key
    pass
```

**Role-Based Access Control (RBAC):**
```python
class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API = "api"

class Permission(str, Enum):
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    RESEARCH_RUN = "research:run"
    EXPORT_CREATE = "export:create"
    ADMIN_ACCESS = "admin:access"

ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.ALL],
    Role.ANALYST: [
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.RESEARCH_RUN,
        Permission.EXPORT_CREATE
    ],
    Role.VIEWER: [Permission.COMPANY_READ],
    Role.API: [Permission.COMPANY_READ, Permission.EXPORT_CREATE]
}

@router.get("/companies/{id}")
@require_permission(Permission.COMPANY_READ)
async def get_company(id: str, user: User = Depends(get_current_user)):
    pass
```

**Session Security:**
- Short-lived JWT tokens (15 min)
- Refresh token rotation
- Secure cookie settings (HttpOnly, Secure, SameSite)
- Session invalidation on logout

**Password Policy (for admin UI):**
- Minimum 12 characters
- Complexity requirements
- Breached password detection (HaveIBeenPwned API)
- Account lockout after 5 failed attempts

---

### Story 4: Data Protection & Encryption
**Points:** 8
**Priority:** P0

Implement comprehensive data protection.

**Encryption at Rest:**
```python
# Database encryption
# PostgreSQL: Transparent Data Encryption (TDE)

# Application-level encryption for PII
from cryptography.fernet import Fernet

class EncryptedField:
    """Automatically encrypt/decrypt sensitive fields."""
    
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> bytes:
        return self.cipher.encrypt(value.encode())
    
    def decrypt(self, value: bytes) -> str:
        return self.cipher.decrypt(value).decode()

# Usage
class Company(BaseModel):
    name: str  # Plaintext
    revenue: float  # Plaintext
    _contact_email: EncryptedField  # Encrypted
```

**Encryption in Transit:**
- TLS 1.3 minimum for all connections
- Certificate pinning for mobile clients
- HSTS headers
- Secure WebSocket (WSS)

**Data Classification:**
```python
class DataClassification(str, Enum):
    PUBLIC = "public"           # No restriction
    INTERNAL = "internal"       # Employees only
    CONFIDENTIAL = "confidential"  # Need-to-know
    RESTRICTED = "restricted"   # Highest protection

@router.get("/companies/{id}")
async def get_company(id: str) -> Company:
    company = await fetch_company(id)
    
    # Log access to confidential data
    if company.classification >= DataClassification.CONFIDENTIAL:
        audit.log(
            action="access",
            resource="company",
            resource_id=id,
            classification=company.classification,
            user=get_current_user()
        )
    
    return company
```

**Data Retention:**
- Automatic deletion after retention period
- GDPR right to erasure (forget me)
- Data export capability

---

### Story 5: Input Validation & Sanitization
**Points:** 5
**Priority:** P0

Prevent injection attacks and malformed data.

**Comprehensive Validation:**
```python
from pydantic import BaseModel, Field, validator
import bleach

class CompanyInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=5000)
    website: str = Field(..., regex=r'^https?://')
    
    @validator('description')
    def sanitize_description(cls, v):
        # Remove potentially dangerous HTML
        return bleach.clean(v, tags=[], strip=True)
    
    @validator('name')
    def validate_name(cls, v):
        # Prevent injection attempts
        if any(char in v for char in ['<', '>', '{', '}', '$']):
            raise ValueError("Invalid characters in name")
        return v.strip()

# SQL Injection Prevention
# Use parameterized queries (ALWAYS!)
await db.fetch(
    "SELECT * FROM companies WHERE id = $1",  # Safe
    company_id
)

# NEVER:
# await db.fetch(f"SELECT * FROM companies WHERE id = '{company_id}'")  # DANGEROUS!
```

**File Upload Security:**
```python
ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.csv', '.json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file: UploadFile) -> None:
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type {ext} not allowed")
    
    # Check size
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("File too large")
    
    # Check file type (magic numbers)
    actual_type = magic.from_buffer(content, mime=True)
    if actual_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("File content doesn't match extension")
    
    # Scan for malware (ClamAV)
    if scan_for_viruses(content):
        raise ValidationError("Malware detected")
```

---

### Story 6: Security Scanning in CI/CD
**Points:** 5
**Priority:** P0

Automated security checks in deployment pipeline.

**GitHub Actions Workflow:**
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Dependency scanning
      - name: Run pip-audit
        uses: pypa/gh-action-pip-audit@v1.0.0
        with:
          inputs: requirements.txt
          
      # Static analysis
      - name: Run Bandit
        uses: PyCQA/bandit@main
        with:
          args: "-r src/ -f json -o bandit-report.json"
          
      # Secrets scanning
      - name: Secret Detection
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          
      # Container scanning
      - name: Scan Docker image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: solstein:latest
          format: sarif
          output: trivy-results.sarif
          
      # SAST
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**Security Gates:**
```yaml
- name: Security Gate
  run: |
    # Fail if high/critical vulnerabilities found
    if [ $(jq '.vulnerabilities | map(select(.severity == "HIGH" or .severity == "CRITICAL")) | length' audit-report.json) -gt 0 ]; then
      echo "❌ High/Critical vulnerabilities found!"
      exit 1
    fi
```

---

### Story 7: GDPR Compliance Implementation
**Points:** 8
**Priority:** P1

Full GDPR compliance for EU customers.

**Requirements:**

**1. Lawful Basis for Processing:**
```python
class ProcessingBasis(str, Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"

@router.post("/companies")
async def create_company(
    data: CompanyInput,
    basis: ProcessingBasis = ProcessingBasis.LEGITIMATE_INTEREST
):
    # Log legal basis
    await audit.log(
        action="data_processing",
        basis=basis,
        data_categories=["company_data", "financial_data"]
    )
```

**2. Right to Access:**
```python
@router.get("/gdpr/export")
async def export_user_data(user_id: str) -> DataExport:
    """Export all data for a user (GDPR Article 15)."""
    data = await gather_all_user_data(user_id)
    return DataExport(
        user_id=user_id,
        export_date=datetime.utcnow(),
        data=data,
        format="json"
    )
```

**3. Right to Erasure ("Right to be Forgotten"):**
```python
@router.delete("/gdpr/erase")
async def erase_user_data(user_id: str):
    """Delete all user data (GDPR Article 17)."""
    # Anonymize rather than delete for referential integrity
    await anonymize_company_data(user_id)
    await delete_user_account(user_id);
    
    await audit.log(
        action="data_erasure",
        user_id=user_id,
        timestamp=datetime.utcnow()
    )
```

**4. Data Processing Agreement (DPA):**
- Standard contractual clauses
- Subprocessor list
- Data transfer mechanisms

**5. Privacy Policy:**
- Clear data usage explanation
- Cookie consent
- Third-party sharing disclosure

---

### Story 8: Incident Response Plan
**Points:** 5
**Priority:** P1

Create and test incident response procedures.

**Incident Response Plan:**
```markdown
# Security Incident Response Plan

## Severity Levels

### Critical (P0)
- Data breach
- Ransomware
- Complete service outage
- **Response:** Immediate (15 min)

### High (P1)
- Unauthorized access
- Malware detection
- Major vulnerability
- **Response:** Within 1 hour

### Medium (P2)
- Minor vulnerability
- Suspicious activity
- **Response:** Within 4 hours

## Response Procedures

### 1. Detection
- Automated alerts
- User reports
- External notification

### 2. Containment
- Isolate affected systems
- Preserve evidence
- Activate incident team

### 3. Eradication
- Remove threat
- Patch vulnerabilities
- Clean compromised systems

### 4. Recovery
- Restore from backups
- Verify system integrity
- Resume services

### 5. Post-Incident
- Root cause analysis
- Lessons learned
- Update procedures
- Regulatory notification (if required)
```

**Incident Response Team:**
- Incident Commander
- Security Lead
- Communications Lead
- Technical Lead
- Legal/Compliance

**Communication Templates:**
```markdown
## Customer Notification Template

Subject: Security Incident Notification

Dear Customer,

We are writing to inform you of a security incident that may have affected your data...

[Details]
[Impact]
[Actions taken]
[Recommendations]

We sincerely apologize for any inconvenience.

Solstein Security Team
```

**Tabletop Exercises:**
- Quarterly incident response drills
- Simulate different attack scenarios
- Measure response times
- Update procedures based on learnings

---

## Security Checklist

### Development
- [ ] Secure coding training
- [ ] Code review requirements
- [ ] Pre-commit security hooks
- [ ] Dependency scanning

### Infrastructure
- [ ] Network segmentation
- [ ] VPC configuration
- [ ] WAF (Web Application Firewall)
- [ ] DDoS protection

### Operations
- [ ] Log retention (1 year)
- [ ] Backup encryption
- [ ] Disaster recovery plan
- [ ] Access log review

### Compliance
- [ ] SOC 2 audit
- [ ] GDPR compliance
- [ ] Penetration test (annual)
- [ ] Vulnerability scan (quarterly)

---

## Definition of Done
- [ ] Security audit passed
- [ ] Zero critical vulnerabilities
- [ ] SOC 2 Type II initiated
- [ ] GDPR compliance achieved
- [ ] Incident response tested
- [ ] Team security trained

## Estimated Effort
- **Total Points:** 57
- **Duration:** 10-12 weeks
- **Team:** 1 security engineer + 1 developer

## Dependencies
- EPIC-016 (Security) - Builds on existing work
- EPIC-018 (Observability) - For security monitoring

---

*Created: 2026-03-06*  
*Target Release: Q4 2026*
