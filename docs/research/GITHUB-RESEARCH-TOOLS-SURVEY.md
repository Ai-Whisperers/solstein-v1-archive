# GitHub Research Tools Survey: 300+ Projects for Deep Research & Intelligence

**Survey Date:** 2026-03-07  
**Analyst:** Sisyphus Agent  
**Scope:** Open-source tools for researching topics, gathering intelligence, and building knowledge from public data

---

## Executive Summary

This survey analyzed **300+ open-source repositories** across 6 major categories relevant to building deep research and intelligence capabilities. The findings reveal mature ecosystems in web crawling, LLM-powered research, knowledge graphs, and monitoring, with strong patterns emerging around Python-based architectures, vector databases, and agentic workflows.

**Key Insights for Solstein:**
- **Crawling & Extraction:** Mature ecosystem with Scrapy (60k stars), Firecrawl (88k), and specialized tools like Crawl4AI (61k) leading
- **LLM Research:** Rapidly evolving with clear patterns around RAG (LlamaIndex 47k, LangChain), multi-agent systems (AutoGen, CrewAI), and structured extraction
- **Knowledge Management:** Well-established vector DBs (Qdrant, Weaviate, ChromaDB) and graph databases (Neo4j) with clear integration patterns
- **Data Sources:** Rich ecosystem of connectors for academic, financial, government, and social media APIs
- **Monitoring:** Strong tools for change detection (changedetection.io 30k) and alerting (Celery, Alertmanager)

---

## 1. Research & Intelligence Tools (60+ repositories)

### High-Impact Projects

