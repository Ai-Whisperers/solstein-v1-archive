# Self-Hosted AI Infrastructure Research
## 150+ Tools for Autonomous Agent VPS Setup
### Generated: 2026-04-07

---

## QUICK REFERENCE: TOP PICKS FOR OUR VPS

| Priority | Tool | Replaces | RAM | Why |
|----------|------|----------|-----|-----|
| ★★★ | SearXNG | Tavily ($20/mo) | 256 MB | Free web search for agents |
| ★★★ | Firecrawl | Firecrawl SaaS ($19-399/mo) | 1-2 GB | Web scraping to markdown |
| ★★★ | Browserless | BrowserBase ($200+/mo) | 1-2 GB | Headless Chrome API |
| ★★★ | Piston | E2B ($0.01/exec) | 1-2 GB | Code execution sandbox 60+ langs |
| ★★★ | ntfy | Push notification SaaS | 64 MB | Notifications for agents |
| ★★ | Gotenberg | CloudConvert ($8/mo) | 512 MB | HTML/Office to PDF |
| ★★ | Stirling PDF | Adobe Acrobat ($20/mo) | 512 MB | PDF manipulation API |
| ★★ | Changedetection.io | Visualping ($10/mo) | 256 MB | Monitor web changes |
| ★★ | LibreTranslate | Google Translate API | 1-2 GB | Free translation API |
| ★★ | Meilisearch | Algolia ($50+/mo) | 512 MB | Full-text search |
| ★★ | Dify | LangChain Cloud | 4 GB | Visual AI workflow builder |
| ★★ | Langfuse | LangSmith ($20+/mo) | 1-2 GB | LLM observability |
| ★ | Miniflux | Feedly Pro ($8/mo) | 128 MB | RSS monitoring for agents |
| ★ | Hoarder/Karakeep | Pocket Premium | 512 MB | AI bookmark manager |
| ★ | Gitea + Woodpecker | GitHub Actions (limits) | 1 GB | Self-hosted Git + CI/CD |
| ★ | Healthchecks.io | Cronitor ($20/mo) | 256 MB | Cron job monitoring |

**Estimated total RAM needed for ★★★ tools: ~5 GB (VPS has 26 GB free)**
**Estimated savings: $300-800/month in SaaS subscriptions**

---

# CATEGORY 1: WEB SEARCH (Replace Tavily/SerpAPI/Google)

## 1. SearXNG ★★★
- **What**: Privacy-respecting metasearch engine, aggregates 70+ search engines (Google, Bing, DuckDuckGo, etc.)
- **Stars**: ~14,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (official docker-compose)
- **Replaces**: Tavily ($20/mo), Google Custom Search API ($5/1000 queries), SerpAPI ($50+/mo)
- **MCP Server**: Yes (searxng-mcp-server)
- **Agent Value**: Direct replacement for Hermes web search backend

## 2. Whoogle Search
- **What**: Self-hosted Google search proxy, no ads/tracking
- **Stars**: ~9,500+
- **RAM**: 128-256 MB
- **Docker**: Yes
- **Replaces**: Google Search API

## 3. MeiliSearch
- **What**: Fast full-text search engine, typo-tolerant, faceted search
- **Stars**: ~48,000+
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes (official: getmeili/meilisearch)
- **Replaces**: Algolia ($1+/1000 requests), Elasticsearch managed
- **MCP Server**: Yes (meilisearch-mcp)

## 4. Typesense
- **What**: Open-source search engine, alternative to Algolia
- **Stars**: ~21,000+
- **RAM**: 512 MB - 4 GB
- **Docker**: Yes
- **Replaces**: Algolia, Elasticsearch Cloud

## 5. Manticore Search
- **What**: Full-text search engine with SQL interface, Elasticsearch alternative
- **Stars**: ~9,000+
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes
- **Replaces**: Elasticsearch Cloud, Solr managed

---

# CATEGORY 2: WEB SCRAPING & CRAWLING

## 6. Firecrawl (Self-hosted) ★★★
- **What**: Web scraping API that converts pages to LLM-ready markdown
- **Stars**: ~25,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (docker-compose for self-hosting)
- **Replaces**: Firecrawl SaaS ($19-$399/mo), ScrapingBee ($49+/mo), Apify
- **MCP Server**: Yes (official firecrawl-mcp)
- **Agent Value**: Agents can scrape any website into clean markdown for analysis

