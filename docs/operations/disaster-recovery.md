# Disaster Recovery Plan

> **Procedures for recovering from catastrophic failures**
> > Last Updated: 2026-03-06
> > Review Frequency: Quarterly

---

## Table of Contents

1. [Overview](#overview)
2. [Recovery Objectives](#recovery-objectives)
3. [Disaster Scenarios](#disaster-scenarios)
4. [Recovery Procedures](#recovery-procedures)
5. [Testing](#testing)
6. [Contact Information](#contact-information)

---

## Overview

This document outlines procedures for recovering Solstein infrastructure and data in the event of a catastrophic failure.

### Scope

- AWS infrastructure (EKS, RDS, ElastiCache, S3)
- Application data (PostgreSQL, Redis)
- Application configuration
- CI/CD pipelines

### Assumptions

- GitHub repository remains accessible
- Terraform state is recoverable
- At least one backup exists
- Team has AWS access

---

## Recovery Objectives

### Recovery Time Objective (RTO)

| Component | RTO | Priority |
|-----------|-----|----------|
| Production API | 1 hour | Critical |
| Database | 2 hours | Critical |
| Cache | 30 minutes | High |
| Staging | 4 hours | Medium |
| CI/CD | 2 hours | High |

### Recovery Point Objective (RPO)

| Component | RPO | Backup Frequency |
|-----------|-----|------------------|
| Database | 1 hour | Hourly (transaction logs) |
| Application Code | 0 | Git repository |
| Configuration | 0 | Git repository |
| User Data | 24 hours | Daily backups |

---

## Disaster Scenarios

### Scenario 1: Complete AWS Region Failure

**Impact:** Entire production environment unavailable

**Detection:**
- Monitoring alerts
- User reports
- Health checks failing

**Response:**
1. Activate DR region
2. Restore from cross-region backups
3. Update DNS
4. Verify functionality

### Scenario 2: Database Corruption

**Impact:** Data integrity compromised

**Detection:**
- Database errors
- Data inconsistencies
- Failed queries

**Response:**
1. Stop writes to database
2. Assess corruption extent
3. Restore from last known good backup
4. Replay transaction logs
5. Verify data integrity

### Scenario 3: Kubernetes Cluster Failure

**Impact:** Application unavailable

**Detection:**
- Node failures
- Control plane issues
- Network partitioning

**Response:**
1. Assess cluster health
2. Attempt repair if minor
3. Create new cluster if necessary
4. Redeploy application

### Scenario 4: Security Breach

**Impact:** Potential data exposure

**Detection:**
- Security alerts
- Unauthorized access
- Data exfiltration

**Response:**
1. Isolate affected systems
2. Rotate all credentials
3. Assess breach scope
4. Restore from clean backups
5. Security audit

---

## Recovery Procedures

### Procedure 1: Complete Environment Recovery

#### Step 1: Assess the Situation

```bash
# Check AWS service health
aws health describe-events

# Check current infrastructure status
aws eks describe-cluster --name solstein-production
aws rds describe-db-instances --db-instance-identifier solstein-production
```

#### Step 2: Prepare Recovery Environment

```bash
# Switch to DR region (if applicable)
export AWS_REGION=us-west-2  # DR region

# Verify Terraform state
aws s3 ls s3://solstein-terraform-state/
```

#### Step 3: Restore Infrastructure

```bash
# Clone repository
git clone https://github.com/your-org/solstein.git
cd solstein

# Initialize Terraform
cd terraform/environments/production
terraform init

# Plan recovery
terraform plan

# Apply (creates new infrastructure)
terraform apply
```

#### Step 4: Restore Database

```bash
# List available backups
aws s3 ls s3://solstein-backups-production/ | sort

# Download latest backup
aws s3 cp s3://solstein-backups-production/BACKUP_FILE.sql.gz /tmp/

# Restore to new RDS instance
gunzip -c /tmp/BACKUP_FILE.sql.gz | \
  psql -h NEW_RDS_ENDPOINT -U postgres -d solstein
```

#### Step 5: Deploy Application

```bash
# Update kubeconfig
aws eks update-kubeconfig --name solstein-production --region us-west-2

# Deploy with Helm
helm upgrade --install solstein ./helm/solstein \
  --namespace solstein \
  --create-namespace \
  --values values-production.yaml \
  --set image.tag=LAST_KNOWN_GOOD_TAG

# Verify deployment
kubectl get pods -n solstein
kubectl get svc -n solstein
```

#### Step 6: Verify Recovery

```bash
# Health check
curl -f https://solstein.app/health

# Database connectivity
kubectl exec -it deployment/solstein-api -n solstein -- \
  python -c "from solstein.infrastructure.database import engine; print('DB OK')"

# Run smoke tests
pytest tests/smoke/ -v
```

#### Step 7: Update DNS (if region changed)

```bash
# Update Route53 records
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONE_ID \
  --change-batch file://dns-update.json
```

#### Step 8: Monitor and Stabilize

- Watch logs for errors
- Monitor metrics
- Verify all features work
- Keep old environment running until verified

---

### Procedure 2: Database Point-in-Time Recovery

#### When to Use

- Database corruption
- Accidental data deletion
- Ransomware attack

#### Steps

```bash
# 1. Identify recovery point
# Find the last known good state

# 2. Create point-in-time restore
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier solstein-production \
  --target-db-instance-identifier solstein-production-recovery \
  --restore-time "2026-03-06T10:00:00Z"

# 3. Wait for restore to complete
aws rds wait db-instance-available \
  --db-instance-identifier solstein-production-recovery

# 4. Update application to use recovered database
kubectl set env deployment/solstein-api \
  DATABASE__URL="postgresql://postgres:PASSWORD@RECOVERY_ENDPOINT:5432/solstein" \
  -n solstein

# 5. Verify data integrity
# Run data validation scripts

# 6. Once verified, rename instances
aws rds modify-db-instance \
  --db-instance-identifier solstein-production \
  --new-db-instance-identifier solstein-production-old \
  --apply-immediately

aws rds modify-db-instance \
  --db-instance-identifier solstein-production-recovery \
  --new-db-instance-identifier solstein-production \
  --apply-immediately

# 7. Clean up old instance (after verification)
aws rds delete-db-instance \
  --db-instance-identifier solstein-production-old \
  --skip-final-snapshot
```

---

### Procedure 3: Kubernetes Cluster Recovery

#### Steps

```bash
# 1. Check if cluster is recoverable
aws eks describe-cluster --name solstein-production

# 2. If not recoverable, create new cluster
# Update Terraform to create new cluster
cd terraform/environments/production

# Edit main.tf to change cluster name or create new

# Apply changes
terraform apply -target=module.eks

# 3. Update kubeconfig
aws eks update-kubeconfig --name solstein-production-new

# 4. Redeploy application
kubectl apply -k k8s/overlays/production

# Or use Helm
helm upgrade --install solstein ./helm/solstein \
  --namespace solstein \
  --create-namespace \
  --values values-production.yaml

# 5. Verify
kubectl get all -n solstein
```

---

### Procedure 4: Security Incident Recovery

#### Immediate Actions (0-15 minutes)

1. **Isolate affected systems:**
   ```bash
   # Revoke security group rules
   aws ec2 revoke-security-group-ingress \
     --group-id sg-xxx \
     --protocol all \
     --source-group sg-yyy
   
   # Scale down compromised pods
   kubectl scale deployment solstein-api --replicas=0 -n solstein
   ```

2. **Preserve evidence:**
   ```bash
   # Snapshot volumes
   aws ec2 create-snapshot \
     --volume-id vol-xxx \
     --description "Incident evidence"
   
   # Export logs
   aws logs create-export-task \
     --log-group-name /aws/eks/solstein-production \
     --from $(date -d '1 hour ago' +%s)000 \
     --to $(date +%s)000 \
     --destination solstein-incident-logs
   ```

#### Short-term Actions (15-60 minutes)

3. **Rotate all credentials:**
   ```bash
   # Database password
   aws secretsmanager rotate-secret --secret-id solstein/db-password
   
   # API keys (manual process)
   # Update in GitHub Secrets
   ```

4. **Restore from clean backups:**
   ```bash
   # Follow Procedure 1: Complete Environment Recovery
   # Use backups from before incident
   ```

#### Recovery Actions (1-4 hours)

5. **Security audit:**
   - Review access logs
   - Identify attack vector
   - Patch vulnerabilities

6. **Verification:**
   - Run security scans
   - Verify no backdoors
   - Test all functionality

---

## Testing

### Quarterly DR Drill

**Schedule:** First Monday of each quarter

**Duration:** 4 hours

**Participants:**
- Platform Team Lead
- On-call Engineer
- Database Administrator
- Security Engineer

**Test Scenarios:**
1. Database point-in-time recovery
2. Complete environment rebuild
3. Security incident response
4. Cross-region failover

**Success Criteria:**
- RTO met for all critical components
- No data loss (within RPO)
- All tests pass
- Documentation updated

### Testing Procedure

```bash
# 1. Announce test
# Post in #incidents channel

# 2. Execute test scenario
# Follow recovery procedures

# 3. Document results
# Time to recovery
# Issues encountered
# Lessons learned

# 4. Update procedures
# Based on findings

# 5. Retrospective
# Schedule within 1 week
```

---

## Contact Information

### Emergency Contacts

| Role | Name | Phone | Email | Escalation |
|------|------|-------|-------|------------|
| Incident Commander | On-call rotation | PagerDuty | - | 15 min |
| Platform Lead | Name | +1-xxx-xxx-xxxx | lead@solstein.app | 30 min |
| Database Admin | Name | +1-xxx-xxx-xxxx | dba@solstein.app | 30 min |
| Security Lead | Name | +1-xxx-xxx-xxxx | security@solstein.app | Immediate |
| Engineering VP | Name | +1-xxx-xxx-xxxx | vp@solstein.app | 1 hour |

### External Contacts

| Service | Contact | Method |
|---------|---------|--------|
| AWS Support | Business Support | AWS Console |
| GitHub Support | Enterprise Support | support.github.com |
| PagerDuty | - | pagerduty.com |

### Communication Channels

- **Primary:** #incidents (Slack)
- **Bridge:** Zoom meeting (link in runbook)
- **Status Page:** status.solstein.app
- **External:** @solsteinstatus (Twitter)

---

## Appendix

### A. Backup Locations

| Data | Primary | DR Region | Retention |
|------|---------|-----------|-----------|
| Database | us-east-1 | us-west-2 | 30 days |
| Terraform State | us-east-1 | us-west-2 | All versions |
| Application Images | ECR | ECR (DR) | 30 images |
| Documents | S3 | S3 (DR) | 90 days |

### B. Infrastructure Inventory

**Production:**
- EKS Cluster: solstein-production
- RDS Instance: solstein-production
- ElastiCache: solstein-production
- S3 Buckets: solstein-production-*, solstein-backups-production

**DR Region:**
- EKS Cluster: solstein-dr
- (Other resources created on-demand)

### C. Recovery Checklist

**Pre-Recovery:**
- [ ] Incident declared
- [ ] Team assembled
- [ ] Stakeholders notified
- [ ] Recovery procedure selected

**During Recovery:**
- [ ] Infrastructure restored
- [ ] Database restored
- [ ] Application deployed
- [ ] Configuration applied
- [ ] Tests passing

**Post-Recovery:**
- [ ] DNS updated (if needed)
- [ ] Monitoring verified
- [ ] Users notified
- [ ] Documentation updated
- [ ] Retrospective scheduled

---

*This plan is maintained by the Platform Team. Last updated: 2026-03-06*
*Next review: 2026-06-06*
