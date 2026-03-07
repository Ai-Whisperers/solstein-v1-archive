# EPIC-033: Data Pipeline Hardening

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 6

---

## Problem Statement

The current data pipeline has gaps:
- No real-time data updates
- No change detection when company data changes
- No data versioning or history
- No incremental enrichment (always full re-enrichment)
- No data lineage tracking

### Impact
- Stale data in platform
- Expensive full re-enrichment runs
- No audit trail for data changes
- Cannot track company evolution over time

---

## Success Criteria

1. ✅ Real-time data updates from sources
2. ✅ Change detection for all tracked fields
3. ✅ Data versioning with full history
4. ✅ Incremental enrichment (only changed fields)
5. ✅ Complete data lineage tracking
6. ✅ 50% reduction in enrichment costs

---

## Technical Analysis

### Current State
- Batch enrichment only
- No change tracking
- Full re-enrichment on every run
- No versioning

### Target State
- Event-driven updates
- Change data capture (CDC)
- Temporal tables for history
- Incremental processing

---

## Stories

### Story 3.1: Implement Change Data Capture (13 pts)
**Task:** Track all changes to company data

**Acceptance Criteria:**
- [ ] CDC enabled on company records
- [ ] Change events published to message queue
- [ ] Change types tracked (CREATE, UPDATE, DELETE)
- [ ] Changed fields identified
- [ ] Timestamp and user tracking

**Implementation:**
```python
# Database trigger or application-level
def on_company_change(company_id: str, changes: dict):
    event = ChangeEvent(
        entity="company",
        entity_id=company_id,
        change_type="UPDATE",
        changed_fields=list(changes.keys()),
        old_values={k: v.old for k, v in changes.items()},
        new_values={k: v.new for k, v in changes.items()},
        timestamp=datetime.utcnow(),
        user_id=get_current_user()
    )
    await publish_to_queue(event)
```

---

### Story 3.2: Implement Temporal Tables (8 pts)
**Task:** Store full history of all data changes

**Acceptance Criteria:**
- [ ] Company history table created
- [ ] Financial metrics history table created
- [ ] Scoring history table created
- [ ] Point-in-time queries possible
- [ ] History retention policy configured

**Implementation:**
```sql
-- PostgreSQL temporal tables
CREATE TABLE company_history (
    company_id TEXT,
    name TEXT,
    revenue_eur_m FLOAT,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    PRIMARY KEY (company_id, valid_from)
);

-- Query as of specific date
SELECT * FROM company_history
WHERE company_id = '123'
AND valid_from <= '2024-01-01'
AND valid_to > '2024-01-01';
```

---

### Story 3.3: Build Incremental Enrichment (13 pts)
**Task:** Only enrich changed fields

**Acceptance Criteria:**
- [ ] Change detection in enrichment pipeline
- [ ] Only changed fields re-enriched
- [ ] Cost tracking per enrichment
- [ ] 50% reduction in enrichment costs

**Implementation:**
```python
async def incremental_enrich(company_id: str):
    company = await get_company(company_id)
    changes = await detect_changes(company)
    
    if not changes:
        logger.info(f"No changes for {company_id}, skipping")
        return
    
    # Only enrich changed fields
    for field in changes:
        await enrich_field(company_id, field)
```

---

### Story 3.4: Real-time Data Streaming (13 pts)
**Task:** Stream updates from sources in real-time

**Acceptance Criteria:**
- [ ] Webhooks from data sources received
- [ ] Events processed in real-time
- [ ] <1 minute latency from source to platform
- [ ] Backpressure handling

**Implementation:**
```python
@app.post("/webhooks/crunchbase")
async def crunchbase_webhook(event: WebhookEvent):
    # Process update immediately
    await process_company_update(event.company_id)
    await notify_subscribers(event.company_id)
```

---

### Story 3.5: Data Lineage Tracking (8 pts)
**Task:** Track where every data point came from

**Acceptance Criteria:**
- [ ] Every field has source attribution
- [ ] Confidence score per field
- [ ] Last updated timestamp per field
- [ ] Enrichment history per field

**Implementation:**
```python
class DataProvenance:
    field_name: str
    source: str  # "crunchbase", "linkedin", "manual"
    confidence: float
    extracted_at: datetime
    enrichment_version: str
    raw_value: Any
```

---

## Architecture

```
Data Sources → Webhooks → Event Queue → 
Change Detection → Incremental Enrichment → 
Temporal Tables → Cache Update → Notifications
```

---

## Definition of Done

- [ ] All data changes tracked
- [ ] Full history queryable
- [ ] Incremental enrichment working
- [ ] Real-time updates <1 min latency
- [ ] Data lineage visible in UI
- [ ] 50% enrichment cost reduction achieved
- [ ] Documentation complete

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Storage explosion from history | High | High | Retention policies, archiving |
| Event queue overload | Medium | High | Backpressure, scaling |
| Out of order events | Medium | Medium | Event ordering, idempotency |

---

## Resources

- **Developers:** 3 backend engineers
- **Time:** 4 weeks
- **Dependencies:** EPIC-031, EPIC-032

---

*Epic created as part of Comprehensive Analysis*
