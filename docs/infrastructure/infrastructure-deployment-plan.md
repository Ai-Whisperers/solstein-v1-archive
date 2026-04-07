# Infrastructure Deployment Plan
## What goes where and why
### 2026-04-07

---

## MACHINE INVENTORY

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAPTOP (ai-whisperers-server)                                       │
│ HP Victus 15-fb0xxx                                                 │
│ ─────────────────────────────────────────                           │
│ CPU:  Ryzen 5 5600H (6C/6T - SMT off)                              │
│ RAM:  16 GB DDR4-3200 (5 GB free)                                   │
│ GPU:  RX 6500M 4GB (limited ROCm) + Vega iGPU                      │
│ Disk: 115 GB free on / │ 563 GB free on /data                      │
│ Net:  WiFi 6 (home LAN) + Tailscale                                │
│ Role: YOUR DAILY DRIVER - desktop, IDE, browser                     │
│ Uptime: Always on (used as server too)                              │
│ Constraint: RAM-limited, shared with desktop use                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ VPS (agentzero)                                                     │
│ Hostinger KVM                                                       │
│ ─────────────────────────────────────────                           │
│ CPU:  AMD EPYC 9354P (8 vCPUs)                                      │
│ RAM:  32 GB (26 GB free!)                                           │
│ GPU:  None                                                          │
│ Disk: 252 GB free                                                   │
│ Net:  1 Gbps public internet + Tailscale                            │
│ Role: PUBLIC-FACING SERVER - always on, always reachable            │
│ Uptime: 99.9% SLA                                                  │
│ Constraint: No GPU, CPU-only inference                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PC-ALE (desktop)                                                    │
│ Gigabyte B450 AORUS ELITE                                           │
│ ─────────────────────────────────────────                           │
│ CPU:  Ryzen 5 3600 (6C/12T)                                         │
│ RAM:  16 GB DDR4-2666 (8 GB free)                                   │
│ GPU:  RTX 2060 SUPER 8GB VRAM (CUDA 13.1)                          │
│ Disk: 236 GB free on C: │ 57 GB free on F:                         │
│ Net:  WiFi (home LAN) + Tailscale                                   │
│ Role: GPU WORKHORSE - local LLM inference, CUDA                    │
│ Uptime: Usually on, may sleep/reboot                                │
│ Constraint: Windows, not always guaranteed online                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DECISION PRINCIPLES

1. **VPS gets everything that must be always-on, public-facing, or used by remote agents**
2. **PC-ALE gets everything that needs GPU (CUDA/VRAM)**
3. **Laptop gets only what YOU interact with directly** - keep it light, it's already RAM-constrained
4. **Laptop's /data partition (563 GB) is wasted** - use it for storage/cache overflow
5. **Everything communicates over Tailscale** (encrypted mesh, no port forwarding)

---

## THE PLAN

### ═══════════════════════════════════════
### VPS (agentzero) — THE BRAIN
### ═══════════════════════════════════════

**Why here**: 26 GB RAM free, 8 vCPUs, always online, public IP, 99.9% uptime.
This is where autonomous agents live and work.

#### ALREADY RUNNING (keep):
| Service | RAM | Purpose |
|---------|-----|---------|
| Hermes Agent v0.7.0 | ~200 MB | Autonomous AI agent |
| LiteLLM | ~900 MB | Unified LLM gateway |
| Traefik | ~120 MB | Reverse proxy / TLS |
| PostgreSQL 14 | ~110 MB | Database |
| N8N | ~340 MB | Workflow automation |
| Qdrant | ~85 MB | Vector database |
| Grafana | ~230 MB | Dashboards |
| Prometheus | ~120 MB | Metrics |
| Uptime Kuma | ~175 MB | Status monitoring |
| Vaultwarden | ~55 MB | Password manager |
| Evolution API | ~280 MB | WhatsApp API |
| Redis | ~27 MB | Cache |
| Portainer | ~85 MB | Docker management |
| Websites (4) | ~620 MB | sunstein, vete, clinica, fun4me |
| Umami | ~210 MB | Analytics |
| **Total current** | **~3.6 GB** | |