## 7. Crawl4AI
- **What**: LLM-friendly web crawler, async, outputs structured data
- **Stars**: ~30,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes
- **Replaces**: Apify ($49+/mo), ScrapingBee, Diffbot ($299+/mo)

## 8. Jina Reader
- **What**: Converts any URL to LLM-friendly text
- **Stars**: ~7,000+
- **RAM**: 1-2 GB
- **Docker**: Yes
- **Replaces**: Jina Reader API (limited free tier)
- **MCP Server**: Yes (jina-reader-mcp)

## 9. Trafilatura
- **What**: Python library for web text extraction, article extraction
- **Stars**: ~3,500+
- **RAM**: 128-256 MB
- **Replaces**: Diffbot article extraction, readability APIs

## 10. Scrapy
- **What**: Python web scraping framework, highly extensible
- **Stars**: ~53,000+
- **RAM**: 256-512 MB
- **Docker**: Community images

## 11. Crawlee
- **What**: Web scraping/crawling library (by Apify team), JS/Python
- **Stars**: ~16,000+
- **RAM**: 512 MB - 2 GB
- **Replaces**: Apify platform ($49+/mo)

## 12. SingleFile
- **What**: Saves complete web pages as single HTML files
- **Stars**: ~16,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (CLI version)

---

# CATEGORY 3: BROWSER AUTOMATION

## 13. Browserless ★★★
- **What**: Headless Chrome as a service, REST API for screenshots, PDFs, scraping
- **Stars**: ~9,000+
- **RAM**: 1-2 GB per Chrome instance
- **Docker**: Yes (official, primary deployment)
- **Replaces**: Browserless SaaS ($200+/mo), BrowserBase, ScrapingBee
- **MCP Server**: Yes (browserless-mcp-server)
- **Agent Value**: Agents can interact with any website, fill forms, take screenshots

## 14. Playwright
- **What**: Browser automation for Chromium, Firefox, WebKit (Microsoft)
- **Stars**: ~68,000+
- **RAM**: 512 MB - 2 GB per browser
- **Docker**: Yes (official mcr.microsoft.com/playwright)
- **MCP Server**: Yes (official by Microsoft: playwright-mcp-server)

## 15. Puppeteer
- **What**: Node.js library for controlling Chrome/Chromium (Google)
- **Stars**: ~89,000+
- **RAM**: 512 MB - 1.5 GB per instance
- **Docker**: Yes

## 16. Selenium Grid
- **What**: Distributed browser automation infrastructure
- **Stars**: ~31,000+
- **RAM**: 1-4 GB for grid
- **Docker**: Yes (official selenium/hub)

## 17. Splash
- **What**: Lightweight scriptable browser for web scraping (Scrapinghub)
- **Stars**: ~4,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes

---

# CATEGORY 4: DOCUMENT PROCESSING & CONVERSION

## 18. Docling (IBM)
- **What**: Document parsing - PDFs, DOCX, PPTX to structured data/markdown
- **Stars**: ~18,000+
- **RAM**: 2-4 GB (ML models)
- **Docker**: Yes
- **Replaces**: AWS Textract, Google Document AI, Azure Form Recognizer
- **MCP Server**: Yes (docling-mcp)

## 19. Stirling PDF ★★
- **What**: All-in-one PDF manipulation (merge, split, convert, OCR, compress, etc.)
- **Stars**: ~50,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes (official: frooodle/s-pdf)
- **Replaces**: Adobe Acrobat ($20+/mo), SmallPDF, iLovePDF
- **Agent Value**: Agents can manipulate any PDF via REST API

## 20. Gotenberg ★★
- **What**: Docker-based API for PDF conversions (HTML, Office → PDF)
- **Stars**: ~8,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes (official: gotenberg/gotenberg)
- **Replaces**: CloudConvert ($8+/mo), DocRaptor, Zamzar API

## 21. Apache Tika
- **What**: Content detection and extraction from 1000+ file types
- **Stars**: ~2,500+
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes (official: apache/tika)
- **MCP Server**: Yes (tika-mcp-server)

## 22. Pandoc
- **What**: Universal document converter (markdown, LaTeX, DOCX, HTML, etc.)
- **Stars**: ~35,000+
- **RAM**: 128-512 MB
- **Docker**: Yes (pandoc/latex)

## 23. Unstructured
- **What**: ETL for documents - extracts text from PDFs, images, HTML
- **Stars**: ~10,000+
- **RAM**: 2-4 GB (with ML models)
- **Docker**: Yes
- **Replaces**: Unstructured.io SaaS ($500+/mo), AWS Textract
- **MCP Server**: Yes (unstructured-mcp)

