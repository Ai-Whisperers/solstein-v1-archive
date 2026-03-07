# OIDC Configuration for Cloud Providers
# This file documents how to configure OIDC authentication for AWS, GCP, and Azure

## AWS OIDC Setup

### 1. Create an OIDC Provider in AWS IAM

```bash
# Get the GitHub OIDC provider thumbprint
THUMBPRINT=$(openssl s_client -servername token.actions.githubusercontent.com \
  -connect token.actions.githubusercontent.com:443 < /dev/null 2>/dev/null |
  openssl x509 -fingerprint -noout | cut -d'=' -f2 | tr -d ':' | tr '[:upper:]' '[:lower:]')

# Create the OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint-list $THUMBPRINT \
  --client-id-list sts.amazonaws.com
```

### 2. Create an IAM Role for GitHub Actions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:your-org/solstein:*"
        }
      }
    }
  ]
}
```

### 3. Attach Policies to the Role

```bash
aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess
```

### 4. Store Role ARN in GitHub Secrets

```bash
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole"
gh secret set AWS_REGION --body "us-east-1"
```

## GCP OIDC Setup

### 1. Create a Workload Identity Pool

```bash
gcloud iam workload-identity-pools create github-actions-pool \
  --location="global" \
  --description="GitHub Actions OIDC pool"
```

### 2. Create a Workload Identity Provider

```bash
gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub" \
  --attribute-condition="assertion.repository=='your-org/solstein'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 3. Grant Access to Service Account

```bash
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/your-org/solstein"
```

### 4. Store Configuration in GitHub Secrets

```bash
gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --body "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider"
gh secret set GCP_SERVICE_ACCOUNT --body "github-actions@PROJECT_ID.iam.gserviceaccount.com"
```

## Azure OIDC Setup

### 1. Create an App Registration

```bash
az ad app create --display-name "GitHub Actions"
```

### 2. Create a Service Principal

```bash
az ad sp create --id $(az ad app list --display-name "GitHub Actions" --query '[0].appId' -o tsv)
```

### 3. Configure Federated Credentials

```bash
az ad app federated-credential create \
  --id $(az ad app list --display-name "GitHub Actions" --query '[0].appId' -o tsv) \
  --parameters '{
    "name": "GitHubActions",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:your-org/solstein:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### 4. Store Configuration in GitHub Secrets

```bash
gh secret set AZURE_CLIENT_ID --body "$(az ad app list --display-name 'GitHub Actions' --query '[0].appId' -o tsv)"
gh secret set AZURE_TENANT_ID --body "$(az account show --query 'tenantId' -o tsv)"
gh secret set AZURE_SUBSCRIPTION_ID --body "$(az account show --query 'id' -o tsv)"
```

## Usage in Workflows

### AWS

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ secrets.AWS_REGION }}
```

### GCP

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

### Azure

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```
