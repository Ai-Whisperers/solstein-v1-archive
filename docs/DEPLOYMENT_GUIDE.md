# Enrichment System - Deployment Guide

**Status**: Production Ready  
**Version**: 1.0  
**Date**: 2026-02-25

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.12+
- pip or uv
- API keys (Companies House required, SEC EDGAR/News optional)

### Installation
```bash
# Clone repository
git clone <repo> && cd solstein

# Install with enrichment support
pip install -e ".[enrichment]"

# Or with uv (faster)
uv sync --extra enrichment
```

### Configuration
```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys
COMPANIES_HOUSE_API_KEY=your-key-here
SEC_EDGAR_API_KEY=optional-key
NEWS_API_KEY=optional-key
ENRICHMENT_ENABLED=true
```

### Run Server
```bash
# Start API server
uvicorn solstein.api.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Docker Deployment

### Build Image
```bash
docker build -t solstein:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e COMPANIES_HOUSE_API_KEY=your-key \
  -e ENRICHMENT_ENABLED=true \
  solstein:latest
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'
services:
  api:
    image: solstein:latest
    ports:
      - "8000:8000"
    environment:
      - ENRICHMENT_ENABLED=true
      - COMPANIES_HOUSE_API_KEY=${COMPANIES_HOUSE_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/solstein
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=solstein
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=solstein
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes 1.20+
- kubectl configured
- Docker image pushed to registry

### Namespace
```bash
kubectl create namespace solstein
kubectl config set-context --current --namespace=solstein
```

### ConfigMap (Configuration)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: enrichment-config
  namespace: solstein
data:
  ENRICHMENT_ENABLED: "true"
  ENRICHMENT_BATCH_SIZE: "10"
  SEC_EDGAR_TIMEOUT: "30"
  COMPANIES_HOUSE_TIMEOUT: "30"
  MAX_RETRIES: "3"
```

### Secret (API Keys)
```bash
kubectl create secret generic enrichment-keys \
  --from-literal=companies-house-api-key=<key> \
  --from-literal=sec-edgar-api-key=<key> \
  --namespace=solstein
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enrichment-api
  namespace: solstein
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enrichment-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: enrichment-api
    spec:
      containers:
      - name: api
        image: solstein:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: enrichment-config
        env:
        - name: COMPANIES_HOUSE_API_KEY
          valueFrom:
            secretKeyRef:
              name: enrichment-keys
              key: companies-house-api-key
        - name: SEC_EDGAR_API_KEY
          valueFrom:
            secretKeyRef:
              name: enrichment-keys
              key: sec-edgar-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      terminationGracePeriodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: enrichment-api
  namespace: solstein
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
  selector:
    app: enrichment-api

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: enrichment-api-hpa
  namespace: solstein
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: enrichment-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Apply Deployment
```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml

# Verify
kubectl get pods -n solstein
kubectl logs deployment/enrichment-api -n solstein
```

---

## CI/CD Pipeline (GitHub Actions)

### `.github/workflows/deploy.yml`
```yaml
name: Deploy Enrichment System

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - run: pip install -e ".[dev]"
    - run: pytest tests/ -v
    - run: coverage report

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - uses: docker/build-push-action@v4
      with:
        push: true
        tags: |
          solstein:latest
          solstein:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    - run: kubectl set image deployment/enrichment-api api=solstein:${{ github.sha }}
```

---

## Environment Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=true
ENRICHMENT_ENABLED=true
SEC_EDGAR_TIMEOUT=30
COMPANIES_HOUSE_TIMEOUT=30
MAX_RETRIES=3
ENRICHMENT_BATCH_SIZE=10
```

### Staging
```bash
ENVIRONMENT=staging
DEBUG=false
ENRICHMENT_ENABLED=true
SEC_EDGAR_TIMEOUT=45
COMPANIES_HOUSE_TIMEOUT=45
MAX_RETRIES=5
ENRICHMENT_BATCH_SIZE=20
LOG_LEVEL=INFO
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
ENRICHMENT_ENABLED=true
SEC_EDGAR_TIMEOUT=60
COMPANIES_HOUSE_TIMEOUT=60
MAX_RETRIES=7
ENRICHMENT_BATCH_SIZE=50
LOG_LEVEL=WARNING
SENTRY_DSN=<your-sentry-dsn>
```

---

## Health Checks

### Liveness (Running)
```bash
curl http://localhost:8000/health
```

Expected: 200 OK with `{"status": "healthy"}`

### Readiness (Ready to serve)
```bash
curl http://localhost:8000/ready
```

Expected: 200 OK with `{"ready": true}`

### Full Diagnostics
```bash
curl http://localhost:8000/metrics
```

Expected: 200 OK with performance metrics

---

## Monitoring & Logging

### Structured Logging
```python
logger.info("✅ Enrichment complete", extra={
    "company_id": "001",
    "sources": ["SEC_EDGAR"],
    "duration_ms": 1234,
    "user_id": "admin@example.com"
})
```

### Log Levels
- `DEBUG`: Detailed enrichment flow, cache operations
- `INFO`: Batch start/completion, successful enrichments
- `WARNING`: Enrichment failures, API timeouts
- `ERROR`: Unrecoverable failures, data corruption

### Monitoring Dashboard
```
Metrics to Track:
- Enrichment success rate (target: >95%)
- Cache hit rate (target: >60%)
- Average duration (target: <1s)
- API error rate (target: <1%)
- Rate limit violations (target: 0)
```

---

## Troubleshooting

### Issue: "API key not found"
```bash
# Check environment variables
env | grep API_KEY

# Verify .env file
cat .env | grep COMPANIES_HOUSE_API_KEY

# Solution: Add valid API key to .env
```

### Issue: "Connection timeout"
```bash
# Check connector timeout settings
grep TIMEOUT .env

# Increase timeout if needed
SEC_EDGAR_TIMEOUT=60  # up from 30

# Verify network connectivity
curl -I https://www.sec.gov
```

### Issue: "Cache not working"
```bash
# Clear cache and restart
curl -X POST http://localhost:8000/enrichment/cache/clear

# Verify metrics
curl http://localhost:8000/metrics
```

### Issue: "Rate limit exceeded"
```bash
# Check current rate limit status
curl -I http://localhost:8000/health | grep RateLimit

# Wait for reset (automatic every minute)
# Or temporarily increase limit in config:
# RATE_LIMIT_PER_MINUTE=200
```

---

## Performance Tuning

### Batch Size Optimization
```python
# For 100 companies:
# batch_size=10  → 10 batches (~2-3s total)
# batch_size=20  → 5 batches (~1.5-2s total)
# batch_size=50  → 2 batches (~1-1.5s total)

# Recommendation: Start with 20, monitor performance
ENRICHMENT_BATCH_SIZE=20
```

### Cache TTL Tuning
```python
# 24 hours (default) - good for stable data
# 12 hours - if data updates frequently
# 7 days - if data rarely changes

# Set in code:
cache = CacheService(ttl_hours=24)
```

### Timeout Tuning
```python
# Based on network latency + API response time:
# Fast networks: 15-20 seconds
# Standard networks: 30-45 seconds
# Slow networks: 60+ seconds

SEC_EDGAR_TIMEOUT=30
COMPANIES_HOUSE_TIMEOUT=30
```

---

## Scaling

### Horizontal Scaling (Kubernetes)
```bash
# Auto-scale based on CPU/memory
kubectl autoscale deployment enrichment-api \
  --min=2 --max=10 --cpu-percent=70 -n solstein

# Manual scaling
kubectl scale deployment enrichment-api \
  --replicas=5 -n solstein
```

### Vertical Scaling
```yaml
# Increase resources in deployment
resources:
  requests:
    memory: "512Mi"  # up from 256Mi
    cpu: "500m"      # up from 250m
  limits:
    memory: "1Gi"    # up from 512Mi
    cpu: "1000m"     # up from 500m
```

---

## Backup & Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump -U solstein -h localhost solstein > backup.sql

# Restore
psql -U solstein -h localhost solstein < backup.sql
```

### Cache Recovery
Cache is ephemeral (in-memory):
- Automatic TTL cleanup (24 hours)
- Manual clear: `curl -X POST /enrichment/cache/clear`
- No persistence required

---

## Post-Deployment Checklist

- [ ] Health check passes (`/health`)
- [ ] Readiness check passes (`/ready`)
- [ ] Metrics endpoint responds (`/metrics`)
- [ ] Audit logging active
- [ ] Rate limiting functional
- [ ] Cache working (hit rate > 0%)
- [ ] All 3 connectors initialized
- [ ] Load tests completed (100+ companies)
- [ ] Monitoring dashboards configured
- [ ] Alerting thresholds set

---

## Support & Escalation

For issues:
1. Check logs: `kubectl logs deployment/enrichment-api -n solstein`
2. Review metrics: `curl http://localhost:8000/metrics`
3. Verify audit trail: `curl http://localhost:8000/companies/{id}/enrichment/audit`
4. Check rate limits: Response headers `X-RateLimit-*`