## 24. LibreOffice Headless
- **What**: Document conversion server (DOCX, XLSX, PPTX to PDF)
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes (used by Gotenberg internally)

## 25. MegaParse
- **What**: Parser for complex documents for RAG/LLM
- **Stars**: ~3,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

---

# CATEGORY 5: OCR & TEXT RECOGNITION

## 26. Surya
- **What**: OCR, layout analysis, reading order, table recognition (90+ languages)
- **Stars**: ~16,000+
- **RAM**: 2-4 GB (GPU recommended)
- **Replaces**: Google Cloud Vision OCR, AWS Textract, Mathpix

## 27. Marker
- **What**: Converts PDFs to markdown with high accuracy (uses Surya)
- **Stars**: ~19,000+
- **RAM**: 2-6 GB (GPU recommended)
- **Replaces**: Mathpix ($10+/mo), Adobe PDF extraction

## 28. PaddleOCR
- **What**: Multi-language OCR toolkit, very accurate
- **Stars**: ~45,000+
- **RAM**: 1-4 GB
- **Docker**: Yes (official)
- **Replaces**: Google Cloud Vision, AWS Textract, ABBYY Cloud

## 29. Tesseract OCR
- **What**: Open-source OCR engine by Google, 100+ languages
- **Stars**: ~63,000+
- **RAM**: 256-512 MB
- **Docker**: Yes

## 30. EasyOCR
- **What**: Python OCR library, 80+ languages, deep learning based
- **Stars**: ~24,000+
- **RAM**: 1-2 GB

## 31. GOT-OCR
- **What**: General OCR Theory - next-gen OCR with LLM, handles math/charts
- **Stars**: ~7,000+
- **RAM**: 4-8 GB (GPU recommended)
- **Replaces**: Mathpix ($10+/mo)

## 32. Nougat (Meta)
- **What**: PDF to markdown for academic documents
- **Stars**: ~9,000+
- **RAM**: 4-8 GB (GPU recommended)

---

# CATEGORY 6: CODE EXECUTION & DEV ENVIRONMENTS

## 33. Piston ★★★
- **What**: Code execution engine, 60+ languages, sandboxed, REST API
- **Stars**: ~5,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (official: ghcr.io/engineer-man/piston)
- **Replaces**: E2B ($0.01/exec), code execution SaaS
- **Agent Value**: Agents can run any code safely in sandboxed containers

## 34. Judge0
- **What**: Online code execution system, 60+ languages, sandboxed
- **Stars**: ~2,500+
- **RAM**: 2-4 GB (requires Redis, PostgreSQL)
- **Docker**: Yes
- **Replaces**: E2B, HackerRank API

## 35. code-server
- **What**: VS Code in the browser
- **Stars**: ~70,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (official: codercom/code-server)
- **Agent Value**: Full IDE accessible remotely for code editing

## 36. JupyterHub / JupyterLab
- **What**: Multi-user Jupyter notebook server
- **Stars**: ~15,000+
- **RAM**: 512 MB - 2 GB per user
- **Docker**: Yes (official: jupyter/datascience-notebook)

## 37. Gitea ★★
- **What**: Lightweight self-hosted Git service (GitHub alternative)
- **Stars**: ~46,000+
- **RAM**: 512 MB
- **Docker**: Yes (official: gitea/gitea)
- **Agent Value**: Mirror all repos, agents can create PRs, manage issues

## 38. Forgejo
- **What**: Gitea fork, community-governed
- **Stars**: ~6,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 39. Woodpecker CI
- **What**: Container-native CI/CD, integrates with Gitea/GitHub
- **Stars**: ~4,500+
- **RAM**: 256 MB - 1 GB
- **Docker**: Yes (official: woodpeckerci/woodpecker-server)
- **Agent Value**: Auto-test code on every push, agents trigger CI

---

# CATEGORY 7: LLM SERVING & INFERENCE

## 40. vLLM
- **What**: High-throughput LLM serving with PagedAttention
- **RAM**: GPU required (NVIDIA), 8 GB+ VRAM
- **Docker**: Yes (vllm/vllm-openai)

## 41. llama.cpp
- **What**: C/C++ LLM inference, CPU + GPU, GGUF format
- **RAM**: 4-64 GB depending on model, CPU-friendly
- **Docker**: Yes

