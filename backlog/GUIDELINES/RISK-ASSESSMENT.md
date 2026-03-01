# Risk Assessment Framework

> Every story carries risk. Identify it early, mitigate it continuously.

---

## Risk Dimensions

### 1. Technical Risk

**Database Changes**
- Schema migrations
- Data migrations
- Index changes
- Connection pool changes

**External Dependencies**
- Third-party APIs
- Library upgrades
- Infrastructure services
- Vendor lock-in

**Performance**
- Query optimization
- Caching strategy
- Resource utilization
- Scalability limits

### 2. Operational Risk

**Deployment**
- Requires downtime
- Database migrations
- Configuration changes
- Rollback complexity

**Monitoring**
- New metrics needed
- Alert thresholds unknown
- Log volume changes
- Error detection gaps

### 3. Business Risk

**User Impact**
- Breaking changes
- UI/UX changes
- Workflow disruption
- Training requirements

**Compliance**
- Regulatory requirements
- Audit trail needs
- Data retention
- Privacy implications

---

## Risk Matrix

| Likelihood \ Impact | Low | Medium | High |
|---------------------|-----|--------|------|
| **High** | 🟡 Monitor | 🔴 Mitigate | 🛑 Block / Spike |
| **Medium** | 🟢 Accept | 🟡 Monitor | 🔴 Mitigate |
| **Low** | 🟢 Accept | 🟢 Accept | 🟡 Monitor |

### Actions

| Action | When | How |
|--------|------|-----|
| **🟢 Accept** | Low risk | Proceed with standard process |
| **🟡 Monitor** | Medium risk | Add checkpoints, review more frequently |
| **🔴 Mitigate** | High risk | Implement specific mitigations before proceeding |
| **🛑 Block** | Critical risk | Requires spike story or architecture review |

---

## Risk Checklist

### For Every Story

**Technical:**
- [ ] Does this change the database schema?
- [ ] Does this affect external API integrations?
- [ ] Could this impact performance?
- [ ] Are there new dependencies?
- [ ] Is this a new pattern or technology?

**Operational:**
- [ ] Does this require a migration?
- [ ] Can this be rolled back quickly?
- [ ] Are new monitoring/alerting needed?
- [ ] Does this change configuration?

**Business:**
- [ ] Is this a breaking change for users?
- [ ] Are there compliance implications?
- [ ] Could this affect data integrity?
- [ ] Is there a security implication?

---

## Common Risk Patterns

### High Risk Combinations

| Pattern | Risk | Mitigation |
|---------|------|------------|
| Database migration + No rollback plan | 🔴 High | Write rollback script first |
| New technology + Production deployment | 🔴 High | Deploy to staging first, observe |
| Breaking change + No feature flag | 🔴 High | Add feature flag, gradual rollout |
| Performance change + No metrics | 🔴 High | Add metrics before change |
| Security fix + No test | 🔴 High | Write regression test first |

### Medium Risk Patterns

| Pattern | Risk | Mitigation |
|---------|------|------------|
| Cross-module refactoring | 🟡 Medium | Incremental changes, frequent testing |
| Library upgrade (major) | 🟡 Medium | Read changelog, test thoroughly |
| New integration | 🟡 Medium | Mock external service for tests |
| Configuration change | 🟡 Medium | Validate config at startup |

---

## Risk Documentation

### In Story Template

```markdown
## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database migration fails | Low | High | Test migration on copy of prod data |
| New library has bugs | Medium | Medium | Keep old implementation as fallback |
| Performance regression | Medium | High | Add load test, monitor after deploy |
```

### Risk Review Meeting

**Weekly, 15 minutes:**
1. Review stories starting next sprint
2. Identify any 🔴 High risks
3. Confirm mitigations are in place
4. Escalate 🛑 Block items

---

## Escalation Path

```
Engineer identifies risk
        ↓
  Can mitigate?
   /        \
  Yes        No
  |           |
  ↓           ↓
Document   Escalate to
mitigation Tech Lead
in story        |
                ↓
          Architecture
          review needed?
           /        \
         Yes         No
          |           |
          ↓           ↓
    Schedule     Proceed with
    ADR review   TL guidance
```

---

## Related

- [Estimation Framework](ESTIMATION.md) — XL stories often have high risk
- [Story Template](../.backlog/templates/story.md) — Include risk section
- [Success Metrics](SUCCESS-METRICS.md) — Track risk identification accuracy
