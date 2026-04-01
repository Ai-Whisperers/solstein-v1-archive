# OSINT Implementation Guide for Solstein

> **Open Source Intelligence (OSINT) Strategy for Competitive Intelligence**
>
> This document outlines how to implement comprehensive OSINT capabilities into the Solstein platform for enhanced PE/VC due diligence.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current OSINT State](#current-osint-state)
3. [OSINT Gaps Analysis](#osint-gaps-analysis)
4. [Recommended OSINT Architecture](#recommended-osint-architecture)
5. [Phase 1: Infrastructure Intelligence](#phase-1-infrastructure-intelligence)
6. [Phase 2: Corporate Network Intelligence](#phase-2-corporate-network-intelligence)
7. [Phase 3: People Intelligence (SOCMINT)](#phase-3-people-intelligence-socmint)
8. [Phase 4: Dark Web & Security Intelligence](#phase-4-dark-web--security-intelligence)
9. [Phase 5: Legal & Regulatory Intelligence](#phase-5-legal--regulatory-intelligence)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Data Quality & Validation](#data-quality--validation)
12. [Compliance & Legal Considerations](#compliance--legal-considerations)

---

## Executive Summary

### What is OSINT for PE/VC?

OSINT (Open Source Intelligence) is the collection and analysis of publicly available information to support investment decisions. For Solstein, OSINT extends beyond traditional financial data to include:

- **Technical footprints** (infrastructure, security posture)
- **Digital presence** (social media, reviews, sentiment)
- **Corporate networks** (subsidiaries, beneficial ownership)
- **People intelligence** (key personnel, hiring patterns)
- **Risk signals** (litigation, breaches, sanctions)

### Why OSINT Matters for Solstein

| Current Gap | Business Impact | OSINT Solution |
|-------------|----------------|----------------|
| No infrastructure scanning | Can't assess tech maturity | Shodan/Censys integration |
| No email pattern discovery | Can't verify corporate legitimacy | Hunter.io/RocketReach |
| No dark web monitoring | Miss data breach risks | HaveIBeenPwned/SpyCloud |
| No litigation tracking | Miss legal risks | PACER/CourtListener |
| No social media sentiment | Miss reputation risks | Brandwatch/Sprinklr |

### ROI Calculation

| OSINT Investment | Cost | Value |
|-----------------|------|-------|
| Infrastructure APIs | $500-2,000/mo | Detect tech debt, security risks |
| People Intelligence | $300-1,000/mo | Verify management quality |
| Security Monitoring | $200-500/mo | Avoid data breach liabilities |
| Legal Tracking | $100-300/mo | Early litigation warning |
| **Total** | **$1,100-3,800/mo** | **Comprehensive risk assessment** |

---

## Current OSINT State

### Existing OSINT Capabilities

Solstein already has foundational OSINT capabilities:

| Category | Current Implementation | Data Sources |
|----------|----------------------|--------------|
| **Financial OSINT** | ✅ Strong | Yahoo Finance, SEC EDGAR, Companies House |
| **News OSINT** | ✅ Good | NewsAPI, Exa AI, web search |
| **Technical OSINT** | ⚠️ Basic | GitHub, website scraping |
| **Company Registry** | ⚠️ Limited | UK only (Companies House) |
| **People OSINT** | ❌ Missing | News-derived only (no direct LinkedIn) |
| **Infrastructure** | ❌ Missing | No scanning capabilities |
| **Security** | ❌ Missing | No breach monitoring |
| **Legal** | ❌ Missing | No litigation tracking |

### Current OSINT Architecture

```
Current Data Flow:
┌──────────────────────────────────────────────────────┐
│  Discovery Sources                              │
│  • Static Catalog (hardcoded)                   │
│  • Web Search (Exa/DDG/Google)                  │
│  • Competitor JSON                              │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│  Enrichment Sources                             │
│  • Yahoo Finance (market data)                  │
│  • SEC EDGAR (US financials)                    │
│  • Companies House (UK registry)                │
│  • NewsAPI (news/sentiment)                     │
│  • GitHub (technical)                           │
│  • Website Scraping (products/tech)             │
│  • PatentsView (IP)                             │
│  • Crunchbase (funding - optional)              │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│  Aggregation & Validation                       │
│  • DefaultFactAggregator                        │
│  • ConflictResolution                           │
│  • SourceAuthority (confidence)                 │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│  Company Profile                                │
│  • Aggregated financials                        │
│  • Technical signals                            │
│  • News sentiment                               │
│  • Confidence scores                            │
└──────────────────────────────────────────────────────┘
```

---

## OSINT Gaps Analysis

### Critical Gaps (Missing Capabilities)

#### 1. Infrastructure Intelligence (MISSING)
**Current State:** Basic website scraping only

**What's Missing:**
- Subdomain enumeration
- Technology fingerprinting (beyond keyword matching)
- SSL certificate analysis
- DNS history
- Cloud infrastructure detection
- Security posture assessment

**PE/VC Impact:**
- Can't assess technical maturity accurately
- Missing security risk indicators
- No cloud adoption metrics

**Recommended Solutions:**
| Tool | Purpose | Cost |
|------|---------|------|
| Shodan | Internet-facing asset discovery | $59/mo |
| SecurityTrails | DNS history and subdomain enum | $50/mo |
| BuiltWith | Technology detection | $295/mo |
| Censys | Certificate and host analysis | Free tier |

#### 2. People Intelligence - SOCMINT (MISSING)
**Current State:** News-derived LinkedIn signals only (0.60 confidence)

**What's Missing:**
- Direct LinkedIn data (headcount, growth, skills)
- Key personnel backgrounds
- Email pattern verification
- Professional network analysis

**PE/VC Impact:**
- Can't verify management quality
- No hiring velocity metrics
- Missing leadership stability signals

**Recommended Solutions:**
| Tool | Purpose | Cost |
|------|---------|------|
| Proxycurl | LinkedIn API alternative | Pay-per-use |
| Hunter.io | Email pattern discovery | $49/mo |
| RocketReach | Contact enrichment | $59/mo |
| Clearbit | Person/company enrichment | $99/mo |

#### 3. Dark Web & Breach Intelligence (MISSING)
**Current State:** No monitoring

**What's Missing:**
- Data breach notifications
- Leaked credential detection
- Dark web mentions
- Compromised asset tracking

**PE/VC Impact:**
- Miss cybersecurity liabilities
- No data breach history
- Underestimate security risks

**Recommended Solutions:**
| Tool | Purpose | Cost |
|------|---------|------|
| HaveIBeenPwned | Breach notification | Free-$500/mo |
| SpyCloud | Dark web monitoring | Enterprise |
| DeHashed | Leaked credentials | $20/mo |

#### 4. Legal & Regulatory Intelligence (MISSING)
**Current State:** No tracking

**What's Missing:**
- Litigation history
- Regulatory enforcement actions
- Sanctions list screening
- Bankruptcy filings

**PE/VC Impact:**
- Miss legal risks
- No regulatory compliance view
- Underestimate liability exposure

**Recommended Solutions:**
| Tool | Purpose | Cost |
|------|---------|------|
| PACER | US court records | $0.10/page |
| CourtListener | Legal database | Free |
| OpenSanctions | Sanctions screening | Free |
| Sayari | Trade/enforcement data | Enterprise |

#### 5. Corporate Network Intelligence (LIMITED)
**Current State:** UK only (Companies House)

**What's Missing:**
- Global company registry coverage
- Beneficial ownership data
- Parent/subsidiary relationships
- Ultimate beneficial owner (UBO) tracking

**PE/VC Impact:**
- Can't map corporate structures
- Miss hidden ownership
- No global coverage

**Recommended Solutions:**
| Tool | Purpose | Cost |
|------|---------|------|
| OpenCorporates | Global registries | Free-$500/mo |
| OpenOwnership | UBO data | Free |
| Orbis | Bureau van Dijk | Enterprise |

---

## Recommended OSINT Architecture

### Enhanced OSINT Data Flow

```
New OSINT Sources to Add:

Phase 1: Infrastructure Intelligence
┌──────────────────────────────────────────────────────┐
│  Infrastructure OSINT                           │
│  • ShodanAdapter                                │
│  • SecurityTrailsAdapter                        │
│  • BuiltWithAdapter (enhanced)                  │
│  • CensysAdapter                                │
└──────────────────────────────────────────────────────┘

Phase 2: Corporate Network
┌──────────────────────────────────────────────────────┐
│  Corporate Network OSINT                        │
│  • OpenCorporatesAdapter                        │
│  • OpenOwnershipAdapter                         │
│  • SayariAdapter (if budget)                    │
└──────────────────────────────────────────────────────┘

Phase 3: People Intelligence
┌──────────────────────────────────────────────────────┐
│  People OSINT (SOCMINT)                         │
│  • ProxycurlAdapter (LinkedIn data)             │
│  • HunterIOAdapter (email patterns)             │
│  • ClearbitAdapter (enrichment)                 │
└──────────────────────────────────────────────────────┘

Phase 4: Security Intelligence
┌──────────────────────────────────────────────────────┐
│  Security OSINT                                 │
│  • HaveIBeenPwnedAdapter                        │
│  • VirusTotalAdapter                            │
│  • URLScanAdapter                               │
└──────────────────────────────────────────────────────┘

Phase 5: Legal Intelligence
┌──────────────────────────────────────────────────────┐
│  Legal OSINT                                    │
│  • PACERAdapter                                 │
│  • CourtListenerAdapter                         │
│  • OpenSanctionsAdapter                         │
└──────────────────────────────────────────────────────┘
```

### OSINT Signal Types for Solstein

Each OSINT source should extract specific signals:

| OSINT Category | Signals Extracted | Scoring Impact |
|----------------|-------------------|----------------|
| **Infrastructure** | Subdomain count, SSL grade, CDN usage, Cloud provider | Technical Maturity Score |
| **Security** | Breach count, credential leaks, malware detection | Risk Score |
| **People** | Headcount growth, AI talent %, leadership tenure | Competitive Position Score |
| **Corporate** | Subsidiary count, UBO complexity, global footprint | Financial Health Score |
| **Legal** | Litigation count, enforcement actions, sanctions | Risk Score |

---

## Phase 1: Infrastructure Intelligence

### 1.1 Shodan Integration

**Purpose:** Discover internet-facing assets and security posture

**Data Provided:**
- Open ports and services
- Technology banners
- SSL certificate details
- Geolocation of servers
- Known vulnerabilities (CVEs)

**PE/VC Use Cases:**
- Assess technical infrastructure maturity
- Identify security exposure
- Detect cloud adoption (AWS/Azure/GCP)

**Implementation:**

```python
# adapters/enrichment/shodan_adapter.py

class ShodanAdapter(BaseRefreshConnector):
    """Shodan OSINT adapter for infrastructure discovery."""

    def __init__(self, api_key: str, db_manager=None):
        super().__init__(
            source_name="shodan",
            source_type="infrastructure",
            db_manager=db_manager,
            confidence=0.75,
        )
        self.api_key = api_key
        self.client = shodan.Shodan(api_key)

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None) -> RawDataSource:
        """Enrich with Shodan data."""
        if not website:
            return self._empty_source(company_id)

        domain = self._extract_domain(website)

        try:
            # Search for host information
            host_data = self.client.search(f"hostname:{domain}")

            # Analyze SSL certificates
            ssl_data = self._analyze_ssl(domain)

            # Extract signals
            data = {
                "total_hosts": host_data['total'],
                "open_ports": self._extract_ports(host_data),
                "technologies": self._extract_tech(host_data),
                "ssl_grade": ssl_data.get('grade'),
                "cloud_provider": self._detect_cloud(host_data),
                "vulnerabilities": self._extract_cves(host_data),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                fetch_timestamp=datetime.now(),
                data=data,
                metadata={"domain": domain, "hosts_found": data["total_hosts"]},
            )
        except Exception as e:
            logger.error(f"Shodan enrichment failed for {company_name}: {e}")
            return self._empty_source(company_id)
```

**Configuration:**
```bash
# .env
SHODAN_API_KEY=your_shodan_key_here
```

**Pricing:**
- Freelancer: $59/month (10,000 search results/month)
- Small Business: $299/month (100,000 search results/month)
- Enterprise: Custom pricing

---

### 1.2 SecurityTrails Integration

**Purpose:** DNS history and subdomain enumeration

**Data Provided:**
- Historical DNS records
- Subdomain enumeration
- WHOIS history
- IP and domain associations

**PE/VC Use Cases:**
- Map digital footprint
- Assess infrastructure growth
- Detect shadow IT

**Implementation:**

```python
# adapters/enrichment/securitytrails_adapter.py

class SecurityTrailsAdapter(BaseRefreshConnector):
    """SecurityTrails adapter for DNS intelligence."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None) -> RawDataSource:
        if not website:
            return self._empty_source(company_id)

        domain = self._extract_domain(website)

        try:
            # Get subdomains
            subdomains = self._get_subdomains(domain)

            # Get DNS history
            dns_history = self._get_dns_history(domain)

            # Get WHOIS history
            whois_history = self._get_whois_history(domain)

            data = {
                "subdomain_count": len(subdomains),
                "subdomains": subdomains[:50],  # Top 50
                "dns_changes_90d": len([h for h in dns_history
                                       if self._within_90d(h['date'])]),
                "domain_age_days": self._calculate_domain_age(whois_history),
                "registrar": whois_history[0].get('registrar') if whois_history else None,
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
                metadata={"domain": domain},
            )
        except Exception as e:
            logger.error(f"SecurityTrails failed: {e}")
            return self._empty_source(company_id)
```

**Pricing:**
- Starter: $50/month (50,000 API calls)
- Business: $200/month (250,000 API calls)
- Enterprise: Custom

---

### 1.3 Enhanced BuiltWith Integration

**Current State:** Basic tech keyword matching

**Enhancement:** Full BuiltWith API integration

```python
# adapters/enrichment/builtwith_adapter.py

class BuiltWithAdapter(BaseRefreshConnector):
    """BuiltWith API adapter for technology detection."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None) -> RawDataSource:
        if not website:
            return self._empty_source(company_id)

        try:
            result = self._call_builtwith_api(website)

            data = {
                "technologies": self._extract_technologies(result),
                "tech_categories": self._categorize_tech(result),
                "ecommerce_platform": self._detect_ecommerce(result),
                "analytics_tools": self._detect_analytics(result),
                "marketing_stack": self._detect_marketing(result),
                "modernity_score": self._calculate_modernity(result),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
            )
        except Exception as e:
            logger.error(f"BuiltWith failed: {e}")
            return self._empty_source(company_id)

    def _calculate_modernity(self, result: dict) -> float:
        """Calculate tech modernity score (0-1)."""
        techs = result.get('technologies', [])

        modern_indicators = [
            'react', 'vue', 'angular', 'kubernetes', 'docker',
            'aws', 'gcp', 'azure', 'serverless', 'graphql'
        ]

        legacy_indicators = [
            'jquery', 'php', 'wordpress', 'drupal', 'java-ee'
        ]

        modern_count = sum(1 for t in techs if any(m in t.lower() for m in modern_indicators))
        legacy_count = sum(1 for t in techs if any(l in t.lower() for l in legacy_indicators))

        if modern_count + legacy_count == 0:
            return 0.5

        return modern_count / (modern_count + legacy_count)
```

---

## Phase 2: Corporate Network Intelligence

### 2.1 OpenCorporates Integration

**Purpose:** Global company registry data

**Coverage:** 200M+ companies, 140+ jurisdictions

**Data Provided:**
- Company registration details
- Filing history
- Director information
- Corporate groupings

**Implementation:**

```python
# adapters/enrichment/opencorporates_adapter.py

class OpenCorporatesAdapter(BaseRefreshConnector):
    """OpenCorporates adapter for global company data."""

    def discover(self, market: str, seed_company: str,
                 max_results: int = 50, extra_keywords: list | None = None):
        """Discover companies by market/sector."""
        try:
            # Search by jurisdiction and industry code
            jurisdiction = self._map_market_to_jurisdiction(market)
            sic_codes = self._map_keywords_to_sic(extra_keywords or [])

            results = self._search_companies(
                jurisdiction=jurisdiction,
                industry_codes=sic_codes,
                limit=max_results
            )

            candidates = []
            for company in results:
                candidates.append(DiscoveryCandidate(
                    company_id=f"oc_{company['company_number']}",
                    name=company['name'],
                    market=market,
                    industry=company.get('industry', 'Unknown'),
                    region=jurisdiction,
                    discovery_reason="opencorporates_registry",
                    source_links=[company['opencorporates_url']],
                ))

            return candidates
        except Exception as e:
            logger.error(f"OpenCorporates discovery failed: {e}")
            return []

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Enrich with registry data."""
        try:
            # Search by name
            search_results = self._search_by_name(company_name)

            if not search_results:
                return self._empty_source(company_id)

            company = search_results[0]
            company_number = company['company_number']
            jurisdiction = company['jurisdiction_code']

            # Get full company data
            full_data = self._get_company_data(jurisdiction, company_number)

            data = {
                "company_number": company_number,
                "jurisdiction": jurisdiction,
                "company_status": full_data.get('current_status'),
                "incorporation_date": full_data.get('incorporation_date'),
                "dissolution_date": full_data.get('dissolution_date'),
                "registered_address": full_data.get('registered_address'),
                "sic_codes": full_data.get('industry_codes', []),
                "officers": self._extract_officers(full_data),
                "filings": self._extract_filings(full_data),
                "corporate_group": self._extract_corporate_group(full_data),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
                metadata={"opencorporates_url": full_data.get('opencorporates_url')},
            )
        except Exception as e:
            logger.error(f"OpenCorporates enrichment failed: {e}")
            return self._empty_source(company_id)
```

**Pricing:**
- Free: 200 requests/day
- Researcher: $100/month (5,000 requests/day)
- Commercial: $500/month (50,000 requests/day)

---

## Phase 3: People Intelligence (SOCMINT)

### 3.1 Proxycurl Integration

**Purpose:** LinkedIn data without official API

**Data Provided:**
- Employee count and growth
- Skills distribution
- Hiring patterns
- Leadership profiles

**Implementation:**

```python
# adapters/enrichment/proxycurl_adapter.py

class ProxycurlAdapter(BaseRefreshConnector):
    """Proxycurl adapter for LinkedIn-derived people intelligence."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Enrich with LinkedIn data via Proxycurl."""
        try:
            # Search for company LinkedIn profile
            linkedin_url = self._find_linkedin_company(company_name, website)

            if not linkedin_url:
                return self._empty_source(company_id)

            # Get company profile
            company_profile = self._get_company_profile(linkedin_url)

            # Get employee count history (if available)
            employee_history = self._get_employee_history(linkedin_url)

            # Get recent hires
            recent_hires = self._get_recent_hires(linkedin_url, days=90)

            # Calculate hiring velocity
            hiring_velocity = self._calculate_hiring_velocity(employee_history)

            # Detect AI talent percentage
            ai_talent_pct = self._calculate_ai_talent_percentage(linkedin_url)

            data = {
                "linkedin_url": linkedin_url,
                "employee_count": company_profile.get('staff_count'),
                "employee_count_range": company_profile.get('staff_count_range'),
                "follower_count": company_profile.get('follower_count'),
                "founded_year": company_profile.get('founded_year'),
                "specialties": company_profile.get('specialties', []),
                "hiring_velocity": hiring_velocity,
                "ai_talent_percentage": ai_talent_pct,
                "recent_hires_count": len(recent_hires),
                "key_leadership": self._extract_leadership(company_profile),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
                metadata={"linkedin_url": linkedin_url},
            )
        except Exception as e:
            logger.error(f"Proxycurl enrichment failed: {e}")
            return self._empty_source(company_id)

    def _calculate_hiring_velocity(self, history: list) -> str:
        """Calculate hiring trend."""
        if len(history) < 2:
            return "unknown"

        recent = history[-1]['count']
        previous = history[0]['count']

        growth_rate = (recent - previous) / previous if previous > 0 else 0

        if growth_rate > 0.2:
            return "high_growth"
        elif growth_rate > 0.05:
            return "moderate_growth"
        elif growth_rate > -0.05:
            return "stable"
        else:
            return "declining"
```

**Pricing:**
- Pay-per-use: $0.01 per profile lookup
- Company profile: ~$0.02-0.05
- No monthly minimum

---

### 3.2 Hunter.io Integration

**Purpose:** Email pattern discovery and verification

**Data Provided:**
- Email pattern (e.g., {first}.{last}@company.com)
- Verified email addresses
- Department breakdown

**Implementation:**

```python
# adapters/enrichment/hunter_adapter.py

class HunterAdapter(BaseRefreshConnector):
    """Hunter.io adapter for email pattern discovery."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Discover email patterns."""
        if not website:
            return self._empty_source(company_id)

        domain = self._extract_domain(website)

        try:
            # Get domain information
            domain_info = self._call_hunter_api(f"domain-search", {"domain": domain})

            # Get email verification stats
            pattern = domain_info.get('pattern')
            emails = domain_info.get('emails', [])

            data = {
                "email_pattern": pattern,
                "pattern_confidence": domain_info.get('pattern_confidence'),
                "total_emails_found": domain_info.get('emails_count', 0),
                "department_breakdown": self._breakdown_by_department(emails),
                "seniority_breakdown": self._breakdown_by_seniority(emails),
                "sample_verified_emails": [
                    e['value'] for e in emails[:5]
                    if e.get('verification', {}).get('status') == 'valid'
                ],
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
            )
        except Exception as e:
            logger.error(f"Hunter.io failed: {e}")
            return self._empty_source(company_id)
```

**Pricing:**
- Free: 25 searches/month
- Starter: $49/month (500 searches)
- Growth: $99/month (2,500 searches)
- Pro: $199/month (10,000 searches)

---

## Phase 4: Dark Web & Security Intelligence

### 4.1 HaveIBeenPwned Integration

**Purpose:** Data breach monitoring

**Data Provided:**
- Breach history for domain
- Compromised account counts
- Breach severity and date

**Implementation:**

```python
# adapters/enrichment/hibp_adapter.py

class HaveIBeenPwnedAdapter(BaseRefreshConnector):
    """HaveIBeenPwned adapter for breach monitoring."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Check for data breaches."""
        if not website:
            return self._empty_source(company_id)

        domain = self._extract_domain(website)

        try:
            # Get breaches for domain
            breaches = self._get_domain_breaches(domain)

            # Calculate risk metrics
            total_accounts = sum(b.get('PwnCount', 0) for b in breaches)
            recent_breaches = [b for b in breaches
                             if self._is_recent(b.get('BreachDate'))]

            sensitive_breaches = [b for b in breaches
                                if self._is_sensitive(b)]

            data = {
                "breach_count": len(breaches),
                "total_compromised_accounts": total_accounts,
                "recent_breach_count": len(recent_breaches),
                "sensitive_breach_count": len(sensitive_breaches),
                "breach_history": [
                    {
                        "name": b.get('Name'),
                        "date": b.get('BreachDate'),
                        "accounts": b.get('PwnCount'),
                        "sensitivity": self._classify_sensitivity(b),
                        "data_classes": b.get('DataClasses', []),
                    }
                    for b in breaches[:10]  # Top 10
                ],
                "risk_level": self._calculate_breach_risk(breaches),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
            )
        except Exception as e:
            logger.error(f"HIBP failed: {e}")
            return self._empty_source(company_id)

    def _calculate_breach_risk(self, breaches: list) -> str:
        """Calculate overall breach risk."""
        if not breaches:
            return "low"

        recent_count = len([b for b in breaches if self._is_recent(b.get('BreachDate'))])
        sensitive_count = len([b for b in breaches if self._is_sensitive(b)])

        if sensitive_count > 0 and recent_count > 0:
            return "critical"
        elif sensitive_count > 0 or recent_count > 1:
            return "high"
        elif len(breaches) > 0:
            return "medium"
        else:
            return "low"
```

**Pricing:**
- Free: 1.5 second rate limit
- Paid: $3.50/month (unlimited, faster)

---

## Phase 5: Legal & Regulatory Intelligence

### 5.1 PACER Integration

**Purpose:** US federal court records

**Data Provided:**
- Litigation history
- Case types and outcomes
- Party information

**Implementation:**

```python
# adapters/enrichment/pacer_adapter.py

class PACERAdapter(BaseRefreshConnector):
    """PACER adapter for US court records."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Search litigation history."""
        try:
            # Search for cases involving company
            cases = self._search_cases(company_name)

            # Categorize cases
            case_summary = self._summarize_cases(cases)

            data = {
                "total_cases": len(cases),
                "cases_as_plaintiff": case_summary.get('plaintiff', 0),
                "cases_as_defendant": case_summary.get('defendant', 0),
                "open_cases": len([c for c in cases if c.get('status') == 'open']),
                "case_types": case_summary.get('types', {}),
                "recent_cases": [
                    {
                        "case_number": c.get('case_number'),
                        "title": c.get('title'),
                        "date_filed": c.get('date_filed'),
                        "court": c.get('court'),
                        "nature_of_suit": c.get('nature_of_suit'),
                    }
                    for c in cases[:10]
                ],
                "litigation_risk": self._assess_litigation_risk(cases),
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
            )
        except Exception as e:
            logger.error(f"PACER failed: {e}")
            return self._empty_source(company_id)
```

**Pricing:**
- $0.10 per page (search results)
- $0.10 per page (document retrieval)
- Quarterly fee: $30 (waived if usage > $30)

---

### 5.2 OpenSanctions Integration

**Purpose:** Sanctions and watchlist screening

**Data Provided:**
- Sanctions list matches
- Politically exposed persons (PEP)
- Criminal watchlists

**Implementation:**

```python
# adapters/enrichment/opensanctions_adapter.py

class OpenSanctionsAdapter(BaseRefreshConnector):
    """OpenSanctions adapter for compliance screening."""

    def enrich(self, company_id: str, company_name: str,
               ticker: str | None = None, website: str | None = None):
        """Screen for sanctions."""
        try:
            # Search entities
            entities = self._search_entities(company_name)

            # Check for exact and fuzzy matches
            matches = self._analyze_matches(entities, company_name)

            data = {
                "sanctions_matches": len([m for m in matches if m['type'] == 'sanction']),
                "pep_matches": len([m for m in matches if m['type'] == 'pep']),
                "watchlist_matches": len([m for m in matches if m['type'] == 'watchlist']),
                "match_details": [
                    {
                        "name": m.get('name'),
                        "type": m.get('type'),
                        "confidence": m.get('confidence'),
                        "source": m.get('source'),
                        "date": m.get('date'),
                    }
                    for m in matches[:5]
                ],
                "compliance_clear": len(matches) == 0,
            }

            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                data=data,
            )
        except Exception as e:
            logger.error(f"OpenSanctions failed: {e}")
            return self._empty_source(company_id)
```

**Pricing:**
- Free tier available
- Commercial: Contact for pricing

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up OSINT base adapter class
- [ ] Implement Shodan integration
- [ ] Add SecurityTrails integration
- [ ] Create OSINT signal extraction framework

### Phase 2: Corporate Intelligence (Weeks 3-4)
- [ ] Implement OpenCorporates integration
- [ ] Add OpenOwnership integration
- [ ] Expand geographic coverage

### Phase 3: People Intelligence (Weeks 5-6)
- [ ] Implement Proxycurl integration
- [ ] Add Hunter.io integration
- [ ] Create hiring velocity signals

### Phase 4: Security Intelligence (Weeks 7-8)
- [ ] Implement HaveIBeenPwned integration
- [ ] Add VirusTotal integration
- [ ] Create security risk scoring

### Phase 5: Legal Intelligence (Weeks 9-10)
- [ ] Implement PACER integration
- [ ] Add OpenSanctions integration
- [ ] Create litigation risk scoring

---

## Data Quality & Validation

### OSINT Confidence Scoring

| OSINT Source | Base Confidence | Factors Affecting Confidence |
|--------------|----------------|------------------------------|
| Shodan | 0.75 | Scan recency, data completeness |
| SecurityTrails | 0.80 | Historical accuracy, coverage |
| OpenCorporates | 0.90 | Government source recency |
| Proxycurl | 0.75 | Data freshness, coverage |
| Hunter.io | 0.70 | Pattern consistency |
| HaveIBeenPwned | 0.95 | Authoritative breach data |
| PACER | 0.95 | Official court records |

### Cross-Validation Strategy

```python
# Example: Validate employee count across sources
def validate_employee_count(sources: dict) -> tuple[int, float]:
    """
    Cross-validate employee count from multiple OSINT sources.
    Returns: (consensus_value, confidence_score)
    """
    values = []
    weights = []

    # Proxycurl (LinkedIn) - highest weight for people data
    if 'proxycurl' in sources:
        values.append(sources['proxycurl']['employee_count'])
        weights.append(0.4)

    # OpenCorporates (registry filings)
    if 'opencorporates' in sources:
        values.append(sources['opencorporates'].get('employee_count'))
        weights.append(0.3)

    # Website (careers page mentions)
    if 'website' in sources:
        values.append(sources['website'].get('employee_count_estimate'))
        weights.append(0.2)

    # News (hiring articles)
    if 'news' in sources:
        values.append(sources['news'].get('employee_count_mention'))
        weights.append(0.1)

    # Calculate weighted average
    if not values:
        return (None, 0.0)

    # Remove outliers (values >2 std dev from mean)
    clean_values = _remove_outliers(values)

    # Weighted average
    total_weight = sum(weights[:len(clean_values)])
    weighted_sum = sum(v * w for v, w in zip(clean_values, weights[:len(clean_values)]))

    consensus = weighted_sum / total_weight if total_weight > 0 else None

    # Confidence based on agreement
    agreement_score = _calculate_agreement(clean_values)
    source_coverage = len(clean_values) / 4  # Max 4 sources

    confidence = agreement_score * source_coverage

    return (consensus, min(confidence, 1.0))
```

---

## Compliance & Legal Considerations

### Legal Framework

1. **GDPR Compliance (EU)**
   - Only collect publicly available data
   - Respect robots.txt and terms of service
   - Implement data retention limits
   - Allow data deletion requests

2. **CFAA (US Computer Fraud and Abuse Act)**
   - Don't circumvent access controls
   - Respect rate limits
   - Don't scrape behind authentication

3. **Terms of Service Compliance**
   - Review API terms for each OSINT source
   - Implement required attribution
   - Respect usage limits

### Ethical Guidelines

1. **Purpose Limitation**
   - Use OSINT only for legitimate due diligence
   - Don't stalk individuals
   - Respect privacy expectations

2. **Data Minimization**
   - Only collect relevant data
   - Delete data when no longer needed
   - Anonymize where possible

3. **Transparency**
   - Document OSINT sources in audit trails
   - Explain data provenance to users
   - Allow data correction requests

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API Terms Violation | Review and comply with all API terms |
| Data Accuracy | Cross-validate all OSINT data |
| Privacy Complaints | Only collect public data, implement takedown process |
| Regulatory Action | Maintain compliance documentation |

---

## Summary

### Key Recommendations

1. **Start with Infrastructure OSINT** (Shodan, SecurityTrails)
   - High impact, reasonable cost
   - Clear technical value for PE/VC
   - Easy to implement

2. **Add People Intelligence** (Proxycurl)
   - Addresses critical gap
   - Pay-per-use pricing
   - Immediate hiring signal value

3. **Implement Security Monitoring** (HaveIBeenPwned)
   - Low cost, high value
   - Critical risk indicator
   - Simple API

4. **Expand Corporate Network** (OpenCorporates)
   - Free tier available
   - Global coverage
   - Registry authority

5. **Consider Legal OSINT** (PACER, OpenSanctions)
   - Compliance requirement
   - Risk identification
   - Enterprise value

### Budget Estimate

| Phase | Tools | Monthly Cost |
|-------|-------|--------------|
| Phase 1 | Shodan + SecurityTrails | $150-350 |
| Phase 2 | OpenCorporates (free tier) | $0-100 |
| Phase 3 | Proxycurl + Hunter | $200-500 |
| Phase 4 | HaveIBeenPwned + VirusTotal | $50-150 |
| Phase 5 | PACER + OpenSanctions | $100-300 |
| **Total** | | **$500-1,400/mo** |

### Expected ROI

- **Risk Avoidance:** Early detection of 1 bad investment pays for years of OSINT
- **Efficiency:** Automated OSINT reduces manual research time by 70%+
- **Competitive Edge:** Data competitors don't have
- **Compliance:** Meet institutional due diligence requirements

---

*For questions or implementation support, contact the Solstein engineering team.*
