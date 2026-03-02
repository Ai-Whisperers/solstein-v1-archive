# Solstein Deployment Guide

## Overview

This guide covers deploying Solstein to production environments.

## Prerequisites

- PostgreSQL 14+ database
- Python 3.10+
- Environment with sufficient resources (see Sizing)
- SSL certificates for HTTPS
- Domain name (optional but recommended)

## Environment Sizing

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Database**: PostgreSQL 14+ with 2GB RAM

### Recommended Production

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 100GB SSD
- **Database**: PostgreSQL 14+ with 4GB+ RAM
- **Read Replica**: For scaling reads

## Pre-Deployment Checklist

- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Health checks configured
- [ ] Monitoring setup
- [ ] Backup strategy defined
- [ ] Rollback plan documented

## Deployment Steps

### 1. Database Setup

```bash
# Create database
createdb solstein_production

# Apply migrations
for f in supabase/migrations/*.sql; do
    psql $DATABASE_URL -f "$f"
done

# Verify schema
psql $DATABASE_URL -c "\dt"
```

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/yourorg/solstein.git
cd solstein

# Install dependencies
pip install -e .

# Run tests
pytest tests/ -v

# Verify installation
python -c "import solstein; print('OK')"
```

### 3. Environment Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/solstein

# Application
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
APP_WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# Temporal (if using)
TEMPORAL_HOST=temporal-server
TEMPORAL_NAMESPACE=solstein

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4. SSL/TLS Setup

```bash
# Using Let's Encrypt
certbot certonly --standalone -d api.solstein.app

# Or use your own certificates
# Place in /etc/ssl/certs/
```

### 5. Process Management

Using systemd:

```ini
# /etc/systemd/system/solstein.service
[Unit]
Description=Solstein API
After=network.target

[Service]
Type=simple
User=solstein
Group=solstein
WorkingDirectory=/opt/solstein
Environment=PATH=/opt/solstein/venv/bin
ExecStart=/opt/solstein/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl enable solstein
sudo systemctl start solstein
sudo systemctl status solstein
```

Using Docker:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -e .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/solstein
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=solstein
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 6. Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name api.solstein.app;

    ssl_certificate /etc/letsencrypt/live/api.solstein.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.solstein.app/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 80;
    server_name api.solstein.app;
    return 301 https://$server_name$request_uri;
}
```

### 7. Health Checks

```bash
# Test health endpoint
curl https://api.solstein.app/health

# Expected response
{"status":"healthy","database":"connected"}

# Test ready endpoint
curl https://api.solstein.app/ready
```

### 8. Monitoring Setup

Using Prometheus:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'solstein'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

Using Grafana:
- Import dashboard for FastAPI
- Set up alerts for:
  - High error rates
  - Slow response times
  - Database connection issues

## Post-Deployment Verification

### 1. API Tests

```bash
# Test endpoints
curl https://api.solstein.app/companies
curl https://api.solstein.app/health
curl https://api.solstein.app/ready
```

### 2. Performance Baseline

```bash
python scripts/performance_baseline.py --save
```

### 3. Integration Tests

```bash
pytest tests/integration/ -v --base-url=https://api.solstein.app
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  api:
    image: solstein:latest
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@pgbouncer:6432/solstein

  pgbouncer:
    image: pgbouncer/pgbouncer
    environment:
      - DATABASES_HOST=postgres
      - DATABASES_PORT=5432
      - DATABASES_DATABASE=solstein
      - POOL_MODE=transaction
      - MAX_CLIENT_CONN=1000
```

### Read Replicas

```python
# Configure read replica
DATABASE_URL = "postgresql+asyncpg://primary"
DATABASE_URL_REPLICA = "postgresql+asyncpg://replica"

# Use replica for reads
async def get_companies():
    async with get_session(url=DATABASE_URL_REPLICA) as session:
        ...
```

## Backup Strategy

### Database Backups

```bash
# Daily backup
pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d).sql.gz

# Continuous archiving (WAL)
# Enable in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backups/wal/%f'
```

### Application Backups

```bash
# Backup configuration
tar czf config-backup.tar.gz .env config/

# Store in S3/GCS
aws s3 cp config-backup.tar.gz s3://solstein-backups/
```

## Security

### 1. Database Security

- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular security updates

### 2. Application Security

- Keep dependencies updated
- Use security headers
- Implement rate limiting
- Enable request validation

### 3. Network Security

- Firewall rules
- DDoS protection
- VPN for admin access
- Regular security scans

## Troubleshooting

### Database Connection Issues

```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1"

# Check pool status
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity"
```

### Performance Issues

```bash
# Check slow queries
psql $DATABASE_URL -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10"

# Analyze tables
psql $DATABASE_URL -c "ANALYZE"
```

### Application Issues

```bash
# Check logs
journalctl -u solstein -f

# Check resource usage
top -p $(pgrep -d',' solstein)
```

## Maintenance

### Regular Tasks

- Daily: Check logs, verify backups
- Weekly: Review performance metrics
- Monthly: Apply security updates
- Quarterly: Review and optimize queries

### Updates

```bash
# Zero-downtime deployment
# 1. Deploy new version
# 2. Verify health
# 3. Switch traffic
# 4. Monitor for issues
```

---

**See Also:**
- [Rollback Plan](ROLLBACK_PLAN.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Architecture Documentation](../ARCHITECTURE.md)