## 42. Ollama
- **What**: User-friendly local LLM runner with REST API
- **RAM**: 4 GB+ minimum, 8 GB+ recommended
- **Docker**: Yes (official: ollama/ollama)

## 43. Text Generation Inference (TGI)
- **What**: HuggingFace's production LLM serving
- **RAM**: GPU required, 16 GB+ VRAM
- **Docker**: Yes (official)

## 44. LiteLLM ★★★ (already deployed)
- **What**: Unified OpenAI-compatible proxy for 100+ providers
- **RAM**: 512 MB
- **Docker**: Yes
- **Agent Value**: Single API endpoint, cost tracking, failover

## 45. LocalAI
- **What**: Drop-in OpenAI API replacement (LLMs, images, audio, embeddings)
- **RAM**: 4-32 GB depending on models
- **Docker**: Yes (localai/localai)

## 46. TabbyAPI
- **What**: FastAPI-based EXL2 inference server, OpenAI-compatible
- **RAM**: GPU required, 6 GB+ VRAM

## 47. Aphrodite Engine
- **What**: vLLM fork optimized for inference, many quant formats
- **RAM**: GPU preferred, 8 GB+ VRAM

---

# CATEGORY 8: VECTOR DATABASES & EMBEDDINGS

## 48. Qdrant (already deployed) ★★
- **What**: High-performance vector similarity search
- **RAM**: 1-8 GB
- **Docker**: Yes (qdrant/qdrant)

## 49. Chroma
- **What**: Lightweight embeddable vector database
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes (chromadb/chroma)

## 50. Weaviate
- **What**: Full-featured vector DB with built-in vectorization
- **RAM**: 2-8 GB
- **Docker**: Yes

## 51. pgvector
- **What**: PostgreSQL extension for vector search (you already have Postgres!)
- **RAM**: Same as PostgreSQL
- **Agent Value**: No new service needed, just add extension to existing PG

## 52. Milvus
- **What**: Cloud-native vector DB, supports billions of vectors
- **RAM**: 8 GB+ (heavy)
- **Docker**: Yes

## 53. LanceDB
- **What**: Serverless embedded vector database
- **RAM**: 256 MB+
- **Embedded library, no server needed**

## 54. TEI (Text Embeddings Inference)
- **What**: HuggingFace's embedding server, OpenAI-compatible
- **RAM**: 2-4 GB (CPU or GPU)
- **Docker**: Yes (official)
- **Agent Value**: Generate embeddings locally instead of paying OpenAI

## 55. Infinity Embedding Server
- **What**: High-throughput embedding inference, OpenAI-compatible
- **RAM**: 1-4 GB
- **Docker**: Yes (michaelf34/infinity)

## 56. FastEmbed
- **What**: Lightweight ONNX-based embeddings by Qdrant, CPU-optimized
- **RAM**: 512 MB - 1 GB

---

# CATEGORY 9: RAG / AI PLATFORMS & AGENT FRAMEWORKS

## 57. Dify ★★
- **What**: Full AI app development platform, visual workflows, RAG, agents
- **Stars**: ~60,000+
- **RAM**: 4 GB+
- **Docker**: Yes (docker-compose)
- **Agent Value**: Build complex AI workflows visually, expose as APIs

## 58. Flowise
- **What**: Drag-and-drop LLM flow builder, LangChain UI
- **Stars**: ~35,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (flowiseai/flowise)

## 59. Langflow
- **What**: Visual framework for multi-agent and RAG apps
- **Stars**: ~40,000+
- **RAM**: 2-4 GB
- **Docker**: Yes (langflowai/langflow)

## 60. AnythingLLM
- **What**: All-in-one AI app, built-in RAG, multi-user, agent capabilities
- **Stars**: ~30,000+
- **RAM**: 2-4 GB
- **Docker**: Yes (mintplexlabs/anythingllm)

## 61. RAGFlow
- **What**: RAG engine with deep document understanding
- **Stars**: ~25,000+
- **RAM**: 4 GB+
- **Docker**: Yes

## 62. Haystack (deepset)
- **What**: End-to-end NLP/RAG framework, pipeline architecture
- **RAM**: 2-8 GB
- **Docker**: Yes

## 63. AutoGen (Microsoft)
- **What**: Multi-agent conversation framework, tool use, code execution
- **RAM**: 1-2 GB
- **Docker**: Yes

