# EPIC-050: OpenClaw-Relevant API Integration

|**Status:** 🔴 Not Started  
|**Priority:** HIGH (P1)  
|**Story Points:** 34  
|**Sprint Allocation:** 3 sprints  
|**Target Date:** Week 28-30

---

## Problem Statement

Analysis of the OpenClaw API list (10,498 APIs) identified approximately 200-300 APIs relevant to competitive intelligence, particularly in news, jobs, social media, and lead generation categories. These APIs are not currently integrated into Solstein but could enhance data coverage for hiring signals, sentiment analysis, and company discovery.

### Impact
- Missing hiring intelligence from 800+ job APIs
- No social media sentiment analysis from 3,000+ social APIs
- Limited news aggregation beyond current sources
- Undiscovered company discovery opportunities
- Competitive disadvantage vs. platforms using these signals

---

## Success Criteria

1. ✅ 50+ high-relevance OpenClaw APIs evaluated and prioritized
2. ✅ 20+ new APIs integrated into Solstein enrichment pipeline
3. ✅ Hiring signal coverage expanded (EPIC-043.3 enhancement)
4. ✅ Social sentiment monitoring operational
5. ✅ News aggregation diversified beyond current sources
6. ✅ All integrations follow Solstein adapter patterns

---

## Stories

### Story 50.1: OpenClaw API Evaluation & Prioritization (8 pts)
**Task:** Systematically evaluate OpenClaw APIs for Solstein relevance

**Acceptance Criteria:**
- [ ] All 10,498 APIs categorized by relevance (high/medium/low)
- [ ] High-relevance list (target: 50-100 APIs) documented
- [ ] Each API scored using EPIC-049 criteria
- [ ] Top 20 APIs selected for immediate integration
- [ ] API evaluation data stored in catalog format
- [ ] Evaluation methodology documented

**Relevance Scoring:**
```python
# src/solstein/data_sources/openclaw_evaluator.py
class OpenClawEvaluator:
    """Evaluate OpenClaw APIs for Solstein relevance."""
    
    HIGH_RELEVANCE_CATEGORIES = [
        ('JOBS-APIS', 0.9),           # Hiring signals
        ('NEWS-APIS', 0.85),          # Market signals
        ('SOCIAL-MEDIA-APIS', 0.8),   # Sentiment, reviews
        ('LEAD-GENERATION-APIS', 0.75),  # Company discovery
        ('SEO-TOOLS-APIS', 0.7),      # Web presence
    ]
    
    def evaluate(self, api: dict) -> dict:
        """Score API for Solstein relevance."""
        scores = {
            'category_match': self.score_category(api),
            'ci_relevance': self.score_ci_usefulness(api),
            'technical_fit': self.score_technical(api),
            'coverage': self.score_coverage(api),
        }
        scores['overall'] = weighted_average(scores)
        return scores
```

---

### Story 50.2: Jobs & Hiring Signal APIs (8 pts)
**Task:** Integrate top job board and hiring intelligence APIs

**Acceptance Criteria:**
- [ ] 5-8 job aggregator APIs integrated
- [ ] Hiring trend extraction by company
- [ ] Role/skill normalization pipeline
- [ ] Time-series hiring data storage
- [ ] Integration with EPIC-043.3 (hiring signals)
- [ ] Rate limiting and caching implemented

**Target APIs:**
| API | Category | Use Case |
|-----|----------|----------|
| Adzuna | Jobs | Job listings by company |
| CareerJet | Jobs | Aggregated job data |
| JSearch (RapidAPI) | Jobs | Real-time job search |
| LinkedIn Jobs (unofficial) | Jobs | Professional hiring |
| Reed.co.uk | Jobs | UK hiring data |
| Indeed API | Jobs | Global job aggregator |