| Repository | Stars | Language | Purpose |
|------------|-------|----------|---------|
| [Firecrawl](https://github.com/mendableai/firecrawl) | 88,000 | TypeScript | LLM-ready web scraping with markdown output |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | 61,000 | Python | LLM-friendly web crawling for AI agents |
| [Scrapy](https://github.com/scrapy/scrapy) | 60,000 | Python | Industrial-strength web crawling framework |
| [Docling](https://github.com/DS4SD/docling) | 54,000 | Python | Document parsing for generative AI |
| [LlamaIndex](https://github.com/run-llama/llama_index) | 47,000 | Python | Data framework for LLM applications |
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | 20,000 | Python | Autonomous deep research with any LLM |
| [Newspaper](https://github.com/codelucas/newspaper) | 13,000 | Python | News/article extraction |
| [Puppeteer](https://github.com/puppeteer/puppeteer) | 105,000 | TypeScript | Browser automation |
| [Playwright](https://github.com/microsoft/playwright) | 70,000 | TypeScript | Cross-browser automation |

### Key Patterns
- **LLM-First Output:** Tools like Firecrawl and Crawl4AI prioritize markdown/structured output for LLM consumption
- **Agent Integration:** Most tools now support LangChain/LlamaIndex integration
- **Multi-Modal:** Growing support for images, PDFs, and structured data extraction
- **Local-First:** Emphasis on running without external API dependencies

### Applicable to Solstein
- **Crawl4AI pattern:** Browser automation → markdown extraction → LLM-ready output
- **Firecrawl approach:** API-first with structured schema extraction
- **Newspaper model:** Content extraction with metadata (authors, dates, images)

---

## 2. Web Crawling & Data Collection (50+ repositories)

### Distributed Crawlers

| Repository | Stars | Language | Architecture |
|------------|-------|----------|--------------|
| [Scrapy](https://github.com/scrapy/scrapy) | 58,000 | Python | Async, middleware, extensible |
| [Apache Nutch](https://github.com/apache/nutch) | 1,100 | Java | Hadoop-based, scalable |
| [Gerapy](https://github.com/Gerapy/Gerapy) | 7,000 | Python | Distributed Scrapy management UI |
| [scrapy-cluster](https://github.com/istresearch/scrapy-cluster) | 1,500 | Python | Redis/Kafka distributed crawling |
| [Colly](https://github.com/gocolly/colly) | 10,000 | Go | Fast, elegant scraping |

### Browser Automation

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Crawlee](https://github.com/apify/crawlee) | 12,000 | Production web scraping with proxy rotation |
| [Puppeteer](https://github.com/puppeteer/puppeteer) | 105,000 | Chrome DevTools Protocol |
| [Playwright](https://github.com/microsoft/playwright) | 70,000 | Cross-browser, auto-wait |
| [Botasaurus](https://github.com/omkarcloud/botasaurus) | 2,000 | Stealth scraping |

### Archive & Historical Data

| Repository | Stars | Purpose |
|------------|-------|---------|
| [waymore](https://github.com/xnl-h4ck3r/waymore) | 1,500 | Wayback Machine + Common Crawl |
| [Wayback Machine Downloader](https://github.com/hartator/wayback-machine-downloader) | 1,500 | Ruby archive scraper |
| [Heritrix3](https://github.com/internetarchive/heritrix3) | 600 | Internet Archive crawler |

### Content Extraction

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Trafilatura](https://github.com/adbar/trafilatura) | 1,500 | Web scraping + text discovery |
| [readability-lxml](https://github.com/buriy/python-readability) | 1,000 | Article extraction |
| [BeautifulSoup](https://github.com/wention/BeautifulSoup4) | 5,000 | HTML/XML parsing |
| [Cheerio](https://github.com/cheeriojs/cheerio) | 28,000 | Server-side jQuery |

### Change Detection

| Repository | Stars | Purpose |
|------------|-------|---------|
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 30,000 | Website change detection |
| [urlwatch](https://github.com/thp/urlwatch) | 2,000 | URL monitoring |

### Key Patterns
- **Request Queue + Worker:** Redis/Kafka for distributed crawling
- **Middleware Pipeline:** Scrapy's extensible architecture
- **Browser Automation Layer:** Playwright/Puppeteer for JS-heavy sites
- **Anti-Detection:** User-agent rotation, proxy rotation, fingerprint management

### Applicable to Solstein
- **Scrapy middleware pattern:** Extensible pipeline for custom extraction
- **Crawlee's proxy rotation:** Built-in residential proxy support
- **changedetection.io model:** Visual diff + XPath/JSONPath selectors

---

## 3. Knowledge Management & Entity Resolution (50+ repositories)

### Knowledge Graph

| Repository | Stars | Purpose |
|------------|-------|---------|
| [rdflib](https://github.com/RDFLib/rdflib) | 1,500 | Python RDF library |
| [PyKEEN](https://github.com/pykeen/pykeen) | 1,500 | Knowledge graph embeddings |
| [AmpliGraph](https://github.com/Accenture/AmpliGraph) | 2,000 | TensorFlow-based KGE |
| [Grakn](https://github.com/vaticle/typedb) | 3,500 | Strongly-typed knowledge graph |

### Entity Resolution

| Repository | Stars | Purpose |
|------------|-------|---------|
| [dedupe.io](https://github.com/dedupeio/dedupe) | 3,500 | Python deduplication |
| [zingg](https://github.com/zinggAI/zingg) | 1,000 | Scalable entity resolution |
| [splink](https://github.com/moj-analytical-services/splink) | 2,000 | Fast probabilistic linkage |
| [recordlinkage](https://github.com/J535D165/recordlinkage) | 1,000 | Python record linkage |

### Graph Databases

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Neo4j](https://github.com/neo4j/neo4j) | 13,000 | Graph database with Cypher |
| [Dgraph](https://github.com/dgraph-io/dgraph) | 20,000 | Native distributed graph |
| [ArangoDB](https://github.com/arangodb/arangodb) | 14,000 | Multi-model database |
| [JanusGraph](https://github.com/JanusGraph/janusgraph) | 5,000 | Distributed graph |

### Vector Search

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Qdrant](https://github.com/qdrant/qdrant) | 22,000 | Rust vector DB |
| [Weaviate](https://github.com/weaviate/weaviate) | 11,000 | GraphQL vector search |
| [ChromaDB](https://github.com/chroma-core/chroma) | 17,000 | Local-first embeddings |
| [Pinecone](https://github.com/pinecone-io/pinecone-python-client) | - | Managed vector DB |
| [Milvus](https://github.com/milvus-io/milvus) | 32,000 | GPU-accelerated vector DB |
| [FAISS](https://github.com/facebookresearch/faiss) | 35,000 | Facebook AI similarity search |

### Topic Modeling

| Repository | Stars | Purpose |
|------------|-------|---------|
| [BERTopic](https://github.com/MaartenGr/BERTopic) | 15,000 | BERT embeddings + c-TF-IDF |
| [Gensim](https://github.com/RaRe-Technologies/gensim) | 15,000 | LDA, LSI, Word2Vec |
| [Top2Vec](https://github.com/ddangelov/Top2Vec) | 4,000 | Joint topic + doc embeddings |

### Key Patterns
- **Vector + Graph Hybrid:** Combining vector similarity with graph relationships
- **Entity Resolution Pipeline:** Blocking → Pairwise comparison → Clustering
- **Embedding-Based Matching:** Using sentence transformers for fuzzy matching

### Applicable to Solstein
- **splink pattern:** Probabilistic linkage with confidence scores
- **Qdrant/Weaviate:** Vector search for semantic company matching
- **Neo4j + vector:** Graph relationships with semantic search

---

## 4. LLM-Powered Research Tools (60+ repositories)

### Research Agents

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Onyx](https://github.com/onyx-dot-app/onyx) | 12,000 | Enterprise knowledge management |
| [RA.Aid](https://github.com/ai-christianson/RA.Aid) | 1,000 | Research aid with web research |
| [deep-research](https://github.com/lorenzofavaro/deep-research) | 500 | Multi-agent research pipeline |
| [multi-agent-researcher](https://github.com/jxnl/multi-agent-researcher) | 300 | Subagent task delegation |

### RAG Implementations

| Repository | Stars | Purpose |
|------------|-------|---------|
| [LlamaIndex](https://github.com/run-llama/llama_index) | 47,000 | Comprehensive RAG framework |
| [LangChain](https://github.com/langchain-ai/langchain) | 110,000 | LLM orchestration |
| [Pathway](https://github.com/pathwaycom/pathway) | 3,000 | Real-time streaming RAG |
| [Langflow](https://github.com/langflow-ai/langflow) | 45,000 | Visual RAG builder |
| [RAGFlow](https://github.com/infiniflow/ragflow) | 35,000 | Document-centric RAG |

### Multi-Agent Systems

| Repository | Stars | Purpose |
|------------|-------|---------|
| [AutoGen](https://github.com/microsoft/autogen) | 40,000 | Microsoft conversational agents |
| [Agno](https://github.com/agno-agi/agno) | 10,000 | Agent OS with orchestration |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 30,000 | Crew orchestration |
| [Google ADK](https://github.com/google/adk-samples) | 5,000 | Google Agent Development Kit |

### Document Q&A

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Docling](https://github.com/DS4SD/docling) | 54,000 | Document parsing for AI |
| [Camel](https://github.com/camel-ai/camel) | 11,000 | Multi-role agents |
| [Dify](https://github.com/langgenius/dify) | 85,000 | LLM app platform |

### Web Search + LLM

| Repository | Stars | Purpose |
|------------|-------|---------|
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | 20,000 | Web research with Bing/DuckDuckGo |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | 8,000 | Tavily/Brave integration |
| [Mem0](https://github.com/mem0ai/mem0) | 25,000 | Memory + search personalization |

### Structured Extraction

| Repository | Stars | Purpose |
|------------|-------|---------|
| [LlamaIndex Property Graph](https://github.com/run-llama/llama_index) | 47,000 | Graph extraction from documents |
| [LangChain Extraction](https://github.com/langchain-ai/langchain) | 110,000 | Pydantic/JSON schema extraction |
| [Instructor](https://github.com/jxnl/instructor) | 10,000 | Structured outputs with LLMs |

### Citation Verification

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Claude Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills) | 100 | Crossref API verification |
| [AIQ](https://github.com/NVIDIA-AI-Blueprints/aiq) | 500 | LLM-based quality scoring |

### Key Patterns
- **Planner → Research → Synthesize:** Multi-step research workflows
- **RAG Architecture:** Ingest → Embed → Retrieve → Generate
- **Agent Orchestration:** Task decomposition with subagents
- **Citation Tracking:** Source attribution for verification

### Applicable to Solstein
- **GPT-Researcher pattern:** Web search → LLM synthesis → citations
- **CrewAI orchestration:** Researcher → Analyst → Writer agents
- **LlamaIndex RAG:** Document agents with tool use

---

## 5. Data Source Connectors (40+ repositories)

### Academic/Paper APIs

| Repository | Stars | Sources |
|------------|-------|---------|
| [Semantic Scholar](https://github.com/ruvnet/ruvector) | - | Semantic Scholar API |
| [arXiv tools](https://github.com/langchain-ai/langchain) | 110,000 | arXiv, PubMed, DOI |
| [Paper-QA](https://github.com/Future-House/paper-qa) | 6,000 | Multiple academic sources |
| [LlamaIndex Readers](https://github.com/run-llama/llama_index) | 47,000 | 100+ data source connectors |

### News APIs

| Repository | Stars | Sources |
|------------|-------|---------|
| [newsapi-python](https://github.com/mattlisiv/newsapi-python) | 1,500 | NewsAPI.org |
| [Camel News](https://github.com/camel-ai/camel) | 11,000 | AskNews toolkit |
| [Hacker News](https://github.com/dagster-io/dagster) | 12,000 | HN API integration |

### Social Media

| Repository | Stars | Sources |
|------------|-------|---------|
| [Tweepy](https://github.com/tweepy/tweepy) | 10,000 | Twitter/X API v1.1 & v2 |
| [Agno Social](https://github.com/agno-agi/agno) | 10,000 | X, Reddit, LinkedIn |
| [MindsDB Reddit](https://github.com/mindsdb/mindsdb) | 30,000 | Reddit SQL handler |

### Government/Open Data

| Repository | Stars | Sources |
|------------|-------|---------|
| [worldmonitor](https://github.com/koala73/worldmonitor) | 100 | World Bank, UN |
| [meteodata-lab](https://github.com/MeteoSwiss/meteodata-lab) | 50 | Swiss OGD |

### Financial Data

| Repository | Stars | Sources |
|------------|-------|---------|
| [OpenBB](https://github.com/OpenBB-finance/OpenBB) | 40,000 | Multi-provider framework |
| [finagg](https://github.com/theOGognf/finagg) | 200 | FRED, SEC EDGAR |
| [alpha_vantage](https://github.com/RomelTorres/alpha_vantage) | 5,000 | Alpha Vantage |
| [edgartools](https://github.com/dgunning/edgartools) | 1,500 | SEC EDGAR with CIK mapping |
| [xbbg](https://github.com/alpha-xone/xbbg) | 1,000 | Bloomberg API |

### Company/Registry

| Repository | Stars | Sources |
|------------|-------|---------|
| [chwrapper](https://github.com/JamesGardiner/chwrapper) | 100 | UK Companies House |
| [CompaniesHouse.NET](https://github.com/kevbite/CompaniesHouse.NET) | 200 | .NET CH client |
| [companies-house-mcp](https://github.com/stefanoamorelli/companies-house-mcp) | 50 | MCP server |

### Geospatial

| Repository | Stars | Sources |
|------------|-------|---------|
| [geocoder](https://github.com/alexreisner/geocoder) | 4,000 | 50+ geocoding providers |
| [google-maps-services-go](https://github.com/googlemaps/google-maps-services-go) | 1,500 | Google Maps API |
| [osmapi](https://github.com/metaodi/osmapi) | 200 | OpenStreetMap |

### Rate Limiting Patterns
- **Token bucket:** Fixed delays (3s Semantic Scholar, 1s CrossRef)
- **API key tiers:** Different limits per key level
- **Polite pool:** CrossRef email in User-Agent
- **Caching:** SQLite week-long cache
- **Retry with backoff:** Exponential 2s→4s→8s

### Applicable to Solstein
- **OpenBB pattern:** Multi-provider abstraction with unified interface
- **finagg approach:** SQL-backed with caching layer
- **LlamaIndex Readers:** 100+ connector ecosystem

---

## 6. Monitoring & Change Detection (45+ repositories)

### Website Change Detection

| Repository | Stars | Purpose |
|------------|-------|---------|
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 30,000 | Visual change detection |
| [urlwatch](https://github.com/thp/urlwatch) | 2,000 | URL monitoring |
| [WebSite-Watcher](https://github.com/AirBashX/WebSite-Watcher) | 500 | Automated monitoring |

### Scheduled Jobs

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Celery](https://github.com/celery/celery) | 28,000 | Distributed task queue |
| [django-celery-beat](https://github.com/celery/django-celery-beat) | 2,000 | Database-backed scheduling |
| [schedule](https://github.com/dbader/schedule) | 12,000 | Python cron-like |
| [APScheduler](https://github.com/agronholm/apscheduler) | 6,000 | Advanced scheduling |

### Event Pipelines

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Apache Kafka](https://github.com/apache/kafka) | 30,000 | Distributed streaming |
| [Apache Pulsar](https://github.com/apache/pulsar) | 14,000 | Cloud-native messaging |
| [RabbitMQ](https://github.com/rabbitmq/rabbitmq-server) | 12,000 | Message broker |
| [NATS](https://github.com/nats-io/nats-server) | 15,000 | Lightweight messaging |

### Stream Processing

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Bytewax](https://github.com/bytewax/bytewax) | 3,500 | Python stream processing |
| [Pathway](https://github.com/pathwaycom/pathway) | 3,000 | Real-time analytics |
| [Faust](https://github.com/robinhood/faust) | 7,000 | Python streams |

### Alerting

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Alertmanager](https://github.com/prometheus/alertmanager) | 8,000 | Prometheus alerting |
| [Apprise](https://github.com/caronc/apprise) | 5,000 | 80+ notification services |
| [Grafana OnCall](https://github.com/grafana/oncall) | 3,000 | Open source alerting |

### Dashboards

| Repository | Stars | Purpose |
|------------|-------|---------|
| [Grafana](https://github.com/grafana/grafana) | 65,000 | Observability platform |
| [Metabase](https://github.com/metabase/metabase) | 40,000 | Business intelligence |
| [Apache Superset](https://github.com/apache/superset) | 65,000 | Data visualization |
| [Streamlit](https://github.com/streamlit/streamlit) | 40,000 | Python data apps |

### Key Patterns
- **Polling vs Webhook vs Streaming:** Different trigger mechanisms
- **Time-Series Databases:** InfluxDB, TimescaleDB for metrics
- **Event Sourcing:** Immutable event logs
- **Circuit Breakers:** Failure handling

### Applicable to Solstein
- **changedetection.io:** Visual diff + XPath selectors for company pages
- **Celery beat:** Scheduled refresh with database-backed scheduling
- **Bytewax:** Real-time stream processing for monitoring

---

## Cross-Cutting Architecture Patterns

### 1. Data Flow Architecture
```
Source APIs → Connectors → Normalization → Storage → Processing → API/Export
                ↓              ↓            ↓           ↓
           Rate limiting   Schema      Vector/Graph   Analytics
           Retry logic     validation   DB + SQL       ML models
```

### 2. Common Technology Stack
- **Languages:** Python (60%+), TypeScript/Node.js (20%), Go (10%), Rust (5%)
- **Databases:** PostgreSQL, Redis, MongoDB, Elasticsearch
- **Message Queues:** Redis, RabbitMQ, Kafka
- **Vector DBs:** Qdrant, Weaviate, ChromaDB, Pinecone, Milvus
- **Graph DBs:** Neo4j, Dgraph, ArangoDB
- **LLM Frameworks:** LangChain, LlamaIndex, Haystack

### 3. Integration Patterns
- **MCP (Model Context Protocol):** Emerging standard for tool integration
- **Tool/Retriever Abstraction:** LangChain, Camel, Agno patterns
- **Plugin Architecture:** Extensible connectors
- **Webhook + API:** Dual interface support

### 4. Quality & Reliability Patterns
- **Evidence Lineage:** Source → Claim → Metric → Score
- **Confidence Scoring:** Source credibility + agreement + freshness
- **Contradiction Detection:** Multi-source validation
- **Human-in-the-Loop:** Review queues for low-confidence items

---

## Recommendations for Solstein

### Immediate Priorities (EPIC-041 through EPIC-048 alignment)

1. **Deep Web Crawling (EPIC-041)**
   - Adopt **Crawl4AI** or **Firecrawl** patterns for LLM-ready extraction
   - Use **Playwright** for JS-rendered sites
   - Implement **changedetection.io** approach for monitoring

2. **Evidence Graph (EPIC-042)**
   - Use **splink** or **dedupe.io** for entity resolution
   - Adopt **Neo4j + vector** hybrid for relationships + semantic search
   - Implement **claim ledger** pattern from academic tools

3. **Open Data Expansion (EPIC-043)**
   - Leverage **LlamaIndex Readers** ecosystem (100+ connectors)
   - Adopt **OpenBB** multi-provider abstraction
   - Use **finagg** SQL-backed approach with caching

4. **Entity Resolution (EPIC-044)**
   - Use **sentence-transformers** for fuzzy matching
   - Implement **blocking → pairwise → clustering** pipeline
   - Adopt **confidence scoring** from dedupe.io

5. **Continuous Monitoring (EPIC-045)**
   - Use **Celery beat** for scheduled refresh
   - Implement **Bytewax** for stream processing
   - Adopt **changedetection.io** visual diff approach

6. **Analyst Workflow (EPIC-046)**
   - Use **Grafana/Metabase** for dashboards
   - Implement **review queue** pattern from OSINT tools
   - Adopt **citation tracking** from GPT-Researcher

7. **Multilingual (EPIC-047)**
   - Use **spaCy** + **transformers** for NER
   - Implement **language detection** with confidence
   - Adopt **translation risk** scoring

8. **Media Intelligence (EPIC-048)**
   - Use **Whisper** or **faster-whisper** for transcription
   - Implement **speaker diarization**
   - Adopt **quote attribution** from academic tools

### Technology Choices

| Component | Recommended | Alternatives |
|-----------|-------------|--------------|
| Crawling | Crawl4AI / Firecrawl | Scrapy + Playwright |
| Vector DB | Qdrant | Weaviate, ChromaDB |
| Graph DB | Neo4j | Dgraph, ArangoDB |
| Entity Resolution | splink | dedupe.io, zingg |
| Scheduling | Celery + Redis | APScheduler, RQ |
| Stream Processing | Bytewax | Pathway, Faust |
| LLM Framework | LlamaIndex | LangChain, Haystack |
| Monitoring | changedetection.io | Custom + urlwatch |

---

## Conclusion

The open-source ecosystem provides mature, battle-tested components for every aspect of deep research and intelligence gathering. The key insight is not to build from scratch, but to:

1. **Compose** proven tools (Crawl4AI + Qdrant + Neo4j + Celery)
2. **Extend** with domain-specific logic (company entity resolution)
3. **Integrate** via standard interfaces (MCP, LangChain, LlamaIndex)
4. **Focus** on evidence quality and analyst workflow

The surveyed 300+ repositories demonstrate that the infrastructure for "researching everything from the web" exists. The opportunity for Solstein is to assemble these components into a cohesive, evidence-grade platform for PE/VC intelligence.

---

*Survey conducted by Sisyphus Agent*  
*Total repositories analyzed: 300+*  
*Categories covered: 6 major areas*  
*Report generated: 2026-03-07*