#### PHASE 1 — DEPLOY NOW (Replace Paid Services):
| Service | RAM | Replaces | Saves |
|---------|-----|----------|-------|
| **SearXNG** | 256 MB | Tavily web search | $20/mo |
| **Browserless** | 1.5 GB | BrowserBase/Selenium cloud | $200+/mo |
| **Piston** | 1 GB | E2B code execution | $10-50/mo |
| **ntfy** | 64 MB | Push notification SaaS | $10/mo |
| **Gotenberg** | 512 MB | CloudConvert | $8/mo |
| **Phase 1 total** | **~3.3 GB** | | **~$248/mo** |

#### PHASE 2 — AGENT CAPABILITIES:
| Service | RAM | Purpose |
|---------|-----|---------|
| **Firecrawl** | 1.5 GB | Deep web scraping to markdown |
| **Stirling PDF** | 512 MB | PDF manipulation API |
| **Changedetection.io** | 256 MB | Monitor web page changes |
| **Miniflux** | 128 MB | RSS feed monitoring |
| **LibreTranslate** | 1 GB | Free translation API |
| **Langfuse** | 1 GB | LLM observability/tracing |
| **Meilisearch** | 512 MB | Full-text search engine |
| **Healthchecks.io** | 256 MB | Cron job monitoring |
| **Phase 2 total** | **~5.2 GB** | |

#### PHASE 3 — AUTONOMOUS DEVELOPMENT:
| Service | RAM | Purpose |
|---------|-----|---------|
| **Gitea** | 512 MB | Self-hosted Git (mirror all repos) |
| **Woodpecker CI** | 512 MB | CI/CD for auto-testing |
| **pgvector extension** | 0 MB | Vector search in existing PG (free!) |
| **Memos** | 128 MB | Agent scratchpad/notes |
| **Apprise** | 256 MB | Multi-channel notifications |
| **Phase 3 total** | **~1.4 GB** | |

#### PHASE 4 — ADVANCED (if needed):
| Service | RAM | Purpose |
|---------|-----|---------|
| Dify | 4 GB | Visual AI workflow builder |
| code-server | 1 GB | Remote VS Code |
| Outline | 1 GB | Knowledge base wiki |
| Label Studio | 1 GB | Data annotation |

#### VPS RESOURCE BUDGET:
```
Total RAM: 32 GB
├── Current services:     3.6 GB
├── Phase 1 (deploy now): 3.3 GB
├── Phase 2 (week 1):     5.2 GB
├── Phase 3 (week 2):     1.4 GB
├── Buffer/OS:            3.0 GB
└── STILL FREE:          15.5 GB  ← plenty of headroom

Total Disk: 387 GB
├── Current:            135 GB
├── New services:        ~20 GB (Docker images + data)
└── STILL FREE:         ~230 GB
```

### ═══════════════════════════════════════
### PC-ALE (Windows Desktop) — THE GPU
### ═══════════════════════════════════════

**Why here**: Only machine with CUDA GPU (RTX 2060 SUPER, 8 GB VRAM).
Dedicated to local LLM inference and GPU workloads.

#### KEEP RUNNING:
| Service | VRAM | RAM | Purpose |
|---------|------|-----|---------|
| **Ollama** | varies | 1-5 GB | LLM inference server |
| **Tailscale** | - | 64 MB | Mesh networking |

#### CURRENT MODELS (keep all):
| Model | Size | Use Case |
|-------|------|----------|
| gemma2:9b | 5.4 GB | General reasoning (best quality) |
| qwen2.5-coder:7b | 4.7 GB | Code generation/review |
| mistral:7b | 4.4 GB | Fast general tasks |
| llama3.1:8b | 4.9 GB | Versatile tasks |

#### ADD THESE MODELS:
| Model | Size | Use Case |
|-------|------|----------|
| **nomic-embed-text** | 274 MB | Embeddings (replace OpenAI embeddings API!) |
| **qwen2.5:14b** (Q4) | ~8 GB | Higher quality reasoning when VRAM allows |

#### ADD THESE SERVICES:
| Service | RAM | VRAM | Purpose |
|---------|-----|------|---------|
| **Faster-Whisper API** | 1 GB | 1-2 GB | Speech-to-text (replace OpenAI Whisper API) |

