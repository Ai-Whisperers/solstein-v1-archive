# External API Inventory - 2026-03-31

This file is a concise inventory of the external APIs and third-party services currently referenced by the Solstein `develop` branch.

It separates:

- active product/data dependencies
- active platform/notification dependencies
- supported LLM provider APIs wired into the runtime

Notes:

- "Official docs" means the provider's own documentation site.
- Some integrations are wrappers around unofficial or self-hosted surfaces. Those are called out explicitly.
- Protocol-only integrations like generic `SMTP` are not listed as vendor APIs.

## Active Product, Search, and Data APIs

1. **Supabase**
   Role: auth, database backend, storage, realtime subscriptions.
   Official docs: https://supabase.com/docs

2. **GitHub REST API**
   Role: repository and engineering-signal enrichment.
   Official docs: https://docs.github.com/en/rest

3. **SEC EDGAR APIs**
   Role: U.S. public-company filings and financial-source enrichment.
   Official docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

4. **Companies House Public Data API**
   Role: UK company registry enrichment.
   Official docs: https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference

5. **Exa Search API**
   Role: structured web search and web-content retrieval.
   Official docs: https://exa.ai/docs/reference/search-api-guide

6. **NewsAPI**
   Role: news retrieval in the older/news connector surface and related tests/docs.
   Official docs: https://newsapi.org/docs

7. **GDELT**
   Role: news aggregation backend introduced in the newer news flow.
   Official docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

8. **SearXNG**
   Role: primary metasearch backend for web search.
   Official docs: https://docs.searxng.org/
   Caveat: self-hosted metasearch service, not a single-source commercial API.

9. **Google Custom Search JSON API**
   Role: fallback web-search path when SearXNG is unavailable.
   Official docs: https://developers.google.com/custom-search/v1/overview

10. **Yahoo Finance via `yfinance`**
    Role: market/quote data enrichment.
    Official docs: https://ranaroussi.github.io/yfinance/
    Caveat: this is an unofficial wrapper over Yahoo Finance public surfaces, not an official Yahoo Finance enterprise API.

11. **Crunchbase Data API**
    Role: funding and company intelligence.
    Official docs: https://data.crunchbase.com/docs/welcome-to-crunchbase-data

12. **OpenCorporates API**
    Role: registry/entity lookup.
    Official docs: https://api.opencorporates.com/documentation/API-Reference

13. **OpenFIGI API**
    Role: financial-identifier lookup.
    Official docs: https://www.openfigi.com/api/documentation

14. **PatentsView**
    Role: patent search and patent-enrichment surfaces.
    Official docs: https://search.patentsview.org/docs/

## Active Platform and Notification APIs

15. **Langfuse**
    Role: LLM tracing, prompt management, and evaluation telemetry.
    Official docs: https://langfuse.com/docs

16. **Slack Incoming Webhooks**
    Role: Slack notifications.
    Official docs: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/

## Supported LLM Provider APIs Wired Into Runtime

17. **OpenAI API**
    Role: embeddings, structured output, and general LLM fallback/support.
    Official docs: https://platform.openai.com/docs/overview

18. **Anthropic Claude API**
    Role: primary Claude provider support and Instructor-based structured extraction.
    Official docs: https://platform.claude.com/docs/en/overview

19. **Groq API**
    Role: OpenAI-compatible fast inference provider.
    Official docs: https://console.groq.com/docs/quickstart

20. **Fireworks AI API**
    Role: OpenAI-compatible inference provider.
    Official docs: https://docs.fireworks.ai/api-reference/introduction

21. **Mistral AI API**
    Role: supported cloud LLM provider.
    Official docs: https://docs.mistral.ai/getting-started/quickstart

22. **DeepInfra API**
    Role: supported OpenAI-compatible cloud inference provider.
    Official docs: https://deepinfra.com/docs

23. **Google Gemini API**
    Role: supported Google-hosted model provider.
    Official docs: https://ai.google.dev/gemini-api/docs

24. **NVIDIA NIM / API Catalog**
    Role: supported NVIDIA-hosted model provider.
    Official docs: https://docs.api.nvidia.com/nim/docs/introduction

