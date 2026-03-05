# Solstein API Providers Guide

> **For Junior Developers** - Complete guide to obtaining and configuring all external API keys for the Solstein competitive intelligence platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Required APIs (Core Functionality)](#required-apis-core-functionality)
3. [Optional APIs (Enhanced Data)](#optional-apis-enhanced-data)
4. [LLM Providers (AI Analysis)](#llm-providers-ai-analysis)
5. [Recommended New APIs](#recommended-new-apis)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Solstein integrates with **27+ external APIs** across five categories:

| Category | Count | Purpose |
|----------|-------|---------|
| **Financial Data** | 5 | Stock prices, SEC filings, funding data |
| **Company Intelligence** | 5 | Company profiles, registry data, corporate structure |
| **Technical Signals** | 2 | GitHub activity, tech stack detection |
| **News & Media** | 4 | News coverage, sentiment analysis, web search |
| **LLM Providers** | 13 | AI analysis, scoring explanations |

### API Key Priority Matrix

| Priority | APIs | Impact |
|----------|------|--------|
| **P0 - Critical** | GitHub, NewsAPI, SEC EDGAR, Yahoo Finance | Platform won't function without these |
| **P1 - Important** | Companies House, Crunchbase, Exa | Significantly improves data quality |
| **P2 - Enhancement** | LinkedIn (Proxycurl), BuiltWith, PitchBook | Competitive differentiation |
| **P3 - Nice to Have** | Glassdoor, G2, OpenCorporates | Additional validation signals |

---

## Required APIs (Core Functionality)

### 1. GitHub API

**Purpose:** Technical due diligence - repository metrics, commit activity, open source presence

**What it provides:**
- Repository count and activity
- Programming languages used
- Commit frequency (engineering velocity)
- Stars and forks (developer interest)
- Issue tracking activity

**Used in:**
- `src/solstein/data/connectors/github_connector.py`
- `src/solstein/infrastructure/connectors/github_refresh.py`
- Growth Score component (technical signals)

---

#### Step-by-Step: Getting Your GitHub Token

**Prerequisites:**
- GitHub account (personal is fine, business recommended)
- 5 minutes

**Step 1: Create/Access GitHub Account**
1. Go to https://github.com
2. Click "Sign up" (or "Sign in" if you have an account)
3. Use your **business email** (e.g., `dev@ai-whisperers.com`)
4. Complete verification

**Step 2: Navigate to Developer Settings**
1. Click your profile picture (top right)
2. Select "Settings"
3. Scroll down and click "Developer settings" (left sidebar)
4. Click "Personal access tokens" → "Tokens (classic)"

**Step 3: Generate Token**
1. Click "Generate new token (classic)"
2. You may need to re-enter your password
3. Fill in the form:
   - **Note:** `Solstein API Access`
   - **Expiration:** Select "No expiration" (or 90 days for security)
   - **Scopes:** Check these boxes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `read:org` (Read org and team membership)
     - ✅ `read:user` (Read user profile data)
     - ✅ `read:project` (Read project boards)

4. Click "Generate token" at the bottom

**Step 4: Save Your Token**
⚠️ **CRITICAL:** The token is shown ONCE. Copy it immediately.

1. Click the copy icon next to the token
2. Save it in your password manager
3. You'll use this as `GITHUB_TOKEN` in your `.env` file

**Step 5: Test Your Token**
```bash
curl -H "Authorization: token YOUR_TOKEN_HERE" https://api.github.com/user
```

Should return your GitHub user information.

**Rate Limits:**
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour
- Solstein uses authenticated requests only

---

### 2. NewsAPI.org

**Purpose:** News coverage analysis - sentiment detection, event identification

**What it provides:**
- News articles mentioning target companies
- Publication dates and sources
- Article titles and descriptions
- Sentiment analysis input

**Used in:**
- `src/solstein/data/additional_sources.py`
- `src/solstein/data/connectors/news_signal_detector.py`
- News signal extraction

---

#### Step-by-Step: Getting Your NewsAPI Key

**Prerequisites:**
- Business email recommended
- 3 minutes

**Step 1: Create Account**
1. Go to https://newsapi.org
2. Click "Get API Key" (top right)
3. Enter your business email: `dev@ai-whisperers.com`
4. Create a password
5. Click "Sign up"

**Step 2: Verify Email**
1. Check your email inbox
2. Click the verification link from NewsAPI
3. You'll be redirected to your dashboard

**Step 3: Get Your API Key**
1. On the dashboard, your API key is displayed prominently
2. It looks like: `1234567890abcdef1234567890abcdef`
3. Click the copy button

**Step 4: Understand Your Plan**
- **Developer (Free):** 100 requests/day, 1 month history
- **Business ($449/month):** 1M requests/day, full archive, commercial use

For development, start with the free plan. Upgrade when going to production.

**Step 5: Test Your Key**
```bash
curl "https://newsapi.org/v2/everything?q=Apple&apiKey=YOUR_API_KEY"
```

Should return JSON with news articles about Apple.

---

### 3. SEC EDGAR (No API Key Required)

**Purpose:** US public company financial statements - 10-K (annual) and 10-Q (quarterly)

**What it provides:**
- Revenue, net income, EBITDA
- Balance sheet data
- Cash flow statements
- Risk factors and management discussion

**Used in:**
- `src/solstein/data/connectors/sec_edgar_connector.py`
- `src/solstein/infrastructure/connectors/sec_edgar_refresh.py`
- Financial Health Score (authoritative source)

---

#### Setup Instructions

**Good News:** No API key required! SEC EDGAR is public data.

**Step 1: Configure User Agent (Required)**
The SEC requires a custom User-Agent header.

1. Open your `.env` file
2. Add:
```bash
SEC_USER_AGENT="Solstein/0.1 (contact: dev@ai-whisperers.com)"
```

**Step 2: No Additional Setup**
The connector uses the `edgar` Python library which handles:
- Filing downloads
- XBRL parsing
- Financial statement extraction

**Rate Limits:**
- 10 requests/second maximum
- Solstein implements backoff and retry logic

**Data Coverage:**
- All US public companies
- Filings from 1994 to present
- 10-K (annual), 10-Q (quarterly), 8-K (current reports)

---

### 4. Yahoo Finance (No API Key Required)

**Purpose:** Market data for public companies - stock prices, market cap, P/E ratios

**What it provides:**
- Real-time stock prices
- Market capitalization
- P/E, P/S ratios
- EPS (earnings per share)
- Revenue and earnings estimates

**Used in:**
- `src/solstein/data/company_research.py`
- `src/solstein/data/fetchers.py`
- Market data normalization

---

#### Setup Instructions

**Good News:** No API key required! Uses the `yfinance` Python library.

**Step 1: Install Dependency**
```bash
pip install yfinance
```

**Step 2: Enable in Environment**
```bash
YAHOO_FINANCE_ENABLED=true
```

**Step 3: No Additional Configuration**
The library scrapes Yahoo Finance public pages.

**Data Coverage:**
- 100,000+ tickers globally
- 50+ exchanges
- Real-time and historical data

**Rate Limits:**
- Unofficial: ~2,000 requests/hour per IP
- Solstein implements caching to avoid limits

---

## Optional APIs (Enhanced Data)

### 5. Companies House API (UK Companies)

**Purpose:** UK company registry data - official filings, director information

**What it provides:**
- Company registration details
- Filing history
- Director appointments/resignations
- SIC codes (industry classification)
- Annual accounts dates

**Used in:**
- `src/solstein/data/connectors/companies_house_connector.py`
- UK company verification

**Confidence Score:** 0.93 (authoritative government source)

---

#### Step-by-Step: Getting Your Companies House API Key

**Prerequisites:**
- Business email required
- UK focus (if analyzing UK companies)

**Step 1: Create Account**
1. Go to https://developer.company-information.service.gov.uk
2. Click "Sign in / Register"
3. Select "Create an account"
4. Enter your business email: `dev@ai-whisperers.com`
5. Create a password
6. Complete CAPTCHA
7. Click "Continue"

**Step 2: Verify Email**
1. Check your email for verification link
2. Click the link within 24 hours
3. You'll be redirected to the developer hub

**Step 3: Create an Application**
1. Click "Create an application" on the dashboard
2. Fill in details:
   - **Application name:** `Solstein Competitive Intelligence`
   - **Description:** `PE/VC intelligence platform for company analysis`
   - **Environment:** Select "Live" (not test)
3. Click "Create"

**Step 4: Get Your API Key**
1. Your application details page will show:
   - **API Key:** A long alphanumeric string
   - **API Secret:** (not needed for REST API)
2. Copy the **API Key**

**Step 5: Test Your Key**
```bash
curl -uYOUR_API_KEY: "https://api.company-information.service.gov.uk/company/00000006"
```

Note the colon after the API key - Companies House uses HTTP Basic Auth with the key as username.

**Rate Limits:**
- 600 requests/5 minutes
- Sufficient for most use cases

**Data Coverage:**
- All UK registered companies
- 4+ million companies
- Updated daily

---

### 6. Crunchbase API (Funding Data)

**Purpose:** Startup funding data - rounds, valuations, investors

**What it provides:**
- Funding round amounts and dates
- Investor syndicates
- Pre/post-money valuations
- Acquisition data
- Founder backgrounds

**Used in:**
- `src/solstein/data/additional_sources.py`
- `src/solstein/infrastructure/connectors/funding_refresh.py`

**Fallback:** News-based funding detection if no API key

---

#### Step-by-Step: Getting Your Crunchbase API Access

**Prerequisites:**
- Business email required
- Company website
- Can take 1-2 weeks for approval

**Step 1: Apply for Access**
1. Go to https://data.crunchbase.com
2. Click "Get Started" or "Contact Sales"
3. Fill out the application form:
   - **Name:** Your full name
   - **Email:** Business email (dev@ai-whisperers.com)
   - **Company:** AI Whisperers
   - **Company Website:** https://ai-whisperers.com
   - **Use Case:** Describe:
     ```
     We are building a competitive intelligence platform for
     private equity and venture capital firms. We need funding
     data to score and classify companies for investment
     opportunities. Data will be used internally for analysis
     and not resold.
     ```
   - **Expected Volume:** Estimate your API calls/month
   - **Data Types:** Check "Funding Rounds", "Investments", "Acquisitions"

4. Submit the application

**Step 2: Wait for Approval**
- Crunchbase reviews applications manually
- Typical response time: 3-7 business days
- You may receive follow-up questions

**Step 3: Review Pricing**
Crunchbase doesn't publish pricing. Typical ranges:
- **Basic:** $500-1,000/month
- **Pro:** $2,000-5,000/month
- **Enterprise:** $10,000+/month

**Step 4: Sign Contract**
1. Review the API License Agreement
2. Sign digitally
3. Provide payment information

**Step 5: Get API Key**
1. Log into your Crunchbase developer account
2. Navigate to "API Keys"
3. Generate a new key
4. Copy the key (starts with `cb_`)

**Step 6: Test Your Key**
```bash
curl -H "X-cb-user-key: YOUR_API_KEY" \
  "https://api.crunchbase.com/api/v4/entities/organizations/facebook"
```

**Without API Key:**
Solstein falls back to news-based funding detection (confidence: 0.30 vs 0.70 with API).

---

### 7. Exa AI (Web Search)

**Purpose:** Deep web search and company discovery

**What it provides:**
- Semantic web search
- Company discovery
- Source provenance tracking
- Content similarity matching

**Used in:**
- `src/solstein/data/web_search_client.py`
- Company discovery pipeline

---

#### Step-by-Step: Getting Your Exa API Key

**Prerequisites:**
- Business email
- Credit card (for paid plans)

**Step 1: Create Account**
1. Go to https://exa.ai
2. Click "Get Started" or "Sign Up"
3. Enter your business email: `dev@ai-whisperers.com`
4. Create a password
5. Click "Create Account"

**Step 2: Verify Email**
1. Check your inbox for verification email
2. Click the verification link

**Step 3: Access Dashboard**
1. Log in at https://dashboard.exa.ai
2. You'll see your API key on the main dashboard
3. It looks like: `exa_1234567890abcdef1234567890abcdef`

**Step 4: Review Pricing**
- **Free Tier:** 100 requests/month
- **Pro ($100/month):** 10,000 requests/month
- **Enterprise:** Custom pricing

For development, start with free tier. Production will likely need Pro.

**Step 5: Add Payment Method (if upgrading)**
1. Go to "Billing" in dashboard
2. Add credit card
3. Select plan

**Step 6: Test Your Key**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST https://api.exa.ai/search \
  -d '{"query": "AI companies in Berlin"}'
```

**Rate Limits:**
- Based on your plan tier
- Free: 100/month
- Pro: 10,000/month

---

## LLM Providers (AI Analysis)

Solstein supports **13 LLM providers** with automatic failover. Only configure the ones you want to use.

### Recommended Priority

| Priority | Provider | Why |
|----------|----------|-----|
| 1 | **Ollama (Local)** | Free, private, no rate limits |
| 2 | **Groq** | Fast, cheap, reliable |
| 3 | **OpenAI** | Best quality, higher cost |
| 4 | **Anthropic** | Excellent reasoning |
| 5 | **Fireworks** | Cost-effective fallback |

---

### 8. OpenAI (Optional but Recommended)

**Purpose:** High-quality AI analysis and structured output

**What it provides:**
- GPT-4o for complex analysis
- GPT-4o-mini for cost-effective tasks
- Structured JSON output
- Best-in-class reasoning

**Used in:**
- `src/solstein/llm/enhanced_client.py`
- Scoring explanations
- Signal extraction

---

#### Step-by-Step: Getting Your OpenAI API Key

**Step 1: Create Account**
1. Go to https://platform.openai.com
2. Click "Sign up"
3. Use business email: `dev@ai-whisperers.com`
4. Verify your phone number
5. Complete email verification

**Step 2: Add Payment Method**
1. Log into platform.openai.com
2. Click your profile (top right) → "Billing"
3. Click "Add payment method"
4. Enter credit card details
5. Set a usage limit (recommended: $100-500/month for safety)

**Step 3: Create API Key**
1. Go to "API Keys" in the left sidebar
2. Click "Create new secret key"
3. Name it: `Solstein Production`
4. Copy the key (starts with `sk-`)

**Step 4: Test Your Key**
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Pricing:**
- GPT-4o-mini: $0.00015/1K input tokens
- GPT-4o: $0.005/1K input tokens
- Typical Solstein analysis: $0.01-0.10 per company

---

### 9. Groq (Recommended - Fast & Cheap)

**Purpose:** Fast inference at low cost

**What it provides:**
- Llama 3.3 70B
- Near-instant responses
- 50%+ cheaper than OpenAI

---

#### Step-by-Step: Getting Your Groq API Key

**Step 1: Create Account**
1. Go to https://console.groq.com
2. Click "Sign Up"
3. Use business email
4. Verify email

**Step 2: Get API Key**
1. Log into console.groq.com
2. Go to "API Keys" in left sidebar
3. Click "Create API Key"
4. Name: `Solstein`
5. Copy the key (starts with `gsk_`)

**Step 3: Test Your Key**
```bash
curl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Pricing:**
- Llama 3.3 70B: $0.00059/1K input tokens
- Free tier: $200 credit to start

---

### 10. Ollama (Local - Free)

**Purpose:** Free, private local LLM inference

**What it provides:**
- Runs entirely on your servers
- No API costs
- No data leaves your infrastructure
- Llama 3.2 by default

**Used in:**
- `src/solstein/llm/enhanced_client.py`
- Privacy-sensitive deployments

---

#### Step-by-Step: Setting Up Ollama

**Step 1: Install Ollama**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

**Step 2: Pull Required Model**
```bash
ollama pull llama3.2
```

**Step 3: Start Ollama Server**
```bash
ollama serve
```

By default, runs on `http://localhost:11434`

**Step 4: Configure Solstein**
```bash
# .env file
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

**Step 5: Test**
```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.2", "prompt": "Hello!"}'
```

**Hardware Requirements:**
- Minimum: 8GB RAM
- Recommended: 16GB+ RAM
- GPU optional but recommended for speed

---

### Other LLM Providers (Optional)

Configure any of these in your `.env` file if you want additional fallbacks:

| Provider | Signup URL | Key Format | Model |
|----------|-----------|------------|-------|
| **Fireworks** | https://fireworks.ai | `fw_...` | mixtral-8x22b |
| **Anthropic** | https://console.anthropic.com | `sk-ant-...` | claude-3-5-haiku |
| **Mistral** | https://console.mistral.ai | Standard API key | mistral-large |
| **DeepInfra** | https://deepinfra.com | Standard API key | Various |
| **Gemini** | https://ai.google.dev | Standard API key | gemini-pro |
| **NVIDIA NIM** | https://build.nvidia.com | Standard API key | Various |
| **Cerebras** | https://cerebras.ai | Standard API key | Various |
| **Kimi** | https://platform.moonshot.cn | Standard API key | moonshot |
| **SiliconFlow** | https://siliconflow.com | Standard API key | Qwen |
| **Alibaba** | https://dashscope.aliyun.com | Standard API key | qwen-plus |

---

## Recommended New APIs

These APIs are **NOT currently integrated** but are highly recommended for production deployments.

### 11. Proxycurl (LinkedIn Alternative) ⭐ HIGHLY RECOMMENDED

**Purpose:** Real LinkedIn data without official API access

**What it provides:**
- Employee count and growth trends
- Hiring velocity
- Skills distribution (AI/ML talent %)
- Leadership team profiles
- Job posting analysis

**Why it matters:** Solstein currently uses news-derived LinkedIn proxies (0.60 confidence). Proxycurl provides real data (0.80+ confidence).

---

#### Step-by-Step: Getting Your Proxycurl API Key

**Step 1: Create Account**
1. Go to https://nubela.co/proxycurl
2. Click "Get Started" or "Sign Up"
3. Enter business email: `dev@ai-whisperers.com`
4. Create password
5. Complete CAPTCHA
6. Click "Sign Up"

**Step 2: Verify Email**
1. Check inbox for verification email
2. Click verification link

**Step 3: Access Dashboard**
1. Log in at https://nubela.co/dashboard
2. Your API key is displayed on the dashboard
3. Looks like: `cL2xX...` (64 characters)

**Step 4: Add Credits**
Proxycurl is pay-per-use (no monthly fee):
- $0.01 per profile lookup
- Add credits via credit card
- Minimum: $10

1. Go to "Billing" in dashboard
2. Click "Add Credits"
3. Enter amount ($50-100 recommended to start)
4. Complete payment

**Step 5: Test Your Key**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://nubela.co/proxycurl/api/v2/linkedin?url=https://www.linkedin.com/in/williamhgates"
```

**Pricing:**
- Person profile API: $0.01/credit
- Company profile API: $0.02/credit
- Typical company enrichment: $0.05-0.10

---

### 12. BuiltWith (Tech Stack Detection)

**Purpose:** Detailed technology stack analysis

**What it provides:**
- Complete tech stack detection
- SaaS tool usage
- Cloud infrastructure detection
- Security posture assessment

**Why it matters:** Currently Solstein only does basic website scraping. BuiltWith provides authoritative tech stack data.

---

#### Step-by-Step: Getting BuiltWith Access

**Step 1: Create Account**
1. Go to https://builtwith.com
2. Click "Sign Up" (top right)
3. Enter business details
4. Use business email

**Step 2: Select Plan**
BuiltWith has multiple products:
- **Reports:** One-time lookups
- **API:** Programmatic access (what you need)
- **Leads:** Sales prospecting

For Solstein, you need the **API** plan.

**Step 3: Review Pricing**
- **API Free:** 1 request/day
- **API Basic:** $295/month - 500 requests/day
- **API Pro:** $495/month - 2,000 requests/day
- **API Enterprise:** $995/month - 10,000 requests/day

**Step 4: Subscribe**
1. Select your plan
2. Enter payment information
3. Complete subscription

**Step 5: Get API Key**
1. Go to your account dashboard
2. Navigate to "API Access"
3. Copy your API key

**Step 6: Test Your Key**
```bash
curl "https://api.builtwith.com/free1/api.json?KEY=YOUR_API_KEY&LOOKUP=example.com"
```

---

### 13. PitchBook (Private Market Data)

**Purpose:** Premium private company data - valuations, comparables, investor intelligence

**What it provides:**
- Precedent transaction data
- Valuation multiples
- Cap tables
- Investor dry powder tracking
- Private company financial estimates

**Why it matters:** Critical for PE/VC valuation work. No other source provides this data.

---

#### Step-by-Step: Getting PitchBook Access

**Step 1: Contact Sales**
PitchBook doesn't have self-service signup for API access.

1. Go to https://pitchbook.com/products/api-data-feed
2. Click "Contact Us" or "Request Demo"
3. Fill out the form:
   - **Name:** Your name
   - **Email:** Business email
   - **Company:** AI Whisperers
   - **Title:** Developer/Data Engineer
   - **Phone:** Your business phone
   - **Message:**
     ```
     We are building a competitive intelligence platform for
     private equity firms. We need API access to valuation data,
     precedent transactions, and investor information for
     automated company scoring.
     ```

**Step 2: Discovery Call**
- PitchBook sales team will schedule a call
- Discuss your use case
- Review data requirements
- Explain pricing (expect $10,000-50,000+/year)

**Step 3: Contract Negotiation**
- Review API License Agreement
- Negotiate pricing and terms
- Sign contract
- Typical process: 2-4 weeks

**Step 4: Technical Onboarding**
- PitchBook provides API documentation
- Technical integration support
- Test environment access

**Step 5: Production Access**
- Receive production API credentials
- Integration complete

**Pricing:**
- Not published publicly
- Expect: $10,000-50,000/year minimum
- Enterprise deals can exceed $100,000/year

---

### 14. OpenFIGI (Free - Identifier Resolution)

**Purpose:** Standard identifier mapping

**What it provides:**
- FIGI (Financial Instrument Global Identifier)
- Ticker ↔ CIK ↔ ISIN ↔ LEI mapping
- Corporate actions data

**Why it matters:** Eliminates duplicate companies when aggregating from multiple sources (SEC, Yahoo, news).

---

#### Step-by-Step: Getting OpenFIGI API Key

**Step 1: Create Account**
1. Go to https://www.openfigi.com
2. Click "Get API Key" or "Sign Up"
3. Enter business email
4. Create password
5. Complete registration

**Step 2: Request API Key**
1. Log into your account
2. Go to "API" section
3. Click "Request API Key"
4. Fill out usage questionnaire:
   - **Use Case:** Company data aggregation and deduplication
   - **Expected Volume:** X requests/day
   - **Application Type:** Commercial data platform

**Step 3: Wait for Approval**
- Usually approved within 24-48 hours
- You'll receive email notification

**Step 4: Access API Key**
1. Log into dashboard
2. Go to "My API Keys"
3. Copy your key

**Step 5: Test Your Key**
```bash
curl -H "Content-Type: application/json" \
  -X POST https://api.openfigi.com/v3/mapping \
  -d '[{"idType":"TICKER","idValue":"AAPL"}]'
```

**Pricing:**
- **Free tier:** 500 requests/day
- **Paid tiers:** Contact sales for higher limits

---

### 15. OpenCorporates (Global Company Registry)

**Purpose:** Global company data beyond UK

**What it provides:**
- 200M+ companies across 140+ jurisdictions
- Corporate network data
- Beneficial ownership
- Officer history

**Why it matters:** Currently Solstein only covers UK (Companies House). OpenCorporates adds EU, US states, and global coverage.

---

#### Step-by-Step: Getting OpenCorporates API Key

**Step 1: Create Account**
1. Go to https://opencorporates.com
2. Click "Sign Up"
3. Enter business email
4. Create password

**Step 2: Verify Email**
1. Check inbox
2. Click verification link

**Step 3: Apply for API Key**
1. Go to https://api.opencorporates.com
2. Click "Get API Token"
3. Fill out application:
   - **Project Name:** Solstein
   - **Description:** PE/VC competitive intelligence platform
   - **Use Case:** Company verification and corporate structure analysis
   - **Expected Calls:** Estimate your volume

**Step 4: Wait for Approval**
- Free tier: Usually approved quickly
- Commercial use may require discussion

**Step 5: Get API Key**
1. Once approved, go to your account settings
2. Navigate to "API"
3. Copy your token

**Step 6: Test Your Key**
```bash
curl "https://api.opencorporates.com/companies/gb/00102498?api_token=YOUR_TOKEN"
```

**Pricing:**
- **Free:** 200 requests/day
- **Researcher:** $100/month - 5,000 requests/day
- **Commercial:** $500/month - 50,000 requests/day

---

## Environment Configuration

### Complete `.env` Template

Create a file named `.env` in your project root:

```bash
# ===========================================
# REQUIRED APIs - Core Functionality
# ===========================================

# GitHub API (Required)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here

# NewsAPI (Required for news signals)
# Get from: https://newsapi.org
NEWS_API_KEY=your_newsapi_key_here

# SEC EDGAR (No key required, but set user agent)
SEC_USER_AGENT="Solstein/0.1 (contact: dev@ai-whisperers.com)"

# Yahoo Finance (No key required)
YAHOO_FINANCE_ENABLED=true

# ===========================================
# OPTIONAL APIs - Enhanced Data
# ===========================================

# Companies House (UK companies)
# Get from: https://developer.company-information.service.gov.uk
COMPANIES_HOUSE_API_KEY=your_companies_house_key_here

# Crunchbase (Funding data)
# Get from: https://data.crunchbase.com (requires approval)
CRUNCHBASE_API_KEY=your_crunchbase_key_here

# Exa AI (Web search)
# Get from: https://exa.ai
EXA_API_KEY=exa_your_key_here

# PatentsView (Patent data)
# Get from: https://www.patentsview.org/api
PATENTSVIEW_API_KEY=your_patentsview_key_here

# ===========================================
# RECOMMENDED NEW APIs (Not yet integrated)
# ===========================================

# Proxycurl (LinkedIn data alternative)
# Get from: https://nubela.co/proxycurl
PROXYCURL_API_KEY=your_proxycurl_key_here

# BuiltWith (Tech stack detection)
# Get from: https://builtwith.com
BUILTWITH_API_KEY=your_builtwith_key_here

# OpenFIGI (Identifier resolution)
# Get from: https://www.openfigi.com
OPENFIGI_API_KEY=your_openfigi_key_here

# OpenCorporates (Global company registry)
# Get from: https://opencorporates.com/api
OPENCORPORATES_API_KEY=your_opencorporates_key_here

# PitchBook (Private market data - Enterprise)
# Contact: https://pitchbook.com/products/api-data-feed
PITCHBOOK_API_KEY=your_pitchbook_key_here

# ===========================================
# LLM PROVIDERS (Configure at least one)
# ===========================================

# Primary LLM Provider
# Options: ollama, openai, groq, fireworks, anthropic, mistral,
#          deepinfra, gemini, nvidia, cerebras, kimi, siliconflow, alibaba
LLM_PROVIDER=groq

# Ollama (Local - Free)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# OpenAI
# Get from: https://platform.openai.com
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Groq (Fast & Cheap - Recommended)
# Get from: https://console.groq.com
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Fireworks
# Get from: https://fireworks.ai
FIREWORKS_API_KEY=fw-your_fireworks_key_here
FIREWORKS_MODEL=mixtral-8x22b-instruct

# Anthropic
# Get from: https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# Mistral
# Get from: https://console.mistral.ai
MISTRAL_API_KEY=your_mistral_key_here
MISTRAL_MODEL=mistral-large-latest

# DeepInfra
# Get from: https://deepinfra.com
DEEPINFRA_API_KEY=your_deepinfra_key_here
DEEPINFRA_MODEL=meta-llama/Llama-2-70b-chat-hf

# Gemini (Google)
# Get from: https://ai.google.dev
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-pro

# NVIDIA NIM
# Get from: https://build.nvidia.com
NVIDIA_NIM_API_KEY=your_nvidia_key_here
NVIDIA_MODEL=meta/llama3-70b-instruct

# Cerebras
# Get from: https://cerebras.ai
CEREBRAS_API_KEY=your_cerebras_key_here
CEREBRAS_MODEL=llama3.1-70b

# Kimi (Moonshot)
# Get from: https://platform.moonshot.cn
KIMI_API_KEY=your_kimi_key_here
KIMI_MODEL=moonshot-v1-8k

# SiliconFlow
# Get from: https://siliconflow.com
SILICONFLOW_API_KEY=your_siliconflow_key_here
SILICONFLOW_MODEL=Qwen/Qwen2.5-72B-Instruct

# Alibaba Cloud
# Get from: https://dashscope.aliyun.com
ALIBABA_API_KEY=your_alibaba_key_here
ALIBABA_MODEL=qwen-plus

# ===========================================
# DATABASE & INFRASTRUCTURE
# ===========================================

# PostgreSQL Database
DATABASE__URL=postgresql+asyncpg://user:password@localhost:5432/solstein

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# ===========================================
# SECURITY
# ===========================================

# JWT Secret (generate strong random string)
SECURITY__SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long

# API Key for internal services
API_KEY=your-internal-api-key

# ===========================================
# MONITORING & LOGGING
# ===========================================

# Log Level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Sentry DSN (optional error tracking)
SENTRY_DSN=https://xxx@yyy.ingest.sentry.io/zzz
```

---

## Troubleshooting

### Common Issues

#### "GitHub API rate limit exceeded"
**Cause:** Using unauthenticated requests or exceeded 5,000 requests/hour
**Solution:**
- Verify `GITHUB_TOKEN` is set in `.env`
- Check token hasn't expired
- Reduce batch size in enrichment requests

#### "NewsAPI: 426 Upgrade Required"
**Cause:** Exceeded free tier (100 requests/day)
**Solution:**
- Upgrade to Business plan ($449/month)
- Implement caching to reduce duplicate requests
- Use Exa AI as fallback

#### "SEC EDGAR: Too Many Requests"
**Cause:** Exceeded 10 requests/second
**Solution:**
- Solstein has built-in backoff, but may need to increase delays
- Spread requests over longer time periods
- Use caching (data doesn't change frequently)

#### "Companies House: 401 Unauthorized"
**Cause:** Invalid API key
**Solution:**
- Verify key is copied correctly
- Ensure no extra spaces
- Regenerate key if necessary

#### "LLM provider not available"
**Cause:** API key not set or invalid
**Solution:**
- Set at least one LLM provider key
- Check key is valid by testing with curl
- Use `LLM_PROVIDER=ollama` for local development (free)

#### "Crunchbase returns no data"
**Cause:** No API key (using news fallback) or key expired
**Solution:**
- Check if `CRUNCHBASE_API_KEY` is set
- Verify key hasn't expired
- News fallback has lower confidence (0.30 vs 0.70)

---

### Testing Your Configuration

Run this diagnostic script:

```python
# test_apis.py
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_apis():
    """Test all configured APIs"""
    results = {}

    # Test GitHub
    if os.getenv('GITHUB_TOKEN'):
        try:
            import requests
            resp = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f"token {os.getenv('GITHUB_TOKEN')}"}
            )
            results['GitHub'] = '✅ Working' if resp.status_code == 200 else f"❌ Error {resp.status_code}"
        except Exception as e:
            results['GitHub'] = f"❌ {str(e)}"
    else:
        results['GitHub'] = '⚠️ Not configured'

    # Test NewsAPI
    if os.getenv('NEWS_API_KEY'):
        try:
            import requests
            resp = requests.get(
                'https://newsapi.org/v2/everything',
                params={'q': 'test', 'apiKey': os.getenv('NEWS_API_KEY')}
            )
            results['NewsAPI'] = '✅ Working' if resp.status_code == 200 else f"❌ Error {resp.status_code}"
        except Exception as e:
            results['NewsAPI'] = f"❌ {str(e)}"
    else:
        results['NewsAPI'] = '⚠️ Not configured'

    # Test LLM Provider
    llm_provider = os.getenv('LLM_PROVIDER', 'not set')
    if llm_provider == 'ollama':
        try:
            import requests
            resp = requests.get(f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/tags")
            results['Ollama'] = '✅ Working' if resp.status_code == 200 else f"❌ Error {resp.status_code}"
        except Exception as e:
            results['Ollama'] = f"❌ {str(e)}"
    else:
        results[f'LLM ({llm_provider})'] = '⚠️ Check manually'

    # Print results
    print("\n" + "="*50)
    print("API Configuration Test Results")
    print("="*50)
    for api, status in results.items():
        print(f"{api:20} {status}")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_apis())
```

Run it:
```bash
python test_apis.py
```

---

## Summary Checklist

### Minimum Viable Setup (Development)
- [ ] GitHub token created
- [ ] NewsAPI key obtained
- [ ] At least one LLM provider configured (Ollama recommended for dev)
- [ ] `.env` file created with all keys
- [ ] Database configured

### Production Setup
- [ ] All Required APIs configured
- [ ] At least 2 LLM providers (for failover)
- [ ] Companies House (if analyzing UK companies)
- [ ] Crunchbase (if analyzing startups)
- [ ] Exa AI (for web search)
- [ ] Redis configured
- [ ] Sentry configured (error tracking)

### Enhanced Setup (Recommended)
- [ ] Proxycurl (LinkedIn data)
- [ ] BuiltWith (tech stack)
- [ ] OpenFIGI (identifier resolution)
- [ ] OpenCorporates (global registry)
- [ ] PitchBook (if budget allows)

---

## Support & Resources

### Getting Help

1. **API Documentation:**
   - GitHub: https://docs.github.com/en/rest
   - NewsAPI: https://newsapi.org/docs
   - SEC EDGAR: https://www.sec.gov/edgar/sec-api-documentation
   - LLM Providers: See individual console documentation

2. **Solstein Documentation:**
   - Check `docs/api.md` for API usage
   - Check `docs/development.md` for setup help

3. **Internal Support:**
   - Slack: #solstein-dev
   - Email: dev@ai-whisperers.com

---

*Last updated: March 2026*
*For Solstein v3.0*
