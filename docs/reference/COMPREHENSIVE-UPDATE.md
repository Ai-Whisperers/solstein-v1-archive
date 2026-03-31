# Solstein Expected Behavior and Product Requirements

Solstein must be a **fast, trustworthy competitive-intelligence and due-diligence platform for investors and strategy teams:** you give it a **market, company set, or research target, and it should automatically gather multi-source evidence, normalize and reconcile conflicting facts, score companies with clear reasoning, and deliver usable outputs like rankings, market analysis, and exports instead of raw scraped data.** The non-negotiable features, based on the current codebase and roadmap direction, are: real external data collection rather than mock/stub agents; multi-source enrichment across financial, corporate-registry, engineering, web, and news signals; provenance and source traceability for every important fact; contradiction detection and confidence/readiness gates before results are trusted; explainable scoring/classification; resumable job execution with observable status; human review for low-confidence cases; and production-grade exports and APIs that make the system operationally reliable, not just analytically interesting.

Read this document entirely and use it as a reference for updating backlog tasks and epics, so we enforce full typescript strict schemas and codebases where needed, and conserve python async where needed, as well as making sure the integration is performed perfectly by analyzing the current adapters and components, and make sure you dont create new compatibility patches, instead go to the most initial stages of the codebase, where each feature wasnt bloated with aliases and compatibility patches, and directly modify its codebase, updating the system so we finally have our product working.
  ---                                                                                                                                                                                                                             
