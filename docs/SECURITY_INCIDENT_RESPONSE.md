# Security Incident Response Plan

> **Procedures for responding to security incidents**
> > Last Updated: 2026-03-06
> > Classification: CONFIDENTIAL

---

## Table of Contents

1. [Incident Classification](#incident-classification)
2. [Response Team](#response-team)
3. [Response Procedures](#response-procedures)
4. [Communication Plan](#communication-plan)
5. [Forensics](#forensics)
6. [Recovery](#recovery)
7. [Post-Incident](#post-incident)

---

## Incident Classification

### Severity Levels

#### Critical (SEV 1)
**Definition:** Active breach with data exfiltration or system compromise

**Examples:**
- Unauthorized access to production database
- Ransomware deployment
- Data breach affecting customers
- Active attacker in environment

**Response Time:** Immediate (15 minutes)

#### High (SEV 2)
**Definition:** Potential breach or high-risk vulnerability exploited

**Examples:**
- Unauthorized API access
- Privilege escalation
- Malware detected
- Credential compromise

**Response Time:** 1 hour

#### Medium (SEV 3)
**Definition:** Security event requiring investigation

**Examples:**
- Failed authentication attempts
- Suspicious network traffic
- Policy violation
- Vulnerability disclosure

**Response Time:** 4 hours

#### Low (SEV 4)
**Definition:** Minor security issue

**Examples:**
- Missing security header
- Documentation gap
- Non-critical vulnerability

**Response Time:** 24 hours

---

## Response Team

### Roles and Responsibilities

#### Incident Commander (IC)
- Overall coordination
- Decision making
- Stakeholder communication
- **Primary:** Security Lead
- **Backup:** Platform Lead

#### Technical Lead
- Technical investigation
- Containment actions
- Evidence preservation
- **Primary:** Senior Security Engineer
- **Backup:** Platform Engineer

#### Communications Lead
- Internal communications
- External communications (if needed)
- Status updates
- **Primary:** Engineering Manager
- **Backup:** Incident Commander

#### Legal/Compliance
- Regulatory requirements
- Legal implications
- Disclosure decisions
- **Primary:** Legal Counsel
- **Backup:** Compliance Officer

### Contact Information

| Role | Primary | Backup | Contact Method |
|------|---------|--------|----------------|
| Incident Commander | Security Lead | Platform Lead | PagerDuty |
| Technical Lead | Security Engineer | Senior Dev | Slack #security |
| Communications | Eng Manager | Product Lead | Slack #incidents |
| Legal | Legal Counsel | Compliance | Email/Phone |

---

## Response Procedures

### Phase 1: Detection and Analysis (0-30 min)

#### Detection Sources
- GitHub Security Advisories
- AWS GuardDuty alerts
- Trivy vulnerability scans
- GitLeaks secret detection
- Manual reports
- Customer reports

#### Initial Assessment

```bash
# 1. Acknowledge alert
# Respond in #security channel

# 2. Gather basic information
- What system is affected?
- When did it start?
- What is the potential impact?
- Is it ongoing?

# 3. Classify severity
# Use severity matrix above

# 4. Activate response team
# Page on-call if SEV 1 or 2
```

#### Evidence Preservation

```bash
# Create incident directory
mkdir -p /incidents/$(date +%Y%m%d-%H%M%S)
cd /incidents/$(date +%Y%m%d-%H%M%S)

# Snapshot affected resources
# EBS volumes
aws ec2 create-snapshot --volume-id vol-xxx --description "Incident evidence"

# RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier solstein-production \
  --db-snapshot-identifier incident-$(date +%Y%m%d-%H%M%S)

# Export CloudWatch logs
aws logs create-export-task \
  --task-name incident-$(date +%Y%m%d-%H%M%S) \
  --log-group-name /aws/eks/solstein-production \
  --from $(date -d '2 hours ago' +%s)000 \
  --to $(date +%s)000 \
  --destination solstein-incident-logs
```

---

### Phase 2: Containment (30 min - 2 hours)

#### Immediate Containment

**Isolate affected systems:**
```bash
# Revoke network access
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxx \
  --ip-permissions IpProtocol=all,FromPort=0,ToPort=65535,IpRanges='[{CidrIp=0.0.0.0/0}]'

# Scale down compromised pods
kubectl scale deployment solstein-api --replicas=0 -n solstein

# Block IP addresses
# Add to WAF or security groups
```

**Preserve evidence:**
```bash
# Create memory dump (if possible)
# Snapshot disks
# Save logs
```

**Prevent further damage:**
```bash
# Rotate credentials immediately
aws secretsmanager rotate-secret --secret-id solstein/db-password --force

# Revoke GitHub tokens
gh api -X DELETE /user/keys/KEY_ID

# Disable compromised accounts
aws iam update-access-key --access-key-id AKIA... --status Inactive --user-name user
```

#### Short-term Containment

**Network segmentation:**
```bash
# Enable network policies
kubectl apply -f k8s/security/emergency-network-policy.yaml

# Block egress
kubectl patch networkpolicy default-deny -n solstein -p '{"spec":{"policyTypes":["Egress"]}}'
```

**Access restrictions:**
```bash
# Disable non-essential access
aws iam attach-user-policy \
  --user-name emergency-lockdown \
  --policy-arn arn:aws:iam::aws:policy/AWSDenyAll
```

---

### Phase 3: Eradication (2-6 hours)

#### Remove Threat

**Identify and remove malware:**
```bash
# Scan all systems
# Remove malicious files
# Patch vulnerabilities
```

**Close attack vectors:**
```bash
# Update security groups
# Patch systems
# Update WAF rules
# Enable additional monitoring
```

**Clean compromised accounts:**
```bash
# Force password reset for all users
# Review and revoke OAuth tokens
# Audit IAM policies
```

---

### Phase 4: Recovery (6-24 hours)

#### Restore Systems

**From clean backups:**
```bash
# Follow Disaster Recovery Plan
# Use verified clean backups
# Rebuild from known-good images
```

**Verify integrity:**
```bash
# Run security scans
# Verify checksums
# Test all functionality
```

**Gradual restoration:**
```bash
# Start with isolated environment
# Gradually restore services
# Monitor closely
```

---

### Phase 5: Post-Incident (24+ hours)

#### Documentation

**Create incident timeline:**
```
2026-03-06 10:00:00 - Alert triggered
2026-03-06 10:05:00 - Incident commander notified
2026-03-06 10:15:00 - Response team assembled
...
```

**Preserve evidence:**
- Store all logs
- Save snapshots
- Document findings

#### Analysis

**Root cause analysis:**
- How did attacker gain access?
- What vulnerabilities were exploited?
- What data was accessed?
- How can we prevent recurrence?

#### Improvements

**Update security controls:**
- Add monitoring
- Update policies
- Implement new tools
- Additional training

---

## Communication Plan

### Internal Communication

**SEV 1 (Critical):**
- Immediate: Response team
- 15 min: Engineering leadership
- 30 min: Executive team
- 1 hour: All employees (if customer data affected)

**SEV 2 (High):**
- Immediate: Response team
- 1 hour: Engineering leadership
- 4 hours: Update to all engineers

**SEV 3-4:**
- Standard ticket/process
- Weekly security review

### External Communication

**Customer notification:**
- If PII accessed: Within 72 hours (GDPR)
- If financial data: Within 24 hours
- Use status page for availability issues

**Regulatory notification:**
- Follow legal team guidance
- Document all notifications

**Public disclosure:**
- Coordinate with legal
- Prepare statements
- Monitor social media

### Communication Templates

**Initial Alert:**
```
🚨 SECURITY INCIDENT 🚨

Severity: [SEV 1/2/3/4]
Status: Active/Contained/Resolved
Time: [Timestamp]

Summary: [Brief description]

Impact: [What systems/data affected]

Actions Taken: [What's been done]

Next Update: [When to expect next update]

Incident Commander: [Name]
```

**Status Update:**
```
📊 SECURITY INCIDENT UPDATE

Incident: [ID]
Time: [Current time]
Elapsed: [X hours]

Current Status: [Update]

Actions Taken:
- [Action 1]
- [Action 2]

Next Steps:
- [Step 1]
- [Step 2]

Next Update: [Time]
```

---

## Forensics

### Evidence Collection

**System artifacts:**
- Memory dumps
- Disk images
- Network captures
- Process listings
- File system metadata

**Log sources:**
- CloudTrail logs
- EKS audit logs
- Application logs
- Database logs
- VPC Flow Logs

**Timeline reconstruction:**
```bash
# Collect all relevant logs
aws logs filter-log-events \
  --log-group-name /aws/eks/solstein-production \
  --start-time $(date -d '2 hours ago' +%s)000 \
  --end-time $(date +%s)000 \
  --filter-pattern "ERROR"
```

### Analysis Tools

- **AWS:** GuardDuty, Security Hub, Detective
- **Kubernetes:** Falco, audit2rbac
- **Network:** VPC Flow Logs, Wireshark
- **Memory:** Volatility, Rekall
- **Disk:** Sleuth Kit, Autopsy

### Chain of Custody

1. Document who collected evidence
2. Document when and where
3. Secure storage
4. Access logging
5. Hash verification

---

## Recovery

### System Recovery

Follow the [Disaster Recovery Plan](./DISASTER_RECOVERY.md)

### Additional Security Measures

**Enhanced monitoring:**
```bash
# Enable additional CloudTrail logging
aws cloudtrail update-trail --name solstein-trail --enable-log-file-validation

# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-ids vpc-xxx \
  --resource-type VPC \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs
```

**Additional scanning:**
```bash
# Run comprehensive vulnerability scan
trivy image --severity HIGH,CRITICAL ghcr.io/your-org/solstein:latest

# Run malware scan
clamscan -r /var/lib/docker/
```

---

## Post-Incident

### Incident Report Template

```markdown
# Security Incident Report

## Executive Summary
- Incident ID: INC-2026-001
- Date: 2026-03-06
- Severity: SEV 1
- Status: Resolved

## Timeline
[Detailed timeline]

## Root Cause
[What happened and why]

## Impact Assessment
- Systems affected: [List]
- Data accessed: [Description]
- Users affected: [Count]
- Financial impact: [If any]

## Response Actions
[What was done]

## Lessons Learned
[What went well, what didn't]

## Action Items
- [ ] Item 1 (Owner, Due Date)
- [ ] Item 2 (Owner, Due Date)

## Appendices
- Evidence logs
- Communication records
- Technical details
```

### Retrospective Meeting

**Schedule:** Within 1 week of resolution

**Attendees:**
- Response team
- Affected teams
- Leadership

**Agenda:**
1. Timeline review
2. What went well
3. What could be improved
4. Action items
5. Plan implementation

---

## Appendix A: Quick Reference

### Emergency Commands

```bash
# Lock down environment
kubectl scale deployment solstein-api --replicas=0 -n solstein

# Rotate all secrets
./scripts/emergency-rotate-secrets.sh

# Isolate network
kubectl apply -f k8s/security/emergency-isolation.yaml

# Create evidence snapshot
./scripts/preserve-evidence.sh
```

### Key Contacts

| Role | Contact | Method |
|------|---------|--------|
| Security Lead | security@solstein.app | PagerDuty |
| Platform Lead | platform@solstein.app | Slack |
| AWS Support | - | AWS Console |
| Legal | legal@solstein.app | Email |

### Useful Resources

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [AWS Security Incident Response Guide](https://docs.aws.amazon.com/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)

---

*This plan is maintained by the Security Team. Last updated: 2026-03-06*
*Classification: CONFIDENTIAL - Internal Use Only*
