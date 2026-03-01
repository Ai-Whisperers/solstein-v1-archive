# NOT DOING List

> Explicitly out of scope. If it's not on this list, it might be in scope. If it is on this list, it's definitely not.

---

## Q1 2026 (Jan-Mar)

### Features

| Item | Why Not | When Might It Be |
|------|---------|------------------|
| Mobile native apps (iOS/Android) | Web app is sufficient for MVP | Q3 2026 if web usage justifies |
| Real-time collaboration | Complex, low user demand | Q4 2026 if team features requested |
| Advanced analytics dashboard | Basic reporting sufficient | Q2 2026 after core stability |
| Custom report builder | Templates cover 80% use case | Q3 2026 if template requests spike |
| White-label / branding | Single-tenant only for now | 2027 if enterprise demand |

### Technical

| Item | Why Not | When Might It Be |
|------|---------|------------------|
| GraphQL API | REST sufficient, adds complexity | If mobile apps require it |
| Microservices extraction | Monolith manageable at current scale | >10 engineers or scaling issues |
| Kubernetes migration | Docker Compose sufficient | Multi-region deployment needed |
| Redis Cluster | Single Redis sufficient | >10k concurrent users |
| Read replicas | No read performance issues | Query time >500ms consistently |

### Integrations

| Item | Why Not | When Might It Be |
|------|---------|------------------|
| Salesforce integration | API export sufficient | Enterprise customers request |
| Slack bot | Webhook notifications sufficient | High engagement with notifications |
| Microsoft Teams | Slack covers most users | Teams-specific customer requests |
| Jira integration | Manual export sufficient | Agile teams become primary users |
| Custom webhooks | Supabase realtime sufficient | Developer ecosystem request |

---

## Q2 2026 (Apr-Jun)

### Features

| Item | Why Not | When Might It Be |
|------|---------|------------------|
| AI-generated executive summaries | LLM integration first | After EPIC-021 complete |
| Predictive scoring models | Current scoring sufficient | Historical data proves value |
| Benchmarking against industry | Data collection first | 6+ months of user data |
| Multi-language UI | English sufficient for target market | International expansion (EPIC-040) |
| Dark mode | Nice-to-have | User request volume |

### Technical

| Item | Why Not | When Might It Be |
|------|---------|------------------|
| Event sourcing | Current audit trail sufficient | Compliance audit requires |
| CQRS full implementation | Read/write separation partial | Performance requires |
| Multi-region deployment | Single region sufficient | EU data residency required |
| Blue-green deployment | Rolling updates sufficient | Zero-downtime required |
| Service mesh | Too complex for current scale | >20 microservices |

---

## Permanent "No" (Unless Strategy Changes)

| Item | Why Never |
|------|-----------|
| On-premise deployment | Cloud-native architecture, no Windows/Linux server support |
| Blockchain for audit trail | PostgreSQL audit sufficient, blockchain adds complexity |
| Custom ML model training | Use existing APIs (OpenAI, Anthropic), no ML ops capacity |
| Desktop application (Electron) | Web app covers all platforms |
| Phone/SMS support | Email + in-app sufficient |

---

## How to Challenge This List

If you believe something on this list should be done:

1. **Write a proposal** with:
   - User/business need
   - Impact quantification
   - Effort estimate
   - Alternative considered

2. **Present to Tech Lead** for technical items

3. **Present to Product** for feature items

4. **Decision recorded** in this file with date and rationale

---

## Recently Removed from NOT DOING

| Item | Date Removed | Reason |
|------|--------------|--------|
| pgvector semantic search | 2026-02-28 | Added as EPIC-023 after strategic review |
| LangGraph agent orchestration | 2026-02-28 | Added as EPIC-022 after strategic review |
| Supabase Auth migration | 2026-02-28 | Added as EPIC-020 after security audit |

---

## Related

- [Milestones](../MILESTONES/) — What's actively being worked on
- [Epic Registry](../README.md#epic-registry) — Full list of committed work