# Data & Search APIs (1–14) - API Map                                                                                                                                                                                                         
                                                                                                                                                                                                                                    
  ┌─────┬───────────────────────┬───────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐    
  │  #  │          API          │              Purpose              │                                                                         Verdict                                                                          │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 1   │ Supabase              │ Auth, DB, storage, realtime       │ Non-negotiable — platform backbone                                                                                                                       │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 2   │ GitHub REST API       │ Repo activity, engineering        │ Replaceable — you can scrape public repos directly (commits, stars, PRs, issues) via the public GraphQL/REST without an API key at scale using multiple  │    
  │     │                       │ signals                           │ IPs or a token pool                                                                                                                                      │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 3   │ SEC EDGAR             │ US public filings                 │ Non-negotiable — it's a free government API, no rate-limit alternative exists, and the data is authoritative. The edgartools wrapper is already as close │    
  │     │                       │                                   │  to native as you get                                                                                                                                    │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 4   │ Companies House       │ UK company registry               │ Non-negotiable — government registry, no scraping alternative that's reliable. Free and authoritative                                                    │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 5   │ Exa Search            │ Structured web search + content   │ Replaceable — SearXNG (#8) already does this self-hosted. Exa adds semantic ranking but you're paying for what you could run yourself                    │ 
  │     │                       │ retrieval                         │                                                                                                                                                          │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 6   │ NewsAPI               │ News articles                     │ Replaceable — GDELT (#7) is already your replacement here. NewsAPI has a hard 100 req/day free limit; GDELT is free and unlimited                        │ 
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 7   │ GDELT                 │ News aggregation                  │ Keep/native — free, no rate limit, query directly via their public API. No key required                                                                  │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 8   │ SearXNG               │ Metasearch                        │ Already native — self-hosted, you own the instance. Upgrade this, don't replace it                                                                       │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 9   │ Google Custom Search  │ Web search fallback               │ Replaceable — 100 queries/day free then paid. SearXNG is the better fallback. Drop this                                                                  │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 10  │ yfinance / Yahoo      │ Market/quote data                 │ Replaceable — unofficial scraper of Yahoo Finance. You can query Yahoo Finance directly with the same HTTP calls yfinance makes. Also replaceable with   │    
  │     │ Finance               │                                   │ free tiers of Alpha Vantage or direct exchange feeds                                                                                                     │ 
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 11  │ Crunchbase            │ Funding & company intelligence    │ Non-negotiable for quality — but expensive. Partially replaceable by combining OpenCorporates + SEC EDGAR + scraped LinkedIn funding rounds, but         │ 
  │     │                       │                                   │ Crunchbase's coverage is unmatched for private companies                                                                                                 │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤ 
  │ 12  │ OpenCorporates        │ Registry/entity lookup            │ Non-negotiable — covers 150+ jurisdictions. No single free alternative with this breadth                                                                 │    
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 13  │ OpenFIGI              │ Financial identifier mapping      │ Non-negotiable — free, no rate-limit issues (300 req/min burst, 5000/day), and there's no other authoritative ISIN↔ticker↔CUSIP mapper                   │
  ├─────┼───────────────────────┼───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤    
  │ 14  │ PatentsView           │ Patent search                     │ Already native — USPTO-backed, free, no key required, bulk downloads available. You can hit this at volume directly                                      │
  └─────┴───────────────────────┴───────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘    
                                                                  
  Platform & Notification APIs (15–16)                                                                                                                                                                                              
                                                                  
  ┌─────┬────────────────┬─────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  #  │      API       │           Purpose           │                                                               Verdict                                                               │
  ├─────┼────────────────┼─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                                      
  │ 15  │ Langfuse       │ LLM tracing & observability │ Replaceable / self-hostable — Langfuse has a Docker self-hosted version. Run it yourself and eliminate the SaaS dependency entirely │
  ├─────┼────────────────┼─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                                      
  │ 16  │ Slack Webhooks │ Notifications               │ Non-negotiable operationally — trivial dependency, no rate limit concerns at notification volume                                    │                                      
  └─────┴────────────────┴─────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                                      
                                                                                                                                                                                                                                    
  LLM Provider APIs (17–29)                                                                                                                                                                                                         
                                                                  
  Anthropic (#18) and OpenAI (#17) are non-negotiable as primary/fallback providers given the product's core function. The rest are purely optional redundancy — Groq, Fireworks, Mistral, DeepInfra, Gemini, NVIDIA NIM, Cerebras, 
  Moonshot, SiliconFlow, Qwen, and Ollama are all wired in as a provider pool. Ollama (#29) is already self-hosted and free. The others exist to avoid single-provider lock-in and for cost arbitrage on inference, which is
  legitimate — but you're maintaining 11 LLM adapters, most of which are probably never exercised in production.

* Overview
                    
  Non-negotiable, keep as-is:                                                                                                                                                                                                       
  - Supabase, SEC EDGAR, Companies House, OpenCorporates, OpenFIGI, PatentsView, GDELT, Anthropic, OpenAI, Slack                                                                                                                                                                                                                  
  Easiest to eliminate (directly replaceable natively or already redundant):
  - Google Custom Search (#9) — drop entirely, SearXNG covers it                                                                                                                                                                    
  - NewsAPI (#6) — drop, GDELT is already there and unlimited                                                                                                                                                                       
  - Exa Search (#5) — consolidate into SearXNG; only keep if semantic search quality matters materially                                                                                                                             
  - yfinance (#10) — inline the same HTTP calls directly, remove the dependency                                                                                                                                                     
  - Langfuse (#15) — self-host to own your tracing data                                                                                                                                                                             
                                                                                                                                                                                                                                    
  Legitimate but worth auditing scope:                                                                                                                                                                                              
  - Crunchbase (#11) — most expensive, partially replaceable by stacking EDGAR + OpenCorporates + scraped signals                                                                                                                   
  - LLM provider pool (#19–29) — 9 of the 11 extras are dead weight unless you're actively routing to them. Pare down to 2–3 with clear fallback logic.

---

# TypeScript 

Below is a **TS-first integration spec** recommendation that adds **per-provider adaptive control** and **Temporal workflows** to the earlier API map.

Two important corrections to the reference sheet:

* **PatentsView is no longer “no key required”** on the current PatentSearch API. The current docs say all requests must include `X-Api-Key`, each key is limited to **45 requests/minute**, and new key grants are **temporarily suspended**. ([PatentsView][1])
* **Google Custom Search JSON API is now closed to new customers**, and existing customers are expected to transition by **January 1, 2027**. ([Google for Developers][2])

---

# 1. Core architecture you should enforce

## Control plane

* **TypeScript + Temporal** for orchestration, retries, scheduling, and failure isolation.
* **Provider adapters** in TS with runtime validation at every boundary.
* **Workflows stay deterministic**; no direct network calls inside workflow code. Temporal’s TS docs explicitly say workflow-to-environment interaction should happen through **Activities**, and workflow-to-workflow communication should use handles/signals to preserve determinism. ([Temporal Docs][3])

## Data plane

* **Supabase** as system of record for auth, relational state, storage, and realtime/broadcast primitives. Supabase documents Postgres, Auth, Storage, Realtime, and Edge Functions as core platform modules. ([Supabase][4])
* **Raw payload landing first**, normalized entities second, analytics tables/materializations third.
* **Langfuse self-hosted** for tracing/observability if you want to keep LLM telemetry in your infra. Langfuse explicitly documents self-hosting with Docker and production-scale deployment options. ([Langfuse][5])

## Temporal rules

* **Activities must be idempotent**, because workers can run many activities concurrently and Temporal may retry them. ([Temporal Docs][6])
* **Workflows do not retry by default**; use workflow retries sparingly. **Activities do get a default retry policy** if you do not set a custom one. ([Temporal Docs][7])
* Use **Schedules** for recurring ingestion instead of cron-like external glue. Temporal recommends schedules for automating repeated workflow execution. ([Temporal Docs][8])
* Use **Continue-As-New** when long-running entity monitors or company intelligence loops build up event history. Temporal documents this as the checkpoint mechanism for long histories/scaling limits. ([Temporal Docs][9])

---

# 2. Global adapter contract

```ts
export type ProviderKey =
  | "supabase"
  | "github"
  | "sec_edgar"
  | "companies_house"
  | "exa"
  | "newsapi"
  | "gdelt"
  | "searxng"
  | "google_cse"
  | "yahoo_finance"
  | "crunchbase"
  | "opencorporates"
  | "openfigi"
  | "patentsview"
  | "langfuse"
  | "slack"
  | "openai"
  | "anthropic";

export type ProviderEnvelope<TNormalized> = {
  requestId: string;
  provider: ProviderKey;
  endpoint: string;
  attempt: number;
  statusCode?: number;
  latencyMs?: number;
  traceId: string;
  rawRef?: string;
  normalized?: TNormalized;
  retryAfterMs?: number;
  rate?: {
    limit?: number;
    remaining?: number;
    resetAt?: string;
    dimension?: "rps" | "rpm" | "rph" | "tpm" | "itpm" | "otpm" | "concurrency";
  };
  errorCode?: string;
  errorMessage?: string;
};

export interface ProviderAdapter<TReq, TNorm> {
  provider: ProviderKey;
  execute(input: TReq): Promise<ProviderEnvelope<TNorm>>;
  classifyRetry(result: ProviderEnvelope<TNorm>): "retry" | "fail" | "drop";
}
```

---

# 3. Per-provider adaptive control matrix

## 1) Supabase

* **Official docs**: core docs, RLS, connection management, realtime, edge functions. ([Supabase][4])
* **Hard constraints**

  * Enable **RLS** on public-schema data APIs; Supabase explicitly says to enable RLS on tables, views, and functions in `public`. ([Supabase][10])
  * Use connection pooling; Supabase documents Supavisor and connection pooling for scalability. ([Supabase][11])
  * Prefer **Broadcast** over raw Postgres Changes when you need scalable realtime fanout; Supabase documents Broadcast as the recommended method for scalability/security. ([Supabase][12])
* **Adaptive control**

  * Not provider-rate-limit driven; it is **DB/pool saturation driven**.
  * Control by:

    * pool occupancy
    * statement latency p95
    * replication lag / realtime lag
    * queue depth
* **Policy**

  * `maxConcurrency`: start 16 per worker for write-heavy ingestion.
  * Backoff on pool saturation or serialization errors.
  * Do not use Supabase Realtime as the ingestion bus.

## 2) GitHub REST / GraphQL

* **Official docs**: REST docs, rate limits, best practices. ([GitHub Docs][13])
* **Hard constraints**

  * Unauthenticated REST: **60 requests/hour** per IP; authenticated users: **5,000/hour**; GitHub Apps/OAuth can go higher in some cases. ([GitHub Docs][14])
  * Secondary limits: **≤100 concurrent requests** shared across REST/GraphQL and **≤900 REST points/minute**. ([GitHub Docs][14])
  * GitHub recommends:

    * authenticated requests
    * avoid concurrent requests
    * at least **1 second** between mutating requests
    * conditional requests with `ETag` / `If-None-Match` when appropriate. ([GitHub Docs][15])
* **Adaptive control**

  * Parse `x-ratelimit-remaining`, `x-ratelimit-reset`, `retry-after`. ([GitHub Docs][14])
  * Maintain:

    * concurrency token bucket
    * points budget
    * endpoint-specific cooldown
* **Policy**

  * `maxConcurrency`: 20 globally, 4 per repo hot path.
  * `baseBackoffMs`: 1500
  * `on403/429`: obey `retry-after`; if absent and secondary suspected, sleep 60s minimum then exponential. ([GitHub Docs][15])

## 3) SEC EDGAR

* **Official docs**: EDGAR APIs, Accessing EDGAR Data, Developer Resources. ([SEC][16])
* **Hard constraints**

  * Current fair-access guideline: **max 10 requests/second** per user across machines. ([SEC][17])
  * SEC asks for efficient scripting and requires declaring a **User-Agent** with company/contact info in request headers. ([SEC][17])
  * `data.sec.gov` provides RESTful JSON APIs for submissions/XBRL, and EDGAR index files are available in HTML/XML/JSON. ([SEC][18])
* **Adaptive control**

  * Use strict **global per-org RPS gate**.
  * Separate lanes:

    * `submissions_json`
    * `xbrl_facts`
    * `index_backfill`
  * Detect 403/connection throttling as congestion signal.
* **Policy**

  * `maxRps`: 5 initially, raise to 8 only after stable runs.
  * `maxConcurrency`: 2
  * `baseBackoffMs`: 2000
  * Always send descriptive `User-Agent`.

## 4) Companies House

* **Official docs**: get started + developer guidelines. ([Developer Hub][19])
* **Hard constraints**

  * **600 requests per 5 minutes**; excess requests return `429` until window reset. ([Developer Hub][20])
  * Auth supported via API key / stream key / OAuth depending endpoint class. ([Developer Hub][19])
* **Adaptive control**

  * Sliding-window limiter per credential.
  * Penalize repeated lookups of same company number less by cache hit.
* **Policy**

  * `rpmEquivalent`: 100
  * `maxConcurrency`: 5
  * `baseBackoffMs`: 1000
  * Prefer cache-first because registry data is relatively slow-changing.

## 5) Exa

* **Official docs**: getting started, search/contents docs, rate-limits page, TypeScript SDK spec. Exa’s docs index and rate-limit page expose the relevant references. ([Exa][21])
* **Hard constraints**

  * Default endpoint limits:

    * `/search` **10 QPS**
    * `/findSimilar` **10 QPS**
    * `/contents` **100 QPS**
    * `/answer` **10 QPS**
    * `/research` **15 concurrent tasks**. ([Exa][22])
* **Adaptive control**

  * Separate limiter per endpoint family.
  * Reserve `/research` concurrency for high-value jobs only.
* **Policy**

  * `searchQps`: 8
  * `contentsQps`: 50
  * `researchConcurrency`: 5 internal cap unless ROI proven
  * `baseBackoffMs`: 750

## 6) NewsAPI

* **Official docs**: docs and endpoint docs. ([News API][23])
* **Practical decision**

  * Keep only if you need its source curation as a secondary signal; otherwise retire per your own consolidation plan.
* **Adaptive control**

  * Low priority lane only.
  * No workflow-critical dependencies.

## 7) GDELT

* **Official docs / official project docs**: GDELT project, DOC 2.0 API docs/blog, data page. ([GDELT Project][24])
* **Hard constraints**

  * GDELT’s DOC 2.0 supports English-keyword search across **65 machine-translated languages**. ([GDELT Project][25])
  * It is an open-data global graph / realtime monitoring surface. ([GDELT Project][24])
* **Adaptive control**

  * No formal public quota surfaced in the docs I checked, so **self-impose** rate and payload discipline.
  * Control by:

    * query cost
    * time window width
    * result volume
* **Policy**

  * `maxConcurrency`: 4
  * `baseBackoffMs`: 500
  * widen windows slowly; do not fan out uncontrolled historical pulls

## 8) SearXNG

* **Official docs**: installation, limiter, bot detection. ([SearXNG Documentation][26])
* **Hard constraints**

  * SearXNG documents that the limiter exists because upstream search engines classify it as a bot and may CAPTCHA/block it. ([SearXNG Documentation][27])
  * `ip_limit` bot detection uses sliding windows and needs Valkey plus `X-Forwarded-For` for proper IP-based control. ([SearXNG Documentation][28])
* **Adaptive control**

  * Your limiter is internal, not vendor-owned.
  * Control dimensions:

    * per-client IP
    * per-origin engine
    * proxy health
    * CAPTCHA/error rate
* **Policy**

  * One limiter for **client → SearXNG**
  * Another for **SearXNG → origin engines**
  * Dynamic per-engine cooloffs on CAPTCHA spikes

## 9) Google Custom Search

* **Official docs**: overview + reference. ([Google for Developers][2])
* **Hard constraints**

  * Closed to new customers; existing customers transition by **2027-01-01**.
  * Requires Programmable Search Engine + API key.
  * **100 free queries/day**, then paid. ([Google for Developers][2])
* **Adaptive control**

  * Put behind a kill-switch and daily budget guard.
* **Policy**

  * Do not build critical workflows around it.

## 10) Yahoo Finance / direct Yahoo calls

* I did **not** find an official public Yahoo Finance API documentation source in the official-domain checks I ran.
* **Policy**

  * Treat as unstable/unofficial.
  * Put behind a best-effort adapter with schema quarantine.
  * Never make it the canonical financial truth source.

## 11) Crunchbase

* **Official docs**: API overview, search APIs, entity lookup APIs. ([Access Crunchbase Data][29])
* **Hard constraints**

  * Crunchbase documents a read-only REST API and notes that limits/ranges can vary by endpoint/reference docs. ([Access Crunchbase Data][29])
* **Adaptive control**

  * Budget-aware throttler.
  * Cache by organization/permalink aggressively.
* **Policy**

  * Premium source for private-company intelligence only.
  * Internal priority score must justify the call.

## 12) OpenCorporates

* **Official docs**: API reference. ([OpenCorporates API][30])
* **Hard constraints**

  * REST API, JSON by default, API key required, usage limits depend on account type/plan. ([OpenCorporates API][30])
* **Adaptive control**

  * Key-per-plan budget accounting.
  * Cache by `(jurisdiction_code, company_number)`.
* **Policy**

  * Use as canonical registry resolver after local cache miss.

## 13) OpenFIGI

* **Official docs**: overview + API documentation. ([OpenFIGI][31])
* **Hard constraints**

  * With API key on mapping API: **25 requests per 6 seconds** and **100 jobs per request**.
  * Without API key: **25 per minute** and **10 jobs per request**.
  * Search/filter API: **20 requests/minute** with key, **5/minute** without.
  * Returns `ratelimit-limit`, `ratelimit-remaining`, `ratelimit-reset`; `429` on rate-limit breach. ([OpenFIGI][32])
* **Adaptive control**

  * Batch aggressively.
  * Separate mapping and search queues.
* **Policy**

  * `mappingBurstWindow`: 6s
  * `mappingBatchSize`: 100
  * `searchRpm`: 20
  * `baseBackoffMs`: 750

## 14) PatentsView

* **Official docs**: PatentSearch API reference, endpoint dictionary, updates page. ([PatentsView][1])
* **Hard constraints**

  * Current PatentSearch API requires `X-Api-Key`.
  * **45 requests/minute** per key.
  * `429` includes `Retry-After`.
  * Requests can use GET or POST; `q` is required; default page size is 100, max 1000. ([PatentsView][1])
* **Adaptive control**

  * Per-key fixed window + pagination-aware queue.
* **Policy**

  * `rpm`: 40 internal
  * `maxConcurrency`: 2
  * pause all backfills if key access is not secured, because new key grants are currently suspended. ([PatentsView][1])

## 15) Langfuse

* **Official docs**: overview, observability, self-hosting, SDKs. ([Langfuse][33])
* **Hard constraints**

  * Open-source and self-hostable.
  * Self-hosted stack uses Postgres, ClickHouse, Redis/Valkey, object storage, and async worker ingestion. ([Langfuse][5])
  * Langfuse notes tracing data is central to prompt/response/token/latency/tool observability. ([Langfuse][34])
* **Adaptive control**

  * Fire-and-buffer, not request-critical.
  * Drop or batch low-priority traces under pressure.
* **Policy**

  * tracing must never block primary provider workflows

## 16) Slack incoming webhooks

* **Official docs**: incoming webhooks, security best practices, rate limits. ([Slack API][35])
* **Hard constraints**

  * Incoming webhooks are JSON POST endpoints.
  * Slack documents **1 request/second** for incoming webhooks, with short bursts allowed.
  * On `429`, Slack returns `Retry-After`. ([Slack API][35])
  * Webhook URLs are channel-specific and tied to the app identity. ([Slack Developer Docs][36])
* **Adaptive control**

  * Per-channel token bucket.
* **Policy**

  * `rps`: 1 per channel
  * aggregate duplicate alerts before sending

## 17) OpenAI

* **Official docs**: Responses API, project rate limits, model comparison/rate-limit tables. ([OpenAI Platform][37])
* **Hard constraints**

  * Responses API supports text/image inputs, JSON outputs, tools, and function calling. ([OpenAI Platform][37])
  * Project-level rate limits are configurable via the admin/reference surface. ([OpenAI Platform][38])
  * Model compare pages publish **TPM by tier** for current models. For example, GPT-5.4 and GPT-5.4 mini show tiered TPM limits and support structured outputs/function calling. ([OpenAI Platform][39])
* **Adaptive control**

  * Dual limiter:

    * request concurrency
    * token budget
  * Route jobs by:

    * expected prompt size
    * output size
    * latency target
* **Policy**

  * use a token-estimator before enqueue
  * prefer structured outputs for extraction
  * use prompt caching / context reuse where applicable

## 18) Anthropic

* **Official docs**: API overview, rate limits. ([Claude API Docs][40])
* **Hard constraints**

  * Rate limits are measured in **RPM, ITPM, and OTPM**.
  * `429` includes `retry-after`.
  * Anthropic documents **acceleration limits**, so sudden traffic ramps can trip 429s even before steady-state usage.
  * Response headers expose current request-limit status.
  * For most Claude models, cached-read input tokens do **not** count toward ITPM, which increases effective throughput when prompt caching is used. ([Claude API Docs][41])
* **Adaptive control**

  * Triple limiter:

    * RPM
    * uncached input tokens
    * output tokens
  * Add **ramp controller** to avoid acceleration-limit spikes.
* **Policy**

  * gradual warm-up after deploy
  * large repeated contexts should use prompt caching

## 19–29) Optional LLM pool

* I am intentionally **not hardcoding per-vendor quotas here** because those vendors change plans, tiers, and model-specific limits more often, and most of your pool is likely dead weight operationally.
* **Pattern**

  * same adapter interface
  * same retry classifier
  * same token-budget contract
  * same provider score
* **Constraint**

  * keep only **2–3 exercised providers** in production; everything else increases adapter entropy, testing surface, and fallback ambiguity.

---

# 4. Temporal workflow pattern

## Workflow split

### A. `ingestProviderWorkflow`

Use for one provider call or one small bounded fanout.

```ts
// workflow
export async function ingestProviderWorkflow(input: {
  provider: ProviderKey;
  jobKey: string;
  payload: unknown;
}) {
  const result = await activities.callProvider(input);   // network only in activity
  await activities.persistRaw(result);
  await activities.normalizeAndUpsert(result);

  if (result.errorCode) {
    await activities.emitTrace(result);
  }

  return result;
}
```

### B. `companyIntelligenceWorkflow`

Use for a company/entity intelligence run.

```ts
export async function companyIntelligenceWorkflow(input: {
  companyId: string;
  cik?: string;
  githubRepos?: string[];
  figiIds?: string[];
}) {
  // fan out in bounded batches, not unbounded Promise.all
  await Promise.all([
    activities.fetchSec(input),
    activities.fetchCompaniesHouse(input),
    activities.fetchOpenCorporates(input),
    activities.fetchCrunchbase(input),
    activities.fetchGdelt(input),
    activities.fetchGithubSignals(input),
  ]);

  await activities.resolveEntities(input.companyId);
  await activities.materializeSignals(input.companyId);
  await activities.notifyIfThresholdCrossed(input.companyId);
}
```

### C. `scheduledMonitorWorkflow`

Use for recurring research/alerts. Back it with Temporal **Schedules**. ([Temporal Docs][8])

```ts
export async function scheduledMonitorWorkflow(input: {
  monitorId: string;
  query: string;
  providers: ProviderKey[];
}) {
  for (const provider of input.providers) {
    await activities.enqueueMonitorProbe({ provider, query: input.query });
  }

  // if this monitor runs indefinitely and accumulates state:
  // continueAsNew(...) when history grows
}
```

---

# 5. Provider-aware retry + throttle policy object

```ts
type AdaptivePolicy = {
  maxConcurrency: number;
  baseBackoffMs: number;
  maxBackoffMs: number;
  maxAttempts: number;
  timeoutMs: number;
  limiter: "fixed-window" | "token-bucket" | "leaky-bucket" | "token+concurrency";
  headers?: {
    retryAfter?: string;
    remaining?: string;
    reset?: string;
  };
  parseDynamicBudget?: boolean;
};

export const PROVIDER_POLICY: Record<ProviderKey, AdaptivePolicy> = {
  supabase: {
    maxConcurrency: 16,
    baseBackoffMs: 100,
    maxBackoffMs: 5_000,
    maxAttempts: 3,
    timeoutMs: 15_000,
    limiter: "concurrency",
  } as any,

  github: {
    maxConcurrency: 20,
    baseBackoffMs: 1_500,
    maxBackoffMs: 60_000,
    maxAttempts: 5,
    timeoutMs: 20_000,
    limiter: "token+concurrency",
    headers: {
      retryAfter: "retry-after",
      remaining: "x-ratelimit-remaining",
      reset: "x-ratelimit-reset",
    },
    parseDynamicBudget: true,
  },

  sec_edgar: {
    maxConcurrency: 2,
    baseBackoffMs: 2_000,
    maxBackoffMs: 90_000,
    maxAttempts: 6,
    timeoutMs: 30_000,
    limiter: "token-bucket",
  },

  companies_house: {
    maxConcurrency: 5,
    baseBackoffMs: 1_000,
    maxBackoffMs: 30_000,
    maxAttempts: 5,
    timeoutMs: 15_000,
    limiter: "fixed-window",
  },

  exa: {
    maxConcurrency: 8,
    baseBackoffMs: 750,
    maxBackoffMs: 20_000,
    maxAttempts: 4,
    timeoutMs: 25_000,
    limiter: "token-bucket",
  },

  newsapi: {
    maxConcurrency: 2,
    baseBackoffMs: 2_000,
    maxBackoffMs: 30_000,
    maxAttempts: 2,
    timeoutMs: 15_000,
    limiter: "fixed-window",
  },

  gdelt: {
    maxConcurrency: 4,
    baseBackoffMs: 500,
    maxBackoffMs: 20_000,
    maxAttempts: 4,
    timeoutMs: 25_000,
    limiter: "token-bucket",
  },

  searxng: {
    maxConcurrency: 8,
    baseBackoffMs: 1_000,
    maxBackoffMs: 30_000,
    maxAttempts: 4,
    timeoutMs: 20_000,
    limiter: "token+concurrency",
  },

  google_cse: {
    maxConcurrency: 1,
    baseBackoffMs: 2_000,
    maxBackoffMs: 60_000,
    maxAttempts: 2,
    timeoutMs: 15_000,
    limiter: "fixed-window",
  },

  yahoo_finance: {
    maxConcurrency: 2,
    baseBackoffMs: 3_000,
    maxBackoffMs: 60_000,
    maxAttempts: 2,
    timeoutMs: 15_000,
    limiter: "token-bucket",
  },

  crunchbase: {
    maxConcurrency: 3,
    baseBackoffMs: 2_000,
    maxBackoffMs: 60_000,
    maxAttempts: 3,
    timeoutMs: 20_000,
    limiter: "token-bucket",
  },

  opencorporates: {
    maxConcurrency: 3,
    baseBackoffMs: 1_500,
    maxBackoffMs: 45_000,
    maxAttempts: 4,
    timeoutMs: 20_000,
    limiter: "fixed-window",
  },

  openfigi: {
    maxConcurrency: 4,
    baseBackoffMs: 750,
    maxBackoffMs: 20_000,
    maxAttempts: 4,
    timeoutMs: 15_000,
    limiter: "fixed-window",
    headers: {
      remaining: "ratelimit-remaining",
      reset: "ratelimit-reset",
      retryAfter: "retry-after",
    },
    parseDynamicBudget: true,
  },

  patentsview: {
    maxConcurrency: 2,
    baseBackoffMs: 1_500,
    maxBackoffMs: 45_000,
    maxAttempts: 4,
    timeoutMs: 20_000,
    limiter: "fixed-window",
    headers: {
      retryAfter: "retry-after",
    },
  },

  langfuse: {
    maxConcurrency: 16,
    baseBackoffMs: 250,
    maxBackoffMs: 5_000,
    maxAttempts: 2,
    timeoutMs: 10_000,
    limiter: "token-bucket",
  },

  slack: {
    maxConcurrency: 1,
    baseBackoffMs: 1_000,
    maxBackoffMs: 30_000,
    maxAttempts: 4,
    timeoutMs: 10_000,
    limiter: "fixed-window",
    headers: {
      retryAfter: "retry-after",
    },
  },

  openai: {
    maxConcurrency: 8,
    baseBackoffMs: 1_500,
    maxBackoffMs: 60_000,
    maxAttempts: 5,
    timeoutMs: 60_000,
    limiter: "token+concurrency",
  },

  anthropic: {
    maxConcurrency: 6,
    baseBackoffMs: 1_500,
    maxBackoffMs: 60_000,
    maxAttempts: 5,
    timeoutMs: 60_000,
    limiter: "token+concurrency",
    headers: {
      retryAfter: "retry-after",
      remaining: "anthropic-ratelimit-requests-remaining",
      reset: "anthropic-ratelimit-requests-reset",
    },
    parseDynamicBudget: true,
  },
};
```

---

# 6. Temporal activity retry shape

Use **custom activity retry policies** for providers, not one global default. Temporal supports custom activity retry policies, activity timeouts, heartbeat timeouts, and even overriding the next retry delay after an activity failure. ([Temporal Docs][7])

```ts
import { proxyActivities } from "@temporalio/workflow";

const githubActivities = proxyActivities<typeof import("./activities/github")>({
  startToCloseTimeout: "20 seconds",
  heartbeatTimeout: "5 seconds",
  retry: {
    initialInterval: "1500 milliseconds",
    backoffCoefficient: 2,
    maximumInterval: "60 seconds",
    maximumAttempts: 5,
    nonRetryableErrorTypes: ["BadRequest", "Unauthorized", "SchemaViolation"],
  },
});

const secActivities = proxyActivities<typeof import("./activities/sec")>({
  startToCloseTimeout: "30 seconds",
  heartbeatTimeout: "10 seconds",
  retry: {
    initialInterval: "2 seconds",
    backoffCoefficient: 2,
    maximumInterval: "90 seconds",
    maximumAttempts: 6,
    nonRetryableErrorTypes: ["BadRequest", "Unauthorized"],
  },
});
```

---

# 7. Adaptive control logic you should actually implement

## Retry classification

* **Retry**

  * transport errors
  * `408`, `409` where safe
  * `423`, `429`, `500`, `502`, `503`, `504`
* **Fail fast**

  * `400`, `401`, `403` unless provider docs explicitly frame it as recoverable throttling
  * schema validation failure
  * unsupported query shape
* **Drop**

  * duplicate idempotency key
  * stale monitor run superseded by newer run

## Dynamic delay

Use provider headers first, then your policy.

```ts
function computeDelayMs(resp: {
  headers: Headers;
  attempt: number;
  provider: ProviderKey;
}) {
  const p = PROVIDER_POLICY[resp.provider];
  const retryAfter = resp.headers.get(p.headers?.retryAfter ?? "");
  if (retryAfter) return Number(retryAfter) * 1000;

  const raw = p.baseBackoffMs * Math.pow(2, resp.attempt - 1);
  const jitter = raw * (0.2 + Math.random() * 0.6);
  return Math.min(jitter, p.maxBackoffMs);
}
```

## Token-aware admission for OpenAI / Anthropic

* Estimate prompt + expected output before enqueue.
* Reject or defer work that would oversubscribe TPM/ITPM/OTPM budgets.
* For Anthropic, weight **uncached** input higher than cached input because cached reads typically do not count toward ITPM on most Claude models. ([Claude API Docs][41])

## Provider score

Use routing pressure, not just raw fallback order.

```ts
score = expected_signal_value / (
  cost_weight * estimated_latency_ms * recent_error_rate * budget_pressure
)
```

---

# 8. Minimal official-doc list by provider

Use these as the **must-read doc set** for your team:

* **Supabase**: core docs, RLS, securing your API, connection management, realtime, edge functions. ([Supabase][4])
* **GitHub**: REST docs, rate limits, REST best practices. ([GitHub Docs][13])
* **SEC EDGAR**: EDGAR APIs, Accessing EDGAR Data, Developer Resources. ([SEC][16])
* **Companies House**: Get started, developer guidelines. ([Developer Hub][19])
* **Exa**: Search/Contents docs, rate limits, TS SDK spec. ([Exa][21])
* **NewsAPI**: docs and endpoint docs, only if you keep it. ([News API][23])
* **GDELT**: project overview, DOC 2.0 docs, data page. ([GDELT Project][24])
* **SearXNG**: limiter, bot detection, installation. ([SearXNG Documentation][27])
* **Google CSE**: overview/reference only for retirement planning. ([Google for Developers][2])
* **Crunchbase**: API overview, search APIs, entity lookup APIs. ([Access Crunchbase Data][29])
* **OpenCorporates**: API reference. ([OpenCorporates API][30])
* **OpenFIGI**: overview + API documentation. ([OpenFIGI][31])
* **PatentsView**: PatentSearch API reference, endpoint dictionary, updates page. ([PatentsView][1])
* **Langfuse**: overview, observability, self-hosting, SDK compatibility. ([Langfuse][33])
* **Slack**: incoming webhooks, rate limits, security. ([Slack API][35])
* **OpenAI**: Responses API, project rate limits, model compare/rate-limit tables. ([OpenAI Platform][37])
* **Anthropic**: API overview, rate limits, response headers. ([Claude API Docs][40])
* **Temporal**: TS SDK guide, core application, failure detection, schedules, continue-as-new, workflow execution overview. ([Temporal Docs][42])

---

# 9. Bottom-line design choice

For Solstein, the correct stack is:

* **TypeScript orchestration**
* **Temporal workflows**
* **per-provider adaptive throttlers**
* **runtime schema validation**
* **Supabase as source-of-truth**
* **Langfuse self-hosted for traces**
* **Spark only later for offline batch analytics**

That design matches the real constraint field: **rate-limit heterogeneity, external I/O, schema drift, partial failures, and long-running monitors**, not local compute saturation. Temporal is the right durability primitive here because it gives you retry/timeouts/schedules/history/recovery, while the provider controllers absorb each API’s very different quota geometry. ([Temporal Docs][43])

# 10. Layers and Components

Solstein's architecture is structured by an **async TypeScript ingestion and orchestration component (part of the Fetch/orchestration layer)** for EDGAR / Companies House / GDELT / OpenCorporates / OpenFIGI / search / LLM calls, with **hard TypeScript enforcement** via `tsconfig` `strict`, **runtime boundary validation** via **Zod**, and **Temporal workflows + activities** for retries, schedules, fan-out/fan-in, and long-running monitors. Temporal’s TypeScript SDK runs workflows in a **deterministic sandbox** and requires side effects and external state access to go through **Activities**, which Temporal recommends making **idempotent** because they can be retried automatically. Normalized records should land first in **Supabase/Postgres + object storage/Parquet**, and only then flow into Python for specialized parsing/enrichment or into Spark for offline analytics. Supabase should remain the system backbone with **RLS**, connection management/Supavisor, and **TypeScript Edge Functions** for low-latency webhook and integration edges. ([TypeScript][44])

**Supabase/Postgres or object storage + queue as source of truth; TypeScript with strict Zod schemas and Temporal-backed adapters for API collection, validation, retries, provider-aware throttling, and data normalization/aggregation; Python with Pydantic, PyArrow/Parquet, and Polars lazy execution for filing parsers, medium-scale enrichment, and columnar transforms; Spark for batch intelligence jobs**. Concretely, Python is the right place for **typed sidecars** and **columnar preprocessing** because **Pydantic** validates canonical Python models and can emit JSON Schema, **PyArrow** is the Arrow/Parquet bridge for fast columnar interchange, and **Polars lazy** can apply query optimization, streaming, and early schema-error detection before you escalate to Spark. ([Pydantic][45])

Concrete examples where Spark is justified remain: joining **GDELT news events + OpenCorporates entities + Crunchbase company/funding tables + OpenFIGI mappings + price/quote history** across long horizons; computing rolling anomaly scores; deduplicating entities across jurisdictions; building sector/topic embeddings datasets; and recomputing competitive-signal features for thousands to millions of documents. **Spark** solves the dominant cost of **tabular transformation** over large datasets—relational SQL/DataFrame execution, joins, aggregations, partition pruning, skew handling, and AQE re-optimization—and **AQE is enabled by default** in modern Spark SQL. Running Spark in **local mode** is fully valid, so you can start on one machine and only go distributed when storage volume, shuffle pressure, or recomputation cadence justifies it. ([Apache Spark][46])

**Fetch/orchestration layer** dominant cost is **external API latency, retries, rate limits, heterogeneous payload normalization, and fan-out/fan-in network I/O**. TypeScript-based **Async/Ingestion Components within the Fetch/orchestration layer** dominant costs are: **calling APIs, parsing per-request JSON, managing webhook notifications, LLM routing, retry logic, and trace emission**. **Spark** and **Catalyst** should therefore stay off the hot path of live orchestration: Spark SQL is optimized for relational query plans, and AQE only helps after the data is already represented as Spark SQL/DataFrame plans. So the right action is **using PySpark only for the offline analytical spine, not as the main app runtime**, while reserving Python in the live path for narrow, typed sidecars where the ecosystem has real leverage. ([Apache Spark][47])

* Contract Integrity Layer
  Beyond the first layer (Fetch/orchestration & async/ingestion & schema enforcement through **strict TypeScript + Zod**) the next fundamental layer is **contract integrity across boundaries**. That means idempotency, versioning, backward compatibility, deterministic serialization, pagination semantics, retry semantics, timeout budgets, and explicit error taxonomies, but now enforced through a **single contract surface**: compile-time strictness in TypeScript, runtime parsing with Zod, and JSON Schema emission from your schemas so that provider contracts, internal DTOs, and Python sidecars do not drift apart. Python improvements belong here too: when a sidecar is unavoidable, it should accept and emit only **Pydantic** models so the boundary remains typed, validated, and serializable instead of devolving into raw JSON. ([TypeScript][44])

* Control-plane Reliability
  The second layer is **control-plane reliability**. For BI research software this is critical because data quality degrades silently, and this is exactly where **Temporal** becomes the durable control plane: workflows run deterministically, side effects are isolated in Activities, Activities should be idempotent, and Temporal gives you retry policies, schedules, and **Continue-As-New** for long-running monitors that would otherwise accumulate too much event history. You still need provenance per field, trace IDs across hops, replayable request logs, dead-letter queues, circuit breakers, adaptive backoff, concurrency limits, cache invalidation policy, and auditability of derived outputs, but the orchestration substrate should now be Temporal rather than ad hoc retry code spread across services. ([Temporal Docs][48])

* Semantic Normalization and Ontology Discipline Layer
  Another critical layer is **semantic normalization and ontology discipline**. APIs rarely agree on entity identity, naming, units, categories, or temporal grain, so proper wiring still requires canonical internal models, entity resolution, deduplication, unit conversion, timezone normalization, and explicit conflict-resolution logic. The update is that this layer should now be split cleanly: **TypeScript adapters at the edge**, a **canonical domain core** shared across services, and **Python analytical sidecars** only for heavier normalization passes, columnar transforms, or specialized parsers. Using **Polars lazy** and **PyArrow/Parquet** here is valuable because they preserve a columnar path, apply optimizer passes such as predicate/projection pushdown, and catch schema problems before materialization. ([Polars User Guide][49])

* Operational Guardrails
  Finally, enforce **operational guardrails**: cost ceilings, SLA/SLOs, test harnesses with recorded fixtures, sandbox/live separation, secret rotation, permission minimization, and synthetic monitoring for drift. In the updated stack, that means **`tsc` strict mode in CI**, Zod schema tests on every provider adapter, **Temporal schedules** for synthetic probes and recurring monitors, **RLS + SSL + network restrictions** in Supabase production, and **Pydantic Settings** or equivalent typed config loading for Python services so secrets and environment-driven behavior remain explicit and validated. I would still rank the core stack as: schema/contracts, provenance/observability, semantic normalization, resilience controls, then security/cost governance—but now each layer has a concrete enforcement mechanism instead of staying conceptual. ([TypeScript][44])

A strong next artifact is to turn this into a **provider scorecard + enforcement matrix** per API: strict schema owner, retry class, Temporal activity policy, cache TTL, canonical ID rule, Python-sidecar yes/no, and Spark-escalation threshold.

# 11. References and March 31 Audits

[1]: https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference/?utm_source=chatgpt.com "PatentSearch API Reference | PatentsView Search Platform ..."
[2]: https://developers.google.com/custom-search/v1/overview "Custom Search JSON API  |  Google for Developers"
[3]: https://docs.temporal.io/develop/typescript/message-passing "Workflow message passing - TypeScript SDK | Temporal Platform Documentation"
[4]: https://supabase.com/docs "Supabase Docs"
[5]: https://langfuse.com/docs/self-hosting "Self-host Langfuse (Open Source LLM Observability) - Langfuse"
[6]: https://docs.temporal.io/develop/typescript/core-application "Core application - TypeScript SDK | Temporal Platform Documentation"
[7]: https://docs.temporal.io/develop/typescript/failure-detection "Failure detection - TypeScript SDK feature guide | Temporal Platform Documentation"
[8]: https://docs.temporal.io/develop/typescript/schedules "Schedules - TypeScript SDK | Temporal Platform Documentation"
[9]: https://docs.temporal.io/develop/typescript/continue-as-new "Continue-As-New - Typescript SDK | Temporal Platform Documentation"
[10]: https://supabase.com/docs/guides/api/securing-your-api?utm_source=chatgpt.com "Securing your API | Supabase Docs"
[11]: https://supabase.com/docs/guides/database/connecting-to-postgres?utm_source=chatgpt.com "Connect to your database | Supabase Docs"
[12]: https://supabase.com/docs/guides/realtime/subscribing-to-database-changes?utm_source=chatgpt.com "Subscribing to Database Changes | Supabase Docs"
[13]: https://docs.github.com/en/rest?utm_source=chatgpt.com "GitHub REST API documentation - GitHub Docs"
[14]: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api "Rate limits for the REST API - GitHub Docs"
[15]: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api?apiVersion=2026-03-10 "Best practices for using the REST API - GitHub Docs"
[16]: https://www.sec.gov/search-filings/edgar-application-programming-interfaces "SEC.gov | EDGAR Application Programming Interfaces (APIs)"
[17]: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data "SEC.gov | Accessing EDGAR Data"
[18]: https://www.sec.gov/about/developer-resources "SEC.gov | Developer Resources"
[19]: https://developer.company-information.service.gov.uk/get-started?utm_source=chatgpt.com "Get started with the Companies House API"
[20]: https://developer.company-information.service.gov.uk/developer-guidelines "Developer Guidelines"
[21]: https://docs.exa.ai/llms.txt?utm_source=chatgpt.com "llms.txt"
[22]: https://exa.ai/docs/reference/rate-limits "Rate Limits - Exa"
[23]: https://newsapi.org/docs "Documentation - News API"
[24]: https://www.gdeltproject.org/?utm_source=chatgpt.com "The GDELT Project"
[25]: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ "GDELT DOC 2.0 API Debuts! – The GDELT Project"
[26]: https://docs.searxng.org/admin/installation-searxng.html?utm_source=chatgpt.com "Step by step installation"
[27]: https://docs.searxng.org/admin/searx.limiter.html "Limiter — SearXNG Documentation (2026.3.29+7ac4ff39f)"
[28]: https://docs.searxng.org/src/searx.botdetection.html?utm_source=chatgpt.com "Bot Detection"
[29]: https://data.crunchbase.com/docs/using-the-api "Using the API"
[30]: https://api.opencorporates.com/documentation/API-Reference "API Reference: version 0.4.8 :: OpenCorporates API"
[31]: https://www.openfigi.com/api/overview?utm_source=chatgpt.com "Overview | OpenFIGI"
[32]: https://www.openfigi.com/api/documentation "Documentation | OpenFIGI"
[33]: https://langfuse.com/docs "Overview - Langfuse"
[34]: https://langfuse.com/docs/observability/overview "LLM Observability & Application Tracing (Open Source) - Langfuse"
[35]: https://api.slack.com/incoming-webhooks "Sending messages using incoming webhooks | Slack Developer Docs"
[36]: https://docs.slack.dev/security?utm_source=chatgpt.com "Security best practices | Slack Developer Docs"
[37]: https://platform.openai.com/docs/api-reference/responses/list?ref=test-ippon.ghost.io "Responses | OpenAI API Reference"
[38]: https://platform.openai.com/docs/api-reference/project-rate-limits?ref=applied-language-understanding.ghost.io "Rate Limits | OpenAI API Reference"
[39]: https://platform.openai.com/docs/models/compare?model=gpt-5.1-codex "Compare models | OpenAI API"
[40]: https://docs.anthropic.com/en/api/overview?utm_source=chatgpt.com "API Overview - Claude API Docs - Claude Console"
[41]: https://docs.anthropic.com/en/api/rate-limits "Rate limits - Claude API Docs"
[42]: https://docs.temporal.io/develop/typescript?utm_source=chatgpt.com "TypeScript SDK developer guide | Temporal Platform Documentation"
[43]: https://docs.temporal.io/workflow-execution "Temporal Workflow Execution overview | Temporal Platform Documentation"
[44]: https://www.typescriptlang.org/tsconfig/strict.html "TypeScript: TSConfig Option: strict"
[45]: https://docs.pydantic.dev/latest/ "Welcome to Pydantic - Pydantic Validation"
[46]: https://spark.apache.org/docs/latest/configuration.html "Configuration - Spark 4.1.1 Documentation"
[47]: https://spark.apache.org/docs/latest/sql-performance-tuning.html "Performance Tuning - Spark 4.1.1 Documentation"
[48]: https://docs.temporal.io/develop/typescript/core-application "Core application - TypeScript SDK | Temporal Platform Documentation"
[49]: https://docs.pola.rs/user-guide/lazy/using/ "Usage - Polars user guide"

# 12. Extra information
* Last dev session checks
1. Opencode codex first agent:
I reviewed the latest remote commit trail on develop and the session hardening commit, then appended cross-referenced documentation updates so the migration reality, boundary strictness work, and external API contract inventory are linked as one narrative. Specifically, I validated 68cd20e (latest remote docs inventory), eed7ff2 (our session strictness hardening), and 8562cb0 (quality baseline), and embedded this traceability directly into the corresponding markdowns.
- Updated docs/audit/VALIDATION_SCHEMA_STRICTNESS_AUDIT_2026-03-31.md with:
  - active/request-boundary state + future hardening backlog
  - new Commit Traceability (Session + Remote) section linking eed7ff2, 68cd20e, 8562cb0
- Updated docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md with:
  - runtime consumption split (legacy vs graph vs shared)
  - new Commit Review Cross-Reference (2026-03-31) section tying inventory governance to strict schema boundaries
- Updated docs/architecture/research-graph.md with:
  - corrected STORY status table (landed/partially landed)
  - Current Branch Reality section
  - new Commit Reality Review (origin/develop) with 7ac122a, 4be64bc, 43c4999, a99bf24, plus eed7ff2 / 68cd20e / 8562cb0
- Current git state: branch develop is aligned with origin/develop, and these 3 markdown files are modified locally (not committed yet).
2. Second codex agent:
• I reviewed the latest remote develop commits and documented the branch reality in the two markdown files that were directly affected by our findings: docs/architecture/research-graph.md now reflects that STORY-077 through
  STORY-079 have landed in part and clarifies that the graph is the intended successor but not yet the canonical end-to-end runtime, while docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md now explains which APIs are shared,
  which are mostly legacy-pipeline integrations, and which are mainly graph-path search integrations. There were no assistant-authored code commits in this session to document, so I only appended the architecture and integration
  findings we established from the current branch state and recent remote history.
  Updated files:
  - docs/architecture/research-graph.md
  - docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md

* External API Inventory
docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md

* Reality Assesment for Boundaries Quality
.sisyphus/drafts/langgraph-migration-boundary-reality.md


* Current state (lastest commit) - Two Conflicting Systems: Legacy Codebase (Linear Stages pipeline, more mature, still not entirely working end-to-end, crowded with mock and hardcoded values/objects) vs Newer Graph System (DAG pipeline, also crowded not only with mock and hardcoded values but with placeholder entire components)

• The recent commit pattern says: the graph system got a short, concentrated
  burst of attention, but the legacy pipeline is still where most real behavior
  and operational depth live. On origin/develop, the graph work is basically a
  four-commit sequence on March 27: STORY-076, 077, 078, 079. By contrast, the
  linear pipeline accumulated many more commits across discovery, enrichment,
  gates, scoring, provenance, contradiction handling, exports, and integration
  tests. So attention recently shifted to graph architecture, but delivery depth
  is still weighted toward the legacy pipeline.

  The blurring is happening more through the compatibility posture than through
  pure graph work. The graph side already added an explicit migration seam in
  src/solstein/research/graph/executor.py with a “stable public interface”
  shaped to match run_market_intelligence(), while the broader codebase is full
  of backward-compat aliases, re-exports, deprecated wrappers, and legacy-
  preserving shims. So the bigger standards problem is not “the graph is taking
  over too much”; it is that the repo keeps preserving old interfaces while
  adding new ones, which obscures the canonical behavior.

  If the goal is to raise standards and stop blurring expectations, the clean
  read is: the graph is the intended future, but the legacy pipeline is still
  the only trustworthy source of behavior. That means you should stop adding
  compatibility patches now, declare one canonical runtime, and use the legacy
  pipeline only as a reference spec for parity. If you continue the graph
  migration, it should be a replacement program, not an interoperability
  program.

* Current Reality Extra Details
- The pipeline.py module contains key logic around line 198, managing core data processing steps.
- Topology definitions include important placeholder lines at 151, 179, 291, and 314, indicating where dynamic components await full implementation.
- The graph executor's main research run is located at line 305, central to orchestrating graph-based workflows.
- The review router around line 164 handles critical routing for user review flows.
- The api main module integrates review and research job functionality, primarily around lines 222-224.
- The graph implementation remains partial, requiring further development to support full execution scenarios.
- Git history reveals several recent commits focused on intent clarification and incremental feature additions relevant to the LangGraph system.
- External API documentation references remain essential for understanding integration points and expected data contracts.
- Pending work includes completing LangGraph system components and enhancing integration robustness to prevent the need for retroactive patches.
- Opportunity exists to streamline integration across modules to enable smoother workflows and reduce technical debt from patchwork fixes.
You are right, and the code confirms exactly that: branch intent is migration to LangGraph (commit sequence 7ac122a → 4be64bc → 43c4999 → a99bf24), but current runtime reality is still mixed—legacy linear research is the only behaviorally complete flow, while LangGraph is partially complete. Legacy has full staged execution with gates/checkpoints/artifacts in src/solstein/research/pipeline.py:198, but in LangGraph the orchestration skeleton is present and collection nodes are real, while core downstream nodes are still placeholders (src/solstein/research/graph/topology.py:151, src/solstein/research/graph/topology.py:179, src/solstein/research/graph/topology.py:291, src/solstein/research/graph/topology.py:314); checkpointer/review resume plumbing exists in src/solstein/research/graph/executor.py:152 and src/solstein/api/routers/review.py:137, yet I do not find a clear production caller path actively executing run_graph_research outside that resume seam. The biggest drift is contract drift: legacy operates around domain-oriented adapter+pipeline contracts (src/solstein/adapters/protocols.py:29, src/solstein/research/discovery.py:98, src/solstein/research/gather.py:128), while graph state is raw-fact TypedDict transport (src/solstein/research/graph/state.py:40) with looser boundary semantics; that is why retro-compat patches keep appearing. So yes: first establish trust boundaries from actual ingress points in code, then anchor each external boundary with official API docs (which I collected for GitHub REST, Companies House, Google Custom Search, SearXNG, SEC EDGAR, Supabase Auth/PostgREST), and only then define adapters + canonical schemas so both systems converge instead of drifting further.