#### WHY NOT MORE ON PC-ALE:
- It's Windows, not ideal for server Docker stacks
- It may sleep/reboot (not 99.9% uptime)
- Limited to 16 GB RAM (8 GB free)
- Its job is singular: **GPU inference via Ollama**
- VPS agents call it over Tailscale when they need local LLM

#### PC-ALE RESOURCE BUDGET:
```
Total RAM: 16 GB
├── Windows + desktop:    8 GB
├── Ollama (idle):        1 GB (loads model on demand)
├── Ollama (active):      5-8 GB (one model at a time)
├── Faster-Whisper:       1 GB
└── STILL FREE:           6-9 GB (idle) / 0-3 GB (active)

GPU VRAM: 8 GB
├── Model loaded:         4-8 GB (one at a time)
├── Whisper:              1-2 GB (shared)
└── System/display:       ~0.5 GB
```

### ═══════════════════════════════════════
### LAPTOP (ai-whisperers-server) — THE COCKPIT
### ═══════════════════════════════════════

**Why minimal here**: Only 5 GB RAM free, it's your daily driver.
Don't add more services. Offload work to VPS.

#### KEEP RUNNING:
| Service | RAM | Purpose |
|---------|-----|---------|
| **Hermes Agent (CLI)** | ~200 MB | Your local AI assistant |
| **Docker containers** | ~2 GB | Keep only essentials below |
| **Chrome + IDE** | ~4 GB | Your daily work |

#### DOCKER CONTAINERS TO KEEP:
| Container | RAM | Why Keep |
|-----------|-----|----------|
| Home Assistant | ~190 MB | Smart home (local devices) |
| Traefik | ~120 MB | Local reverse proxy |
| Redis | ~27 MB | Hermes cache |

#### DOCKER CONTAINERS TO MOVE TO VPS:
| Container | RAM | Why Move |
|-----------|-----|----------|
| ~~N8N~~ | ~340 MB | Duplicate - already on VPS |
| ~~Grafana~~ | ~230 MB | Duplicate - already on VPS |
| ~~Prometheus~~ | ~120 MB | Duplicate - already on VPS |
| ~~Loki~~ | ~165 MB | Move log aggregation to VPS |
| ~~Promtail~~ | ~90 MB | Move with Loki |
| ~~Node Exporter~~ | ~40 MB | Keep lightweight agent, point to VPS Prometheus |

#### MOVE TO /data PARTITION (563 GB free!):
```
Move Docker data-root to /data/docker/
  → Frees ~30 GB from / partition
  → /data has 563 GB and is otherwise completely empty

Move ~/logs/ to /data/logs/ (symlink)
Move ~/.cache/ to /data/cache/ (symlink)
Move ~/Downloads/ to /data/downloads/ (symlink)
```

#### LAPTOP RESOURCE BUDGET AFTER CLEANUP:
```
Total RAM: 16 GB (14 GB usable)
├── Desktop + Browser:     4 GB
├── Hermes Agent:          0.2 GB
├── Home Assistant:        0.2 GB
├── Traefik + Redis:       0.15 GB
├── OS + buffers:          3 GB
└── ACTUALLY FREE:         6.5 GB  ← much better than 5 GB

Disk / (344 GB):
├── Before:              212 GB used (65%)
├── After moving Docker:  ~180 GB used (52%)
└── Free:                ~145 GB

Disk /data (593 GB):
├── Docker data:          ~30 GB
├── Logs + cache:         ~5 GB
└── Free:                ~558 GB
```

---

## NETWORK ARCHITECTURE