25. **Cerebras Inference API**
    Role: supported Cerebras-hosted inference provider.
    Official docs: https://inference-docs.cerebras.ai/introduction

26. **Moonshot AI / Kimi API**
    Role: supported Kimi provider.
    Official docs: https://platform.moonshot.ai/docs/introduction

27. **SiliconFlow API**
    Role: supported SiliconFlow-hosted model provider.
    Official docs: https://docs.siliconflow.com/en/api-reference/introduction

28. **Alibaba Cloud Model Studio / Qwen API**
    Role: supported Alibaba-hosted model provider.
    Official docs: https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen

29. **Ollama API**
    Role: local/self-hosted model runtime option.
    Official docs: https://docs.ollama.com/api
    Caveat: usually local or self-hosted rather than third-party SaaS.

## Not Counted As Current Official API Dependencies

- **LinkedIn official API**: not a first-class official integration in the current branch; repo surfaces are heuristic/placeholder and not equivalent to a verified LinkedIn API contract.
- **Proxycurl, BuiltWith, PitchBook**: documented/prospective surfaces exist, but they are not the cleanest current end-to-end dependency set to treat as active runtime integrations.
- **Generic SMTP**: used for email delivery, but it is a protocol integration, not one provider-specific API.

## Repo Anchors

Primary repo references used to compile this list:

- `docs/API_PROVIDERS_GUIDE.md`
- `docs/reference/external-integrations/README.md`
- `docs/reference/external-integrations/AUDIT_2026-03-25.md`
- `.env.example`
- `src/solstein/config.py`
- `src/solstein/llm/provider_strategies.py`
- `src/solstein/notifications/channels.py`

## Runtime Consumption Notes

The APIs above are not consumed uniformly by the two research/orchestration
paths currently present in the repository.

### Shared or Near-Shared Research Integrations

- **GitHub REST API**: used by graph collection nodes via `GitHubAgent`; similar
  engineering-signal behavior also exists in the broader legacy research stack.
- **SEC EDGAR APIs**: used directly by graph `sec_filings` and also by legacy
  enrichment/connectors.
- **Companies House Public Data API**: used directly by graph
  `companies_house` and also by legacy enrichment/connectors.

### Primarily Legacy Stage-Pipeline / Registry-Driven Integrations

- **Exa Search API**
- **Yahoo Finance via `yfinance`**
- **Crunchbase Data API**
- **NewsAPI**
- **OpenCorporates API**
- **OpenFIGI API**
- **PatentsView**

These are wired mainly through the adapter registry, unified adapters, and
legacy enrichment/discovery flows. They are not currently exposed through the
LangGraph runtime as a single shared integration layer.

### Primarily Graph-Path Search Runtime

- **SearXNG**
- **Google Custom Search JSON API**

These power the newer graph-oriented web search path via `WebSearchAgent`
and its search backend dispatcher. Their usage pattern is not the same as the
legacy Exa-centric discovery/enrichment path.

### Platform-Wide Rather Than Pipeline-Specific

- **Supabase**
- **Langfuse**
- **Slack Incoming Webhooks**
- **Supported LLM provider APIs**

These are cross-cutting platform dependencies. They support the wider product
runtime and observability surface, but they are not evidence that the legacy
pipeline and graph runtime share one canonical data-integration stack.

## Commit Review Cross-Reference (2026-03-31)

- Latest remote commit reviewed: `68cd20e` (`docs: add external API inventory summary`).
  - This file remains the canonical external-integration inventory produced by that commit.

- Session hardening commit reviewed: `eed7ff2` (`audit: harden validation schema strictness at boundaries`).
  - Boundary strictness work in API/router/schema layers depends on accurate external contract boundaries documented here.
  - This commit-to-doc linkage is intentional: strict request schemas should be derived from provider contracts in this inventory, not inferred ad hoc.

- Immediate historical baseline reviewed: `8562cb0` (`chore(lint): enforce full ruff compliance across src and tests`).
  - Quality-only baseline commit; used here as the pre-boundary-hardening reference point.

- Migration drift note:
  - The inventory includes APIs consumed by both legacy stage-pipeline and graph-path runtimes.
  - Contract governance should converge through adapter boundaries so both runtimes normalize to one canonical internal shape.
