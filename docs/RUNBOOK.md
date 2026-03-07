# Solstein Operations Runbook

> **Procedures for common operational tasks**
> > Last Updated: 2026-03-06

---

## Table of Contents

1. [Monitoring & Alerting](#monitoring--alerting)
2. [Incident Response](#incident-response)
3. [Maintenance Procedures](#maintenance-procedures)
4. [Backup & Recovery](#backup--recovery)
5. [Scaling Operations](#scaling-operations)
6. [Security Operations](#security-operations)

---

## Monitoring & Alerting

### Key Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold | Action |
|--------|-------------------|-------------------|--------|
| API Response Time (p95) | > 500ms | > 2000ms | Scale up, investigate |
| Error Rate | > 1% | > 5% | Rollback, investigate |
| CPU Usage | > 70% | > 90% | Scale up |
| Memory Usage | > 80% | > 95% | Scale up, investigate leaks |
| Database Connections | > 80% | > 95% | Check connection pooling |
| Disk Usage | > 80% | > 90% | Clean up, expand storage |

### Dashboards

**Grafana:**
- URL: https://grafana.solstein.app
- Login with SSO

**Key Dashboards:**
- Application Overview
- Database Performance
- Infrastructure Health
- Business Metrics

### Alert Routing

| Alert Severity | Channel | Response Time |
|----------------|---------|---------------|
| P1 (Critical) | PagerDuty + Slack #incidents | 15 minutes |
| P2 (High) | Slack #alerts | 1 hour |
| P3 (Medium) | Slack #notifications | 4 hours |
| P4 (Low) | Email digest | 24 hours |

---

## Incident Response

### Incident Severity Levels

#### SEV 1 - Critical
**Definition:** Complete service outage or data loss

**Examples:**
- Production down
- Database corruption
- Security breach
- Data loss

**Response:**
1. Page on-call engineer immediately
2. Create incident channel: #incident-YYYY-MM-DD-description
3. Notify stakeholders within 15 minutes
4. Work on resolution
5. Post-incident review within 24 hours

#### SEV 2 - High
**Definition:** Major functionality impaired

**Examples:**
- Significant performance degradation
- Partial service outage
- Failed deployments

**Response:**
1. Create incident channel
2. Notify team within 30 minutes
3. Work on resolution
4. Post-incident review within 48 hours

#### SEV 3 - Medium
**Definition:** Minor impact or workarounds available

**Examples:**
- Single feature not working
- Non-critical performance issues
- Failed CI builds

**Response:**
1. Create GitHub issue
2. Fix during business hours
3. Document in weekly review

### Incident Response Checklist

**Immediate (0-15 min):**
- [ ] Acknowledge alert
- [ ] Create incident channel
- [ ] Assess impact
- [ ] Notify stakeholders

**Short-term (15-60 min):**
- [ ] Gather information
- [ ] Attempt quick fix
- [ ] Document actions taken
- [ ] Update stakeholders every 15 min

**Resolution:**
- [ ] Verify fix
- [ ] Monitor for 30 minutes
- [ ] Close incident channel
- [ ] Schedule post-mortem

**Post-Incident:**
- [ ] Write post-mortem
- [ ] Identify root cause
- [ ] Create action items
- [ ] Update runbooks

---

## Maintenance Procedures

### Daily Checks

**Morning (9 AM):**
```bash
# Check overnight alerts
gh run list --status failure --created ">$(date -d '1 day ago' -I)"

# Check system health
kubectl get pods -n solstein
kubectl top nodes

# Review backup status
aws s3 ls s3://solstein-backups-production/ | tail -5
```

**Evening (5 PM):**
```bash
# Check day's deployments
kubectl get deployments -n solstein

# Review resource usage
kubectl top pods -n solstein

# Check for pending alerts
```

### Weekly Maintenance

**Monday:**
- Review failed workflows
- Check security scan results
- Review Dependabot PRs

**Wednesday:**
- Review performance metrics
- Check for resource leaks
- Review logs for errors

**Friday:**
- Weekly backup verification
- Documentation updates
- Knowledge sharing

### Monthly Maintenance

**First Monday:**
- Review and rotate secrets
- Update dependencies
- Review cost reports
- Security audit

**Third Monday:**
- Capacity planning review
- Performance optimization
- Documentation review
- Runbook updates

### Quarterly Maintenance

- Disaster recovery drill
- Security penetration test
- Infrastructure review
- Architecture review
- Team training

---

## Backup & Recovery

### Backup Schedule

| Data | Frequency | Retention | Location |
|------|-----------|-----------|----------|
| Database | Daily at 3 AM | 30 days | S3 |
| Database | Weekly (Sunday) | 90 days | S3 Glacier |
| Application Config | On change | 10 versions | Git |
| Terraform State | Every apply | All versions | S3 with versioning |

### Backup Verification

**Weekly verification:**
```bash
# Download latest backup
aws s3 cp s3://solstein-backups-production/$(aws s3 ls s3://solstein-backups-production/ | sort | tail -1 | awk '{print $4}') /tmp/backup.sql.gz

# Verify integrity
gunzip -t /tmp/backup.sql.gz

# Clean up
rm /tmp/backup.sql.gz
```

### Recovery Procedures

#### Database Recovery

**Point-in-time recovery (within 7 days):**
```bash
# Use AWS RDS point-in-time restore
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier solstein-production \
  --target-db-instance-identifier solstein-production-recovery \
  --restore-time 2026-03-06T10:00:00Z
```

**From backup file:**
```bash
# Download backup
aws s3 cp s3://solstein-backups-production/BACKUP_FILE.sql.gz /tmp/

# Restore to new instance
gunzip -c /tmp/BACKUP_FILE.sql.gz | psql -h NEW_HOST -U postgres -d solstein
```

#### Kubernetes Recovery

**Restore from Helm:**
```bash
# List releases
helm list -n solstein

# Rollback to previous version
helm rollback solstein 1
```

**Restore from Kustomize:**
```bash
# Reapply configuration
kubectl apply -k k8s/overlays/production
```

#### Complete Environment Recovery

1. **Restore Terraform state:**
   ```bash
   cd terraform/environments/production
   terraform init
   terraform plan  # Verify no changes needed
   ```

2. **Restore infrastructure:**
   ```bash
   terraform apply
   ```

3. **Restore application:**
   ```bash
   helm upgrade --install solstein ./helm/solstein \
     --namespace solstein \
     --values values-production.yaml
   ```

4. **Restore database:**
   ```bash
   # Follow database recovery procedure
   ```

---

## Scaling Operations

### Horizontal Scaling

**Manual scale:**
```bash
# Scale deployment
kubectl scale deployment solstein-api -n solstein --replicas=10

# Verify
kubectl get pods -n solstein
```

**Update HPA:**
```bash
# Edit HPA
kubectl edit hpa solstein-api -n solstein

# Or patch
kubectl patch hpa solstein-api -n solstein -p '{"spec":{"maxReplicas":20}}'
```

### Vertical Scaling

**Update resource limits:**
```bash
# Edit deployment
kubectl edit deployment solstein-api -n solstein

# Or via Helm
helm upgrade solstein ./helm/solstein \
  --set resources.limits.cpu=2000m \
  --set resources.limits.memory=4Gi
```

### Database Scaling

**Scale RDS instance:**
```bash
aws rds modify-db-instance \
  --db-instance-identifier solstein-production \
  --db-instance-class db.r5.xlarge \
  --apply-immediately
```

**Add read replica:**
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier solstein-production-replica \
  --source-db-instance-identifier solstein-production
```

### Cache Scaling

**Scale ElastiCache:**
```bash
aws elasticache modify-cache-cluster \
  --cache-cluster-id solstein-production \
  --cache-node-type cache.r5.large \
  --apply-immediately
```

---

## Security Operations

### Security Monitoring

**Daily:**
- Review security scan results
- Check for new CVEs
- Review access logs

**Weekly:**
- Review AWS CloudTrail logs
- Check GitHub security alerts
- Review firewall logs

**Monthly:**
- Full security audit
- Penetration test review
- Compliance check

### Vulnerability Management

**Critical vulnerabilities:**
1. Assess impact immediately
2. Create patch plan
3. Test in staging
4. Deploy to production within 24 hours

**High vulnerabilities:**
1. Assess within 24 hours
2. Schedule patch within 1 week

**Medium/Low vulnerabilities:**
1. Assess during sprint planning
2. Include in next release

### Access Control

**Grant access:**
```bash
# AWS IAM
aws iam add-user-to-group --user-name USER --group-name solstein-developers

# Kubernetes
kubectl create rolebinding USER-binding \
  --role=developer \
  --user=USER \
  --namespace=solstein
```

**Revoke access:**
```bash
# AWS IAM
aws iam remove-user-from-group --user-name USER --group-name solstein-developers

# Kubernetes
kubectl delete rolebinding USER-binding -n solstein
```

### Incident Response

**Security incident detected:**
1. **Immediate (0-15 min):**
   - Isolate affected systems
   - Preserve evidence
   - Notify security team

2. **Short-term (15-60 min):**
   - Assess scope
   - Identify root cause
   - Begin containment

3. **Containment:**
   - Block malicious traffic
   - Rotate compromised credentials
   - Patch vulnerabilities

4. **Recovery:**
   - Restore from clean backups
   - Verify system integrity
   - Resume operations

5. **Post-Incident:**
   - Document timeline
   - Identify lessons learned
   - Update security controls

---

## Emergency Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| On-call Engineer | Rotation | PagerDuty | 15 min |
| Platform Lead | Name | Slack/Email | 30 min |
| Security Lead | Name | Slack/Email | Immediate |
| Engineering Manager | Name | Slack/Email | 1 hour |

---

*This runbook is maintained by the Platform Team. Last updated: 2026-03-06*