```
                    INTERNET
                       │
                       ▼
              ┌────────────────┐
              │     VPS        │
              │  Public IP     │
              │  Traefik :443  │◄─── HTTPS from world
              │                │
              │  ┌──────────┐  │
              │  │ Hermes   │  │  Autonomous agent
              │  │ Agent    │  │  (works 24/7)
              │  └────┬─────┘  │
              │       │        │
              │  ┌────┴─────┐  │
              │  │ LiteLLM  │──┼──► Cloud APIs (Anthropic, OpenAI, Groq)
              │  │ Gateway  │  │
              │  └────┬─────┘  │
              │       │        │        Tailscale mesh
              └───────┼────────┘        (encrypted)
                      │
         ┌────────────┼───────────────┐
         │            │               │
         ▼            ▼               ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  LAPTOP  │  │  PC-ALE  │  │ VPS svcs │
  │ Hermes   │  │  Ollama  │  │ SearXNG  │
  │ (local)  │  │  :11434  │  │ Browser  │
  │ Home Ast │  │ RTX 2060 │  │ Piston   │
  │          │  │ Whisper  │  │ Firecrawl│
  └──────────┘  └──────────┘  │ ntfy     │
                              │ n8n      │
                              │ Qdrant   │
                              │ Gitea    │
                              │ etc...   │
                              └──────────┘

  LLM ROUTING (via LiteLLM):
  ┌─────────────────────────────────────────────────┐
  │ Request Type        → Route           → Cost    │
  │ ──────────────────────────────────────────────── │
  │ Simple/routine      → pc-ale Ollama   → FREE    │
  │ Code generation     → pc-ale qwen2.5  → FREE    │
  │ Fast reasoning      → Groq free tier  → FREE    │
  │ Complex reasoning   → Claude/GPT-4    → $$$     │
  │ Embeddings          → pc-ale nomic    → FREE    │
  │ Speech-to-text      → pc-ale Whisper  → FREE    │
  │ Web search          → VPS SearXNG     → FREE    │
  │ Code execution      → VPS Piston      → FREE    │
  │ Web scraping        → VPS Firecrawl   → FREE    │
  └─────────────────────────────────────────────────┘
```

---

## WHAT DOES NOT GO ANYWHERE (and why)

| Tool | Reason to Skip |
|------|---------------|
| Dify | Hermes + n8n already covers workflow needs |
| Flowise/Langflow | Same - redundant with Hermes |
| Milvus | Overkill - Qdrant + pgvector is enough |
| Apache Airflow | n8n + Hermes cron handles this |
| Kong/APISIX | Traefik already deployed on both |
| Vault/Infisical | Vaultwarden already handles secrets |
| Keycloak/Authentik | Not needed for 1-2 user setup |
| Immich | Not relevant to AI agent work |
| Pi-hole/AdGuard | Nice but not agent infrastructure |
| Headscale | Already using Tailscale (hosted) |
| Open Interpreter | Hermes terminal tool does this |
| Selenium Grid | Browserless is simpler |
| Weaviate | Qdrant already deployed |
| MLflow | Premature - add when doing actual ML training |
| Stable Diffusion | No GPU on VPS, laptop GPU too weak |

---

## IMPLEMENTATION ORDER

### Day 1: VPS Phase 1 + Laptop Cleanup
1. Deploy SearXNG on VPS
2. Deploy Browserless on VPS
3. Deploy Piston on VPS
4. Deploy ntfy on VPS
5. Deploy Gotenberg on VPS
6. Remove duplicate n8n/grafana/prometheus from laptop
7. Move Docker data-root to laptop /data
8. Update LiteLLM to route through pc-ale Ollama

### Day 2-3: VPS Phase 2
9. Deploy Firecrawl on VPS
10. Deploy Stirling PDF on VPS
11. Deploy Changedetection.io on VPS
12. Deploy Miniflux on VPS
13. Deploy LibreTranslate on VPS
14. Deploy Langfuse on VPS
15. Deploy Meilisearch on VPS
16. Deploy Healthchecks.io on VPS

### Day 4-5: VPS Phase 3 + PC-ALE models
17. Deploy Gitea on VPS + mirror all repos
18. Deploy Woodpecker CI on VPS
19. Install pgvector on VPS PostgreSQL
20. Deploy Memos on VPS
21. Add nomic-embed-text model to pc-ale Ollama
22. Set up Faster-Whisper on pc-ale

### Day 6-7: Wire It All Together
23. Configure Hermes VPS to use all new tools
24. Set up MCP servers for SearXNG, Firecrawl, Browserless
25. Configure autonomous work cycles (Hermes cron)
26. Set up Langfuse tracing for all LLM calls
27. Test end-to-end: Hermes → search → scrape → analyze → code → commit
