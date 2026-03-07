# EPIC-052: Community-Driven API Discovery

|**Status:** 🔴 Not Started  
|**Priority:** MEDIUM (P2)  
|**Story Points:** 21  
|**Sprint Allocation:** 2 sprints  
|**Target Date:** Week 33-34

---

## Problem Statement

API landscape evolves rapidly. Solstein's small team cannot continuously monitor and evaluate all potential data sources. A community-driven approach to API discovery would leverage user knowledge and scale the platform's data source expansion beyond internal capacity.

### Impact
- Limited visibility into new APIs
- Team bottleneck for API evaluation
- Missing valuable data sources known to users
- No feedback loop from analysts using the platform
- Slower data source expansion than competitors

---

## Success Criteria

1. ✅ Public API suggestion system operational
2. ✅ Community voting on proposed APIs
3. ✅ Contributor documentation for adding APIs
4. ✅ Recognition/incentive system for contributors
5. ✅ Monthly community API review process
6. ✅ 20+ APIs suggested by community in first quarter

---

## Stories

### Story 52.1: API Suggestion System (8 pts)
**Task:** Build system for community API suggestions

**Acceptance Criteria:**
- [ ] API suggestion form (web UI or GitHub issue template)
- [ ] Required fields: API name, provider, URL, use case, category
- [ ] Optional fields: pricing, auth type, rate limits, coverage
- [ ] Suggestion validation and deduplication
- [ ] Suggestion status tracking (submitted, under review, accepted, rejected)
- [ ] Notification system for updates

**GitHub Issue Template:**
```yaml
# .github/ISSUE_TEMPLATE/api_suggestion.yml
name: API Source Suggestion
description: Suggest a new data source for Solstein
title: '[API Suggestion] '
labels: ['api-suggestion', 'triage']
body:
  - type: input
    id: api_name
    attributes:
      label: API Name
      placeholder: e.g., "Crunchbase API"
    validations:
      required: true
  
  - type: input
    id: provider
    attributes:
      label: Provider/Company
      placeholder: e.g., "Crunchbase Inc."
    validations:
      required: true
  
  - type: input
    id: documentation_url
    attributes:
      label: API Documentation URL
      placeholder: https://...
    validations:
      required: true
  
  - type: dropdown
    id: category
    attributes:
      label: Category
      options:
        - Financial Data
        - Regulatory/Government
        - News & Media
        - Jobs & Hiring
        - Social Media
        - Web Scraping
        - Patents & IP
        - Other
    validations:
      required: true
  
  - type: textarea
    id: use_case
    attributes:
      label: Use Case for Solstein
      placeholder: How would this API enhance competitive intelligence?
    validations:
      required: true
  
  - type: dropdown
    id: pricing
    attributes:
      label: Pricing
      options:
        - Free
        - Freemium
        - Paid
        - Enterprise
        - Unknown
  
  - type: textarea
    id: additional_info
    attributes:
      label: Additional Information
      placeholder: Rate limits, coverage, data quality notes, etc.
```

---

### Story 52.2: Community Voting & Prioritization (5 pts)
**Task:** Implement voting system for API suggestions

**Acceptance Criteria:**
- [ ] Voting mechanism on API suggestions (GitHub reactions or custom)
- [ ] Comment/discussion thread per suggestion
- [ ] Priority scoring based on votes + internal assessment
- [ ] Leaderboard of top requested APIs
- [ ] Regular review of high-vote suggestions

---

### Story 52.3: Contributor Documentation (5 pts)
**Task:** Create documentation for API contributors

**Acceptance Criteria:**
- [ ] Contributor guide for suggesting APIs
- [ ] Template for API evaluation
- [ ] Documentation for creating adapter PRs
- [ ] Quality standards explained
- [ ] Recognition program described

**Documentation Structure:**
```
docs/contributing/
├── README.md                    # Contributor overview
├── API_SUGGESTION_GUIDE.md      # How to suggest APIs
├── ADAPTER_CONTRIBUTION.md      # How to build adapters
├── QUALITY_STANDARDS.md         # What makes a good API
└── RECOGNITION.md               # Contributor recognition
```

---

### Story 52.4: Recognition & Incentives (3 pts)
**Task:** Build contributor recognition system

**Acceptance Criteria:**
- [ ] Contributor leaderboard
- [ ] Badges/achievements for contributions
- [ ] Recognition in release notes
- [ ] "API Curator" role for top contributors
- [ ] Quarterly contributor spotlight

---

## Definition of Done

- [ ] API suggestion system operational
- [ ] GitHub issue templates created
- [ ] Community voting active
- [ ] Contributor documentation published
- [ ] Recognition system launched
- [ ] 5+ API suggestions received
- [ ] First community-suggested API integrated

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low community engagement | Medium | Medium | Promotion, incentives |
| Quality of suggestions | Medium | Medium | Clear guidelines, review process |
| Spam/abuse | Low | Low | Moderation, validation |

---

## Resources

- **Developers:** 1 backend engineer
- **Time:** 2 weeks
- **Dependencies:** EPIC-049 (catalog framework)

---

*Epic created from OpenClaw API list analysis*
