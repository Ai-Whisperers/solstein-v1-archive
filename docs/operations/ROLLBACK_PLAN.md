# Solstein Rollback Plan

## Overview

This document outlines procedures for rolling back the PostgreSQL migration if critical issues are encountered.

## Rollback Scenarios

### Scenario 1: Critical Data Loss

If data loss is detected during migration:

1. **Stop all services immediately**
   ```bash
   sudo systemctl stop solstein
   ```

2. **Restore from backup**
   ```bash
   # If you have a pre-migration backup
   pg_restore -d solstein_production backup-pre-migration.dump
   ```

3. **Verify data integrity**
   ```bash
   python scripts/verify_database_integrity.py
   ```

4. **Restart services**
   ```bash
   sudo systemctl start solstein
   ```

### Scenario 2: Application Errors

If the application encounters errors after migration:

1. **Check error logs**
   ```bash
   journalctl -u solstein -n 100 --no-pager
   ```

2. **Identify failing queries**
   ```bash
   # Check PostgreSQL logs
   sudo tail -f /var/log/postgresql/postgresql-15-main.log
   ```

3. **If fixable, apply fix**
   - Missing index? Add index
   - Constraint issue? Review constraints
   - Query error? Update code

4. **If not fixable quickly, consider partial rollback**

### Scenario 3: Performance Degradation

If database performance is worse than JSON files:

1. **Run performance baseline**
   ```bash
   python scripts/performance_baseline.py
   ```

2. **Compare with pre-migration metrics**
   - Query execution times
   - Concurrent user handling
   - Memory usage

3. **Apply optimizations**
   - Add missing indexes
   - Optimize slow queries
   - Tune PostgreSQL configuration

4. **If still unsatisfactory, plan rollback**

## Rollback Procedures

### Full Rollback to JSON

**⚠️ Warning: This will lose any data created after migration**

1. **Export new data (if possible)**
   ```bash
   # Export any new records created since migration
   pg_dump --data-only --table=new_table $DATABASE_URL > new_data.sql
   ```

2. **Archive PostgreSQL data**
   ```bash
   pg_dump $DATABASE_URL | gzip > postgresql-archive-$(date +%Y%m%d).sql.gz
   ```

3. **Switch to JSON mode**
   ```bash
   # Update configuration
   echo "USE_JSON_STORAGE=true" >> .env

   # Revert code changes
   git checkout pre-migration-branch
   ```

4. **Verify JSON files exist**
   ```bash
   ls -la data/competitors/
   ```

5. **Restart application**
   ```bash
   sudo systemctl restart solstein
   ```

6. **Verify operation**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/companies
   ```

### Partial Rollback (Hybrid Mode)

Run both JSON and PostgreSQL in parallel:

1. **Enable dual-write mode**
   ```python
   # In configuration
   DUAL_WRITE_MODE = True
   ```

2. **Write to both storage types**
   ```python
   async def create_company(data):
       # Write to PostgreSQL
       company_db = await db_repo.create(data)

       # Also write to JSON (for rollback safety)
       company_json = await json_repo.create(data)

       return company_db
   ```

3. **Read from PostgreSQL primarily**
   ```python
   async def get_company(id):
       # Try PostgreSQL first
       company = await db_repo.get_by_id(id)
       if not company and DUAL_WRITE_MODE:
           # Fallback to JSON
           company = await json_repo.get_by_id(id)
       return company
   ```

4. **Monitor both systems**
   - Compare data consistency
   - Track performance difference
   - Plan final migration

## Pre-Rollback Checklist

Before initiating rollback:

- [ ] Document reason for rollback
- [ ] Notify stakeholders
- [ ] Create backup of current state
- [ ] Estimate downtime
- [ ] Prepare rollback script
- [ ] Test rollback procedure in staging
- [ ] Have rollback team on standby

## Rollback Verification

After rollback:

- [ ] Application starts successfully
- [ ] Health checks pass
- [ ] Critical functions work
- [ ] Data is accessible
- [ ] Performance is acceptable
- [ ] No error logs
- [ ] Users can access system

## Communication Plan

### During Rollback

1. **Notify immediately**
   - Slack/email to team
   - Status page update
   - Customer communication (if external)

2. **Provide updates every 15 minutes**
   - Current status
   - Expected completion
   - Any issues encountered

3. **Post-rollback**
   - Confirm resolution
   - Root cause analysis
   - Prevention measures

## Prevention Measures

To avoid future rollbacks:

1. **Pre-migration Testing**
   - Comprehensive test suite
   - Load testing
   - Data integrity checks
   - Staging environment validation

2. **Gradual Migration**
   - Start with read-only traffic
   - Gradually increase write traffic
   - Monitor metrics continuously

3. **Feature Flags**
   - Use database via feature flag
   - Can quickly disable if issues
   - A/B test performance

4. **Monitoring**
   - Set up alerts for errors
   - Track performance metrics
   - Monitor data consistency

## Rollback Decision Matrix

| Issue | Severity | Action | Timeframe |
|-------|----------|--------|-----------|
| Data loss | Critical | Immediate rollback | Minutes |
| Security breach | Critical | Immediate rollback | Minutes |
| Complete outage | Critical | Immediate rollback | Minutes |
| Slow queries | High | Optimize first | Hours |
| Minor data inconsistency | Medium | Fix forward | Days |
| Feature degradation | Low | Fix forward | Next release |

## Contact Information

**Escalation Path:**
1. On-call engineer
2. Engineering lead
3. CTO

**Emergency Contacts:**
- Database Admin: [contact]
- DevOps: [contact]
- Product Owner: [contact]

## Post-Rollback Analysis

After any rollback, conduct:

1. **Root Cause Analysis**
   - What went wrong?
   - Why wasn't it caught?
   - How to prevent recurrence?

2. **Documentation Update**
   - Update runbooks
   - Revise procedures
   - Improve monitoring

3. **Team Retrospective**
   - What worked?
   - What didn't?
   - Improvements for next time?

---

**Last Updated**: 2024
**Owner**: Engineering Team
**Review Schedule**: Quarterly
