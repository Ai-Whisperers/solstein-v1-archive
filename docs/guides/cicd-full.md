# Solstein CI/CD Documentation

> **Complete guide for the Solstein CI/CD infrastructure**
> 
> Last Updated: 2026-03-06

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Workflows Reference](#workflows-reference)
4. [Deployment Guide](#deployment-guide)
5. [Operations Runbook](#operations-runbook)
6. [Troubleshooting](#troubleshooting)
7. [Security](#security)
8. [Infrastructure](#infrastructure)

---

## Quick Start

### Prerequisites

- GitHub account with repository access
- AWS CLI configured (for infrastructure)
- kubectl installed (for Kubernetes)
- Helm 3.x installed
- Terraform 1.5+ installed

### Initial Setup

1. **Configure GitHub Secrets:**
   ```bash
   # Required secrets
   gh secret set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT:role/GitHubActions"
   gh secret set AWS_REGION --body "us-east-1"
   gh secret set TEST_ADMIN_EMAIL --body "test@example.com"
   gh secret set TEST_ADMIN_PASSWORD_HASH --body "..."
   gh secret set TEST_SECRET_KEY --body "..."
   gh secret set DB_PASSWORD --body "..."
   gh secret set SLACK_WEBHOOK_URL --body "..."
   ```

2. **Create Terraform State Infrastructure:**
   ```bash
   aws s3 mb s3://solstein-terraform-state
   aws dynamodb create-table \
     --table-name solstein-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

3. **Deploy Infrastructure:**
   ```bash
   cd terraform/environments/staging
   terraform init
   terraform apply
   ```

4. **Deploy Application:**
   ```bash
   # Using Helm
   helm install solstein ./helm/solstein \
     --namespace solstein \
     --create-namespace \
     --values values-staging.yaml
   
   # Or using Kustomize
   kubectl apply -k k8s/overlays/staging
   ```

---

## Architecture Overview

### CI/CD Pipeline Flow

```
Developer pushes code
        │
        ▼
┌─────────────────────────────────────┐
│ 1. Pre-commit Hooks                 │
│    - Linting, formatting, secrets   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 2. CI Workflow                      │
│    - Lint & Format                  │
│    - Type Check                     │
│    - Security Scan                  │
│    - Unit Tests                     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 3. Integration Tests                │
│    - Database integration           │
│    - API integration                │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 4. Build & Push                     │
│    - Docker image build             │
│    - SBOM generation                │
│    - Vulnerability scan             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 5. Deploy to Staging                │
│    - Database migrations            │
│    - Rolling deployment             │
│    - Smoke tests                    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 6. Production Release               │
│    - Manual approval                │
│    - Canary deployment              │
│    - Automated rollback             │
└─────────────────────────────────────┘
```

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     VPC                             │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │              Public Subnets                 │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │   │
│  │  │  │  ALB    │  │  NAT    │  │  Bastion│     │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘     │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │              Private Subnets                │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │   │
│  │  │  │  EKS    │  │  RDS    │  │  Redis  │     │   │   │
│  │  │  │ (Pods)  │  │(Postgres│  │(ElastiCache)  │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘     │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │     S3      │  │     ECR     │  │ CloudWatch  │       │
│  │  (Backups)  │  │  (Images)   │  │  (Logs)     │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflows Reference

### Core CI/CD Workflows

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| `ci.yml` | PR, Push | Lint, test, security scan | ~10 min |
| `integration-tests.yml` | PR, Push | Full integration tests | ~15 min |
| `release.yml` | Tag | Build, SBOM, release | ~20 min |
| `deploy-staging.yml` | Push to develop | Deploy to staging | ~10 min |
| `deploy-production.yml` | Tag | Deploy to production | ~15 min |

### Quality & Security Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `code-quality-guardrails.yml` | PR (Python files) | Code quality checks |
| `pre-commit.yml` | PR | Pre-commit hooks validation |
| `validate-workflows.yml` | PR (workflows) | Workflow syntax validation |
| `benchmarks.yml` | Weekly | Performance regression testing |
| `chaos.yml` | Weekly | Resilience testing |
| `load-testing.yml` | Weekly | Load testing |

### Maintenance Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `db-migrations.yml` | Manual | Database migrations |
| `backup-restore.yml` | Daily, Manual | Database backup/restore |
| `docs.yml` | Push to main | Documentation deployment |

### Workflow Inputs

#### deploy-production.yml
```yaml
version:        # Required, e.g., "v1.0.0"
environment:    # Required, "production" or "production-dr"
```

#### db-migrations.yml
```yaml
environment:    # Required, "staging" or "production"
command:        # Required, "upgrade", "downgrade", "current", "history"
revision:       # Optional, default "head"
```

#### load-testing.yml
```yaml
duration:       # Optional, default "10" (minutes)
users:          # Optional, default "100"
spawn_rate:     # Optional, default "10"
host:           # Optional, default "https://staging.solstein.app"
```

---

## Deployment Guide

### Deploying to Staging

Staging is automatically deployed on every push to the `develop` branch.

**Manual deployment:**
```bash
gh workflow run deploy-staging.yml
```

### Deploying to Production

Production requires a Git tag and manual workflow dispatch:

1. **Create and push a tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **The release workflow will automatically trigger.**

3. **Or manually deploy:**
   ```bash
   gh workflow run deploy-production.yml \
     -f version=v1.0.0 \
     -f environment=production
   ```

### Database Migrations

**Apply migrations:**
```bash
gh workflow run db-migrations.yml \
  -f environment=staging \
  -f command=upgrade \
  -f revision=head
```

**Rollback migrations:**
```bash
gh workflow run db-migrations.yml \
  -f environment=staging \
  -f command=downgrade \
  -f revision=-1
```

**Check current version:**
```bash
gh workflow run db-migrations.yml \
  -f environment=staging \
  -f command=current
```

### Using Helm

**Install/Upgrade:**
```bash
helm upgrade --install solstein ./helm/solstein \
  --namespace solstein \
  --create-namespace \
  --values values-production.yaml \
  --set image.tag=v1.0.0
```

**Rollback:**
```bash
helm rollback solstein 1
```

**Uninstall:**
```bash
helm uninstall solstein --namespace solstein
```

### Using Terraform

**Plan changes:**
```bash
cd terraform/environments/production
terraform plan
```

**Apply changes:**
```bash
terraform apply
```

**Destroy infrastructure:**
```bash
terraform destroy
```

---

## Operations Runbook

### Daily Operations

**Check system health:**
```bash
# Check pods
kubectl get pods -n solstein

# Check services
kubectl get svc -n solstein

# Check ingress
kubectl get ingress -n solstein

# Check HPA
kubectl get hpa -n solstein
```

**View logs:**
```bash
# All pods
kubectl logs -n solstein -l app.kubernetes.io/name=solstein

# Specific pod
kubectl logs -n solstein deployment/solstein-api

# Follow logs
kubectl logs -n solstein -f deployment/solstein-api
```

**Check metrics:**
```bash
# Port forward to Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Open http://localhost:9090
```

### Weekly Operations

**Review failed workflows:**
```bash
gh run list --status failure
```

**Check backup status:**
```bash
aws s3 ls s3://solstein-backups-production/
```

**Review security scans:**
```bash
# Check Trivy results in GitHub Security tab
# Check Dependabot alerts
```

### Monthly Operations

**Rotate secrets:**
```bash
# Update database password
aws secretsmanager rotate-secret --secret-id solstein/db-password

# Update API keys
gh secret set OPENAI_API_KEY --body "new-key"
```

**Review costs:**
```bash
# Check AWS Cost Explorer
# Review GitHub Actions usage
```

**Update dependencies:**
```bash
# Update Python packages
pip list --outdated

# Update GitHub Actions
# Check for new action versions
```

---

## Troubleshooting

### Common Issues

#### Workflow Failures

**Issue:** CI workflow fails on tests
```bash
# Check test logs
gh run view RUN_ID --log

# Run tests locally
pytest tests/ -v
```

**Issue:** Docker build fails
```bash
# Build locally
docker build -t solstein:test .

# Check Dockerfile syntax
docker build --no-cache -t solstein:test .
```

#### Deployment Failures

**Issue:** Pod stuck in Pending
```bash
# Check events
kubectl get events -n solstein --sort-by='.lastTimestamp'

# Check resource quotas
kubectl describe resourcequota -n solstein

# Check node resources
kubectl top nodes
```

**Issue:** Pod CrashLoopBackOff
```bash
# Check logs
kubectl logs -n solstein deployment/solstein-api --previous

# Check events
kubectl describe pod -n solstein -l app.kubernetes.io/name=solstein
```

**Issue:** Database connection failures
```bash
# Test connection
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- psql -h postgres -U postgres

# Check secrets
kubectl get secret -n solstein solstein-secrets -o jsonpath='{.data.database-url}' | base64 -d
```

#### Infrastructure Issues

**Issue:** Terraform state lock
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

**Issue:** EKS node issues
```bash
# Check nodes
kubectl get nodes

# Check node groups
aws eks describe-nodegroup --cluster-name solstein-production --nodegroup-name general
```

### Emergency Procedures

#### Rollback Production Deployment

```bash
# Via Helm
helm rollback solstein 1

# Via kubectl
kubectl rollout undo deployment/solstein-api -n solstein

# Via GitHub Actions
gh workflow run deploy-production.yml \
  -f version=PREVIOUS_VERSION \
  -f environment=production
```

#### Restore Database from Backup

```bash
# List available backups
aws s3 ls s3://solstein-backups-production/ | sort

# Restore specific backup
gh workflow run backup-restore.yml \
  -f action=restore \
  -f environment=production \
  -f backup_file=solstein-production-20260101-030000.sql.gz
```

#### Scale Up for High Traffic

```bash
# Manual scale
kubectl scale deployment solstein-api -n solstein --replicas=10

# Update HPA
kubectl patch hpa solstein-api -n solstein -p '{"spec":{"maxReplicas":20}}'
```

---

## Security

### Security Checklist

- [ ] All secrets stored in GitHub Secrets (not in code)
- [ ] OIDC authentication configured (no long-lived AWS credentials)
- [ ] Branch protection enabled on main branch
- [ ] CODEOWNERS file active
- [ ] Dependabot alerts enabled
- [ ] Security scanning enabled (Trivy, Bandit, Safety)
- [ ] Network policies configured
- [ ] Pod security policies enforced
- [ ] Encryption at rest enabled (RDS, S3, ElastiCache)
- [ ] Encryption in transit enabled

### Secret Rotation Schedule

| Secret Type | Rotation Frequency | Procedure |
|-------------|-------------------|-----------|
| Database passwords | 90 days | Automatic via AWS Secrets Manager |
| API keys | 180 days | Manual rotation |
| GitHub tokens | On demand | Regenerate in GitHub UI |
| TLS certificates | 365 days | Automatic via cert-manager |

### Incident Response

**Security incident detected:**
1. Isolate affected resources
2. Rotate compromised secrets
3. Review audit logs
4. Create incident report
5. Implement preventive measures

---

## Infrastructure

### AWS Resources

| Resource | Purpose | Environment |
|----------|---------|-------------|
| EKS Cluster | Kubernetes orchestration | staging, production |
| RDS PostgreSQL | Primary database | staging, production |
| ElastiCache Redis | Caching layer | staging, production |
| ECR Repository | Container images | shared |
| S3 Bucket | Backups, exports | staging, production |
| Application Load Balancer | Traffic distribution | staging, production |
| Route53 Zone | DNS management | production |

### Kubernetes Resources

| Resource | Namespace | Purpose |
|----------|-----------|---------|
| Deployment/solstein-api | solstein | Main application |
| StatefulSet/postgres | solstein | Database |
| Deployment/redis | solstein | Cache |
| Ingress/solstein-api | solstein | HTTP routing |
| HPA/solstein-api | solstein | Auto-scaling |
| CronJob/postgres-backup | solstein | Automated backups |

### Resource Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| API | 250m | 1000m | 512Mi | 2Gi |
| PostgreSQL | 100m | 500m | 256Mi | 1Gi |
| Redis | 50m | 200m | 128Mi | 256Mi |

---

## Additional Resources

- [OIDC Setup Guide](../OIDC_SETUP.md)
- [Architecture Decision Records](./adr/)
- [API Documentation](https://api.solstein.app/docs)
- [Runbooks](./runbooks/)

---

## Support

For issues or questions:
- **Slack:** #platform-support
- **Email:** platform@solstein.app
- **On-call:** PagerDuty rotation

---

*This documentation is maintained by the Platform Team. Last updated: 2026-03-06*