**Adapter Pattern:**
```python
# src/solstein/adapters/enrichment/jobs_unified.py
class JobsUnifiedAdapter(BaseDataSourceAdapter):
    """Unified adapter for job board APIs."""
    
    source_name = "jobs_aggregate"
    source_type = DataSourceType.JOBS
    
    def __init__(self, apis: list[JobAPIClient]):
        self.apis = apis
    
    async def enrich(self, company_id, company_name, **kwargs) -> RawDataSource:
        """Aggregate hiring data from multiple job APIs."""
        jobs = []
        for api in self.apis:
            try:
                api_jobs = await api.search_jobs(company=company_name)
                jobs.extend(api_jobs)
            except APIError as e:
                logger.warning(f"{api.name} failed: {e}")
        
        return RawDataSource(
            source_type=self.source_type,
            data=self.normalize_jobs(jobs),
            confidence=self.calculate_confidence(jobs),
        )
    
    def normalize_jobs(self, jobs: list) -> list[dict]:
        """Normalize job data to common schema."""
        return [{
            'title': job.get('title'),
            'role_category': self.categorize_role(job['title']),
            'location': job.get('location'),
            'posted_date': parse_date(job.get('date')),
            'skills': self.extract_skills(job.get('description', '')),
            'seniority': self.infer_seniority(job['title']),
        } for job in jobs]
```

---

### Story 50.3: Social Media & Sentiment APIs (8 pts)
**Task:** Integrate social media monitoring and sentiment analysis APIs

**Acceptance Criteria:**
- [ ] 5-8 social media APIs integrated
- [ ] Company mention tracking across platforms
- [ ] Sentiment analysis pipeline
- [ ] Review aggregation (Glassdoor, Trustpilot patterns)
- [ ] Social engagement metrics
- [ ] Integration with scoring engine

**Target APIs:**
| API | Platform | Data Type |
|-----|----------|-----------|
| Brandwatch | Multi | Social listening |
| Mention | Multi | Brand monitoring |
| Social Searcher | Multi | Social mentions |
| Reddit API | Reddit | Community sentiment |
| Twitter/X API | X | Public sentiment |
| Glassdoor (scraper) | Glassdoor | Employee reviews |

---

### Story 50.4: News & Content Aggregation APIs (5 pts)
**Task:** Diversify news sources beyond current NewsAPI

**Acceptance Criteria:**
- [ ] 3-5 additional news APIs integrated
- [ ] Multi-source news aggregation
- [ ] Duplicate detection across sources
- [ ] Source quality weighting
- [ ] Geographic coverage expansion

**Target APIs:**
| API | Coverage | Notes |
|-----|----------|-------|
| GNews | Global | Google News alternative |
| Currents API | Global | News aggregator |
| Newscatcher | Global | 70,000+ sources |
| Event Registry | Global | Event extraction |
| Aylien News | Global | NLP-enriched news |

---

### Story 50.5: Lead Generation & Discovery APIs (5 pts)
**Task:** Enhance company discovery with lead generation APIs

**Acceptance Criteria:**
- [ ] 3-5 company discovery APIs integrated
- [ ] Competitor identification enhanced
- [ ] Market expansion suggestions
- [ ] Contact data (where available)
- [ ] Integration with discovery pipeline

**Target APIs:**
| API | Use Case | Coverage |
|-----|----------|----------|
| Clearbit | Company enrichment | Global |
| ZoomInfo (if API available) | B2B data | US/EU |
| Apollo.io | Company discovery | Global |
| Hunter.io | Email discovery | Global |
| BuiltWith | Technology detection | Global |

---

## Definition of Done

- [ ] 50+ OpenClaw APIs evaluated and catalogued
- [ ] 20+ new APIs integrated and tested
- [ ] Jobs/hiring signals expanded (EPIC-043.3)
- [ ] Social sentiment monitoring operational
- [ ] News aggregation diversified
- [ ] Company discovery enhanced
- [ ] All integrations follow BaseDataSourceAdapter pattern
- [ ] Documentation updated with new sources

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API reliability issues | High | Medium | Multiple sources, fallback chains |
| Rate limiting | High | Medium | Caching, queue management |
| Data quality variation | Medium | Medium | Quality scoring, source weighting |
| API deprecation | Medium | Medium | Monitoring, abstraction layer |
| Cost overruns | Medium | High | Budget tracking, usage alerts |

---

## Resources

- **Developers:** 2 backend engineers
- **Budget:** $500-2000/month for API subscriptions
- **Time:** 3 weeks
- **Dependencies:** EPIC-049 (catalog framework)

---

## Cost Estimates

| API Category | APIs | Est. Monthly Cost |
|--------------|------|-------------------|
| Jobs | 5-8 | $200-500 |
| Social | 5-8 | $300-800 |
| News | 3-5 | $100-300 |
| Discovery | 3-5 | $200-500 |
| **Total** | **20+** | **$800-2100** |

---

*Epic created from OpenClaw API list analysis*
