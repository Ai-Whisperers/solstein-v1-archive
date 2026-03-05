# Databricks on AWS Deployment Strategy

> **Document Version**: 1.0
> **Last Updated**: 2026-03-05
> **Applies to**: Solstein AI Platform

## Overview

This document outlines the comprehensive deployment strategy for running LangChain-based competitive intelligence workflows on Databricks using AWS infrastructure. The solution supports three environments: **development**, **staging**, and **production**.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud Infrastructure                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Dev VPC       │    │  Staging VPC    │    │   Prod VPC      │         │
│  │   10.0.0.0/16   │    │  10.1.0.0/16    │    │  10.2.0.0/16    │         │
│  │                 │    │                 │    │                 │         │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │         │
│  │ │ Databricks  │ │    │ │ Databricks  │ │    │ │ Databricks  │ │         │
│  │ │ Workspace   │ │    │ │ Workspace   │ │    │ │ Workspace   │ │         │
│  │ │             │ │    │ │             │ │    │ │             │ │         │
│  │ │ • Single    │ │    │ │ • Auto-scale│ │    │ │ • HA Cluster│ │         │
│  │ │   Node      │ │    │ │ • Small     │ │    │ │ • Multi-AZ  │ │         │
│  │ │ • Spot      │ │    │ │   Cluster   │ │    │ │ • Reserved  │ │         │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │         │
│  │                 │    │                 │    │                 │         │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │         │
│  │ │ S3 Data     │ │    │ │ S3 Data     │ │    │ │ S3 Data     │ │         │
│  │ │ Bucket      │ │    │ │ Bucket      │ │    │ │ Bucket      │ │         │
│  │ │ (encrypted) │ │    │ │ (encrypted) │ │    │ │ (encrypted) │ │         │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Shared Infrastructure                            │   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ CloudWatch  │  │ Secrets     │  │ IAM Roles   │  │ PrivateLink│  │   │
│  │  │ Monitoring  │  │ Manager     │  │ & Policies  │  │ Endpoints  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Environment Strategy

### Development Environment

| Component | Configuration |
|-----------|--------------|
| **Cluster Type** | Single-node (driver only) |
| **Instance** | r5.large (spot) |
| **Auto-terminate** | 30 minutes idle |
| **Cost optimization** | 100% spot instances |
| **Access** | All engineers |
| **Data** | Synthetic/sample data |

### Staging Environment

| Component | Configuration |
|-----------|--------------|
| **Cluster Type** | Standard with auto-scaling |
| **Workers** | 2-4 (r5.xlarge spot) |
| **Auto-terminate** | 60 minutes idle |
| **Cost optimization** | 80% spot, 20% on-demand |
| **Access** | Approved developers |
| **Data** | Anonymized production data |

### Production Environment

| Component | Configuration |
|-----------|--------------|
| **Cluster Type** | High Availability |
| **Workers** | 4-8 (r5.2xlarge on-demand) |
| **Auto-terminate** | Never (always-on) |
| **Cost optimization** | Reserved instances |
| **Access** | On-call rotation only |
| **Data** | Full production data |
| **SLA** | 99.9% uptime |

## Infrastructure as Code

All infrastructure is managed using **Terraform** with the following structure:

```
infrastructure/terraform/aws-databricks/
├── main.tf              # Root module
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── backend.tf           # State management
├── providers.tf         # Provider configuration
├── databricks.tf        # Workspace & clusters
├── networking.tf        # VPC, subnets, security
├── iam.tf              # Roles and policies
├── storage.tf          # S3 buckets
├── monitoring.tf       # CloudWatch & alerts
├── modules/
│   ├── vpc/            # VPC module
│   ├── workspace/      # Databricks workspace
│   └── monitoring/     # CloudWatch dashboard
└── environments/
    ├── dev/
    │   └── terraform.tfvars
    ├── staging/
    │   └── terraform.tfvars
    └── prod/
        └── terraform.tfvars
```

## Deployment Pipeline

### CI/CD Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   PR     │───▶│   Lint   │───▶│   Test   │───▶│  Build   │───▶│  Deploy  │
│ Created  │    │ & Format │    │ & Coverage│   │ Package  │    │  to Dev  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                                       │
                              ┌────────────────────────────────────────┘
                              ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Tag    │───▶│   Prod   │───▶│  Monitor │    │  Merge   │───▶│  Deploy  │
│  Push    │    │ Approval │    │ & Alert  │◀───│  to Main │    │  to Stg  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### GitHub Actions Workflows

1. **Quality Gates** (on every PR):
   - Black formatting check
   - Ruff linting
   - MyPy type checking
   - Pytest with coverage (>80%)
   - Bandit security scan
   - pip-audit dependency check

2. **Dev Deployment** (on PR to develop):
   - Validate Databricks bundle
   - Deploy to dev workspace
   - Run smoke tests
   - Post PR comment with results

3. **Staging Deployment** (on merge to main):
   - Full test suite
   - Deploy to staging workspace
   - Run integration tests
   - Notify on Slack