## 64. CrewAI
- **What**: Framework for orchestrating autonomous AI agents
- **RAM**: 1-2 GB
- **Docker**: Yes

## 65. OpenHands (formerly OpenDevin)
- **What**: Autonomous AI software engineer, writes code, uses terminal
- **Stars**: ~45,000+
- **RAM**: 4-8 GB
- **Docker**: Yes (ghcr.io/all-hands-ai/openhands)

## 66. SWE-agent
- **What**: AI agent for solving GitHub issues (Princeton)
- **RAM**: 2-4 GB
- **Docker**: Yes

## 67. Aider
- **What**: AI pair programmer in terminal, git-aware
- **Stars**: ~25,000+
- **RAM**: 256 MB
- **Docker**: Yes

## 68. Open Interpreter
- **What**: Natural language to code execution, local ChatGPT Code Interpreter
- **RAM**: 1-2 GB

---

# CATEGORY 10: WORKFLOW AUTOMATION

## 69. n8n (already deployed) ★★
- **What**: Workflow automation, 400+ integrations, AI agent nodes
- **RAM**: 1-2 GB
- **Docker**: Yes (n8nio/n8n)

## 70. Temporal
- **What**: Durable workflow execution engine
- **RAM**: 2-4 GB
- **Docker**: Yes

## 71. Apache Airflow
- **What**: Workflow orchestration, DAG-based, REST API
- **RAM**: 2-4 GB
- **Docker**: Yes (apache/airflow)

## 72. Huginn
- **What**: Agents that monitor and act on your behalf, event-driven
- **Stars**: ~44,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (huginn/huginn)

## 73. Activepieces
- **What**: Open-source Zapier alternative, visual flow builder
- **Stars**: ~10,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

## 74. Windmill
- **What**: Developer-oriented workflow engine, Python/TS/Go/Bash
- **Stars**: ~10,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

## 75. webhook (adnanh)
- **What**: Lightweight webhook server, define hooks in JSON/YAML
- **RAM**: 64 MB
- **Docker**: Single binary

---

# CATEGORY 11: NOTIFICATIONS & COMMUNICATION

## 76. ntfy ★★★
- **What**: Push notifications via HTTP PUT/POST, dead simple
- **Stars**: ~19,000+
- **RAM**: 64 MB
- **Docker**: Yes (binwiederhier/ntfy)
- **Agent Value**: Agents can notify you of anything via simple curl

## 77. Gotify
- **What**: Self-hosted push notification server with REST API
- **Stars**: ~12,000+
- **RAM**: 128 MB
- **Docker**: Yes (gotify/server)

## 78. Apprise
- **What**: Unified notification library, 90+ services (Slack, Telegram, email, etc.)
- **RAM**: 256 MB
- **Docker**: Yes (apprise-api)

## 79. Mailpit
- **What**: SMTP testing tool with web UI and REST API (MailHog successor)
- **Stars**: ~6,000+
- **RAM**: 128 MB
- **Docker**: Yes (axllent/mailpit)

## 80. Listmonk
- **What**: Self-hosted newsletter/mailing list manager
- **Stars**: ~15,000+
- **RAM**: 256 MB
- **Docker**: Yes (listmonk/listmonk)

## 81. Postal
- **What**: Full mail server for sending/receiving, REST API
- **RAM**: 1-2 GB
- **Docker**: Yes

---

# CATEGORY 12: KNOWLEDGE BASES & NOTES

## 82. Outline
- **What**: Beautiful wiki/knowledge base, Markdown, REST API
- **Stars**: ~29,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

## 83. Wiki.js
- **What**: Powerful wiki with GraphQL API
- **Stars**: ~25,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes (requarks/wiki)

## 84. BookStack
- **What**: Wiki/documentation platform with REST API
- **Stars**: ~15,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 85. Trilium
- **What**: Hierarchical note-taking, REST API, scripting
- **Stars**: ~27,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (zadam/trilium)

## 86. Memos
- **What**: Lightweight memo/note hub, REST API
- **Stars**: ~35,000+
- **RAM**: 128 MB
- **Docker**: Yes (neosmemo/memos)

## 87. SiYuan
- **What**: Local-first knowledge management, block-based, REST API
- **RAM**: 512 MB
- **Docker**: Yes

---

# CATEGORY 13: RSS / FEED MONITORING

## 88. Miniflux ★★
- **What**: Minimalist RSS reader with excellent REST API
- **Stars**: ~7,000+
- **RAM**: 128-256 MB
- **Docker**: Yes (miniflux/miniflux)
- **Agent Value**: Agents monitor RSS feeds for news, research, competitor updates

## 89. FreshRSS
- **What**: Full-featured RSS aggregator, Google Reader API compatible
- **Stars**: ~10,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (freshrss/freshrss)

## 90. Changedetection.io ★★
- **What**: Website change detection and monitoring, REST API, webhooks
- **Stars**: ~20,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (dgtlmoon/changedetection.io)
- **Replaces**: Visualping ($10+/mo), Distill.io
- **Agent Value**: Agents get alerted when any webpage changes

---

# CATEGORY 14: LINK SAVING & BOOKMARKS

## 91. Linkwarden
- **What**: Collaborative bookmark manager, auto-screenshots, PDF archiving
- **Stars**: ~9,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 92. Hoarder (now Karakeep)
- **What**: AI-powered bookmark manager, auto-tagging, full-text search
- **Stars**: ~8,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 93. Wallabag
- **What**: Read-it-later / article archiver with REST API
- **Stars**: ~10,000+
- **RAM**: 256-512 MB
- **Docker**: Yes (wallabag/wallabag)

## 94. Shiori
- **What**: Simple bookmark manager with REST API, CLI
- **Stars**: ~9,000+
- **RAM**: 128 MB
- **Docker**: Yes

---

# CATEGORY 15: TTS / STT / TRANSLATION

## 95. Piper TTS
- **What**: Fast local text-to-speech, many voices
- **Stars**: ~7,000+
- **RAM**: 256 MB
- **Docker**: Can be wrapped as HTTP API

## 96. Whisper.cpp / Faster-Whisper
- **What**: Local speech-to-text (OpenAI Whisper), CPU-friendly
- **Stars**: ~37,000+ / ~14,000+
- **RAM**: 1-4 GB
- **Replaces**: OpenAI Whisper API ($0.006/min)

## 97. LibreTranslate ★★
- **What**: Self-hosted machine translation, full REST API
- **Stars**: ~9,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (libretranslate/libretranslate)
- **Replaces**: Google Translate API, DeepL API

## 98. Lingva Translate
- **What**: Alternative frontend for Google Translate with API
- **RAM**: 256 MB
- **Docker**: Yes

---

# CATEGORY 16: ANALYTICS & MONITORING

## 99. Plausible
- **What**: Privacy-friendly web analytics, REST API
- **Stars**: ~20,000+
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes

## 100. Umami (already deployed)
- **What**: Simple fast web analytics
- **Stars**: ~23,000+
- **RAM**: 256 MB
- **Docker**: Yes

## 101. Healthchecks.io
- **What**: Cron job / scheduled task monitoring
- **Stars**: ~8,000+
- **RAM**: 256 MB
- **Docker**: Yes
- **Agent Value**: Monitor all agent cron jobs, alert on failure

## 102. Gatus
- **What**: Automated health dashboard, config-driven
- **Stars**: ~6,000+
- **RAM**: 128 MB
- **Docker**: Yes

## 103. Langfuse ★★
- **What**: Open-source LLM engineering platform, traces, evals, prompts
- **Stars**: ~7,000+
- **RAM**: 1-2 GB
- **Docker**: Yes (langfuse/langfuse)
- **Replaces**: LangSmith ($20+/mo), Helicone
- **Agent Value**: Track all LLM calls, costs, performance across agents

## 104. Phoenix (Arize)
- **What**: AI observability and evaluation, OpenTelemetry-native
- **RAM**: 1-2 GB
- **Docker**: Yes

---

# CATEGORY 17: VPN / TUNNELING / NETWORKING

## 105. Headscale
- **What**: Self-hosted Tailscale control server
- **Stars**: ~23,000+
- **RAM**: 256 MB
- **Docker**: Yes

## 106. Netbird
- **What**: WireGuard-based mesh VPN with SSO
- **Stars**: ~11,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 107. wg-easy
- **What**: Simple WireGuard VPN management with web UI
- **Stars**: ~16,000+
- **RAM**: 128 MB
- **Docker**: Yes

## 108. FRP
- **What**: Fast Reverse Proxy, expose local servers behind NAT
- **Stars**: ~87,000+
- **RAM**: 64 MB
- **Docker**: Yes

## 109. Rathole
- **What**: Lightweight reverse proxy for NAT traversal
- **Stars**: ~10,000+
- **RAM**: 32 MB