4. **Production Deployment** (on tag push):
   - Require 2 approvals
   - Deploy to production workspace
   - Run health checks
   - Enable automatic rollback on failure

## Security Architecture

### Data Protection

| Layer | Implementation |
|-------|---------------|
| **Encryption at Rest** | SSE-S3 with KMS (CMK) |
| **Encryption in Transit** | TLS 1.3 only |
| **Key Management** | AWS KMS with rotation |
| **Secret Storage** | AWS Secrets Manager |
| **Network Isolation** | VPC with PrivateLink |

### Access Control

```
┌─────────────────────────────────────────────────────────────────┐
│                     Identity & Access                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  GitHub     │    │  AWS IAM    │    │ Databricks  │         │
│  │  OIDC       │───▶│  Roles      │───▶│  SCIM       │         │
│  │  (No keys)  │    │  (Least     │    │  (Synced)   │         │
│  │             │    │  privilege) │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│  Access Levels:                                                  │
│  • Read: View notebooks, query data                             │
│  • Write: Create/edit notebooks, run jobs                       │
│  • Admin: Manage clusters, users, permissions                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

### Metrics Collected

| Category | Metrics | Destination |
|----------|---------|-------------|
| **Infrastructure** | CPU, memory, disk | CloudWatch |
| **Databricks** | Job duration, failures | CloudWatch + Databricks UI |
| **Application** | LLM latency, token usage | CloudWatch + Custom |
| **Cost** | DBU consumption, S3 costs | CloudWatch + Cost Explorer |

### Alerting

```yaml
Critical Alerts (PagerDuty):
  - Production job failure
  - Cluster health check failure
  - Cost anomaly (>200% of baseline)

Warning Alerts (Slack):
  - Staging job failure
  - High cluster utilization (>80%)
  - Spot instance interruption

Info Notifications (Slack):
  - Deployment completed
  - Scheduled maintenance
```

## Cost Optimization

### Strategies

1. **Spot Instances**
   - Dev: 100% spot (acceptable interruption)
   - Staging: 80% spot, 20% on-demand
   - Prod: Reserved instances for baseline, spot for burst

2. **Auto-termination**
   - Dev: 30 min idle
   - Staging: 60 min idle
   - Prod: Never (scheduled scale-down nights/weekends)

3. **Storage Lifecycle**
   - Bronze data: 30 days → IA, 90 days → Glacier
   - Silver data: 90 days → IA
   - Gold data: Keep indefinitely

4. **Budget Controls**
   - Monthly budget: $5K dev, $10K staging, $50K prod
   - Alert at 50%, 80%, 100%
   - Auto-shutdown at 120%

## Disaster Recovery

### RPO/RTO Targets

| Environment | RPO | RTO |
|-------------|-----|-----|
| Development | 24 hours | 4 hours |
| Staging | 12 hours | 2 hours |
| Production | 1 hour | 30 minutes |

### Backup Strategy

1. **Databricks Workspaces**
   - Git integration for notebooks (GitHub)
   - Automated export of job definitions (daily)
   - Cluster configuration in Terraform (version controlled)

2. **Data (S3)**
   - Cross-region replication to us-west-2
   - Versioning enabled on all buckets
   - 30-day retention of deleted objects

3. **State Files**
   - Terraform state in S3 with DynamoDB locking
   - Versioning enabled
   - Replicated to secondary region

## Getting Started

### Prerequisites

```bash
# Install required tools
brew install terraform
brew install databricks-cli
pip install databricks-connect

# Configure AWS CLI
aws configure

# Configure Databricks CLI
databricks configure --token
```

### Initial Setup

1. **Bootstrap Infrastructure**:
   ```bash
   cd infrastructure/terraform/aws-databricks
   terraform init
   terraform workspace new dev
   terraform apply -var-file=environments/dev/terraform.tfvars
   ```

2. **Configure Databricks CLI**:
   ```bash
   export DATABRICKS_HOST="https://..."
   export DATABRICKS_TOKEN="dapixxxxx"
   ```

3. **Deploy Databricks Bundle**:
   ```bash
   databricks bundle validate
   databricks bundle deploy --target dev
   ```

### Daily Operations

```bash
# Deploy to dev
databricks bundle deploy --target dev

# Run a job
databricks jobs run-now --job-id <job-id>

# View logs
databricks clusters list
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Cluster fails to start | Check IAM permissions, VPC endpoints |
| Job fails with timeout | Increase timeout, check resource limits |
| Import errors | Verify library installation, check Python version |
| Connection timeout | Check security groups, PrivateLink status |

### Debug Commands

```bash
# Check cluster status
databricks clusters get --cluster-id <id>

# View job runs
databricks jobs list-runs --job-id <id>

# Export logs
databricks clusters get --cluster-id <id> | jq .state
```

## References

- [Terraform Databricks Provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Databricks on AWS Best Practices](https://docs.databricks.com/administration-guide/account-settings/aws/index.html)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html)
- [AWS Databricks Security Guide](https://docs.databricks.com/security/index.html)

---

**Next Steps**: See `SETUP.md` for detailed setup instructions and `TROUBLESHOOTING.md` for common issues.