---

# CATEGORY 18: SECRETS & AUTHENTICATION

## 110. Infisical
- **What**: Open-source secrets management, REST API, CLI
- **Stars**: ~16,000+
- **RAM**: 512 MB
- **Docker**: Yes

## 111. Vault (HashiCorp)
- **What**: Industry-standard secrets management
- **RAM**: 512 MB - 1 GB
- **Docker**: Yes (hashicorp/vault)

## 112. Authelia
- **What**: SSO and 2FA portal, reverse proxy companion
- **Stars**: ~22,000+
- **RAM**: 128 MB
- **Docker**: Yes (authelia/authelia)

## 113. Authentik
- **What**: Identity provider (SAML, OAuth2, OIDC, LDAP)
- **Stars**: ~14,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

---

# CATEGORY 19: STORAGE & BACKUP

## 114. MinIO
- **What**: S3-compatible object storage
- **Stars**: ~48,000+
- **RAM**: 1-4 GB
- **Docker**: Yes (minio/minio)
- **Agent Value**: Store artifacts, models, datasets with S3 API

## 115. SeaweedFS
- **What**: Fast distributed storage, S3-compatible
- **Stars**: ~23,000+
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes

## 116. Restic
- **What**: Fast encrypted backup, supports S3/SFTP
- **Stars**: ~27,000+
- **RAM**: 256 MB

## 117. BorgBackup
- **What**: Deduplicating backup with encryption
- **Stars**: ~11,000+
- **RAM**: 256 MB

## 118. Duplicati
- **What**: Backup with web UI and REST API
- **RAM**: 512 MB
- **Docker**: Yes

---

# CATEGORY 20: AI CODING ASSISTANTS

## 119. Tabby
- **What**: Self-hosted AI coding assistant, code completion + chat
- **Stars**: ~22,000+
- **RAM**: 4-8 GB VRAM (GPU), CPU available
- **Docker**: Yes (tabbyml/tabby)
- **Agent Value**: Free Copilot alternative for all your devs

## 120. Continue
- **What**: Open-source AI code assistant IDE extension
- **Stars**: ~20,000+
- **RAM**: Minimal (connects to LLM backend)

## 121. LibreChat
- **What**: Enhanced ChatGPT clone, multi-provider, plugins, RAG
- **Stars**: ~20,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

---

# CATEGORY 21: ML OPERATIONS & OBSERVABILITY

## 122. MLflow
- **What**: ML lifecycle platform (experiments, model registry, serving)
- **Stars**: ~18,000+
- **RAM**: 1-4 GB
- **Docker**: Yes

## 123. Label Studio
- **What**: Data labeling and annotation (text, image, audio, video)
- **Stars**: ~19,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

## 124. Grafana (already deployed)
- **What**: Visualization and dashboarding
- **RAM**: 256 MB - 1 GB
- **Docker**: Yes

## 125. Prometheus (already deployed)
- **What**: Metrics collection and alerting
- **RAM**: 512 MB - 2 GB
- **Docker**: Yes

---

# CATEGORY 22: MEDIA & IMAGE TOOLS

## 126. Immich
- **What**: Self-hosted photo/video management (Google Photos alternative)
- **Stars**: ~55,000+
- **RAM**: 2-4 GB
- **Docker**: Yes

## 127. Excalidraw
- **What**: Collaborative whiteboard/diagramming
- **Stars**: ~90,000+
- **RAM**: 256 MB
- **Docker**: Yes

## 128. ImageMagick API
- **What**: Image manipulation via REST API wrapper
- **RAM**: 256 MB

---

# CATEGORY 23: DNS & AD BLOCKING

## 129. Pi-hole
- **What**: DNS sinkhole / ad blocker with REST API
- **Stars**: ~49,000+
- **RAM**: 256 MB
- **Docker**: Yes (pihole/pihole)

## 130. AdGuard Home
- **What**: DNS-based ad blocker with REST API
- **Stars**: ~26,000+
- **RAM**: 256 MB
- **Docker**: Yes

## 131. CoreDNS
- **What**: Flexible plugin-based DNS server
- **RAM**: 128 MB
- **Docker**: Yes

---

# CATEGORY 24: API GATEWAYS

## 132. Traefik (already deployed)
- **What**: Cloud-native reverse proxy / API gateway
- **RAM**: 128 MB
- **Docker**: Yes

## 133. Kong Gateway
- **What**: API gateway with plugin ecosystem
- **Stars**: ~39,000+
- **RAM**: 1-2 GB
- **Docker**: Yes

## 134. APISIX
- **What**: High-performance API gateway
- **Stars**: ~14,000+
- **RAM**: 512 MB
- **Docker**: Yes

---

# CATEGORY 25: MCP SERVERS (Model Context Protocol)

These let AI agents interact with self-hosted tools:

| # | MCP Server | Connects To | Notes |
|---|------------|-------------|-------|
| 135 | searxng-mcp | SearXNG | Web search |
| 136 | firecrawl-mcp | Firecrawl | Web scraping |
| 137 | browserless-mcp | Browserless | Browser automation |
| 138 | playwright-mcp | Playwright | Official Microsoft |
| 139 | puppeteer-mcp | Puppeteer | Browser control |
| 140 | docling-mcp | Docling | Document parsing |
| 141 | tika-mcp | Apache Tika | File extraction |
| 142 | unstructured-mcp | Unstructured | Document ETL |
| 143 | meilisearch-mcp | Meilisearch | Search index |
| 144 | jina-reader-mcp | Jina Reader | URL to text |
| 145 | qdrant-mcp | Qdrant | Vector search |
| 146 | postgres-mcp | PostgreSQL | Database access |
| 147 | redis-mcp | Redis | Cache/state |
| 148 | filesystem-mcp | Local files | File read/write |
| 149 | fetch-mcp | URLs | HTTP fetching |
| 150 | git-mcp | Git repos | Repository operations |

---

# DEPLOYMENT PLAN FOR OUR VPS

## Phase 1: Replace Paid Services (Day 1)
RAM: ~3 GB new
```
SearXNG (256 MB)      → Replace Tavily for web search
Browserless (1.5 GB)  → Headless Chrome for agents
ntfy (64 MB)          → Agent notifications
Piston (1 GB)         → Code execution sandbox
```

## Phase 2: Enhanced Agent Capabilities (Week 1)
RAM: ~4 GB new
```
Firecrawl (1.5 GB)         → Deep web scraping
Gotenberg (512 MB)         → Document conversion
Stirling PDF (512 MB)      → PDF manipulation
Changedetection.io (256 MB) → Web monitoring
Miniflux (128 MB)          → RSS feed monitoring
LibreTranslate (1 GB)      → Translation API
```

## Phase 3: Full Autonomous Infrastructure (Week 2)
RAM: ~4 GB new
```
Langfuse (1 GB)       → LLM observability
Meilisearch (512 MB)  → Full-text search
Dify (2 GB)           → Visual AI workflows
Healthchecks (256 MB) → Cron monitoring
```

## Phase 4: Development Platform (Month 1)
```
Gitea (512 MB)        → Self-hosted Git
Woodpecker CI (512 MB)→ CI/CD pipelines
code-server (1 GB)    → Remote IDE
pgvector extension    → Vector search in existing PG
```

---

## TOTAL RESOURCE BUDGET

| Phase | New RAM | Cumulative | VPS Free After |
|-------|---------|------------|----------------|
| Current | 0 | 5.3 GB used | 26 GB free |
| Phase 1 | ~3 GB | ~8 GB | 23 GB free |
| Phase 2 | ~4 GB | ~12 GB | 19 GB free |
| Phase 3 | ~4 GB | ~16 GB | 15 GB free |
| Phase 4 | ~2.5 GB | ~18.5 GB | 12.5 GB free |

**Even with EVERYTHING deployed, we'd still have 12+ GB RAM free on the VPS.**

---

## ESTIMATED MONTHLY SAVINGS

| SaaS Replaced | Monthly Cost | Self-hosted Alternative |
|---------------|-------------|------------------------|
| Tavily | $20 | SearXNG |
| Firecrawl SaaS | $19-399 | Firecrawl self-hosted |
| Browserless Cloud | $200+ | Browserless Docker |
| E2B/Code Exec | $10-50 | Piston |
| CloudConvert | $8 | Gotenberg |
| Adobe Acrobat | $20 | Stirling PDF |
| Algolia | $50+ | Meilisearch |
| LangSmith | $20+ | Langfuse |
| Visualping | $10 | Changedetection.io |
| Google Translate API | $20/mo est | LibreTranslate |
| Feedly Pro | $8 | Miniflux |
| Push notifications | $10 | ntfy |
| **TOTAL** | **$395-815/mo** | **$0 (VPS already paid)** |
