> **Moved**: This guide has been consolidated into [`docs/guides/setup.md`](../guides/setup.md).
> **Security Note**: This file previously contained API key examples that have since been rotated.
> Please update your bookmarks.

# Solstein Project - Complete Setup Guide

> **Date**: 2026-03-01
> **Version**: 3.0
> **Last Updated**: 2026-03-01 00:50 UTC
> **Author**: Ivan Weiss van der Pol

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [OpenCode Setup](#opencode-setup)
3. [API Keys & Providers](#api-keys--providers)
4. [Configuration Files](#configuration-files)
5. [Current Provider Status](#current-provider-status)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## Quick Start

### Prerequisites

- Python 3.10+
- uv package manager (recommended) or pip
- Redis 6+ (required for cache and Celery task queue)
- PostgreSQL 14+ (optional, for data storage)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd solstein

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e .

# Setup database (optional)
export PYTHONPATH=src && python -c "import asyncio; from solstein.infrastructure.database import init_db; asyncio.run(init_db())"
```

### Environment Setup

Create a `.env` file in the project root with all API keys (see [API Keys section](#api-keys--providers) below).

---

## OpenCode Setup

### What is OpenCode?

OpenCode is an open-source AI coding agent that connects to 75+ LLM providers. This project is configured for OpenCode v1.0+ with granular permissions and multi-provider fallback.

### Configuration Files

The project includes these OpenCode configuration files:

| File | Purpose |
|------|---------|
| `.mcp.json` | MCP server configuration with granular permissions |
| `opencode.yml` | Comprehensive project configuration |
| `.opencode/settings.json` | Team-wide settings with hooks |
| `.opencode/agents/*.json` | Subagent definitions (build, plan, review, test, docs) |
| `AGENTS.md` | Project context for AI agents |

### Installing OpenCode

```bash
# Install OpenCode CLI
npm install -g @opencode-ai/cli

# Check version (must be >= 1.0.216 for security)
opencode --version

# Configure MCP servers
make mcp-check
```

### Available Subagents

| Agent | Purpose | Budget | Mode |
|-------|---------|--------|------|
| `@build` | Implementation & code changes | 500 | Read/Write |
| `@plan` | Architecture & research | 300 | Read-Only |
| `@review` | Code quality checks | 200 | Read-Only |
| `@test` | Test generation | 200 | Read/Write |
| `@docs` | Documentation | 150 | Read/Write |

### Slash Commands

```bash
/test          # Run test suite
/lint          # Run linting checks
/format        # Format all code
/typecheck     # Run type checking
/mcp-check     # Check MCP servers
/health        # Check LLM provider health
```

---

## API Keys & Providers

### 🔐 Master API Keystore

**⚠️ SECURITY WARNING**: These keys are sensitive. Never commit them to git. The `.env` file is already in `.gitignore`.

### Tier 1: Foundation Models (Direct)

| Provider | Environment Variable | Key | Status |
|----------|---------------------|-----|--------|
| **OpenAI** | `OPENAI_API_KEY` | `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` | ⚠️ Rate Limited (resets Mar 2) |
| **Anthropic** | `ANTHROPIC_API_KEY` | `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` | ✅ Working |
| **Gemini** | `GEMINI_API_KEY` | `AIzaSyCaIdRPNf3bgPyQ3FuVeWkFpn-zfEQIr-Y` | ✅ Working |
| **Mistral** | `MISTRAL_API_KEY` | `MTU4GM4kvuyey2iCmGJNsflvCfGpqYlB` | ✅ Working |
| **Kimi** | `KIMI_API_KEY` | `sk-ZtloAb4Vgcmq58TvfQBenNhl0wLUcKgNApN2hBs17JadnzYK` | ✅ Working |

### Tier 2: Ultra-Fast & Specialized Inference

| Provider | Environment Variable | Key | Status |
|----------|---------------------|-----|--------|
| **NVIDIA NIM** | `NVIDIA_NIM_API_KEY` | `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` | ✅ Working |
| **Groq** | `GROQ_API_KEY` | `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` | ✅ Working |
| **Cerebras** | `CEREBRAS_API_KEY` | `csk-j46xrkrr9ky9xddrndyvtjyhhn8m9kv4jtfpmx6x9yhhxdkj` | ✅ Working |
| **DeepInfra** | `DEEPINFRA_API_KEY` | `vfrzluVzjdDW5s0v64jFj08GNJvj3g8B` | ✅ Working |
| **Fireworks** | `FIREWORKS_API_KEY` | `fw_AcxApvcXwf2QFEiyygcWqB` | ✅ Working |
| **SiliconFlow** | `SILICONFLOW_API_KEY` | `sk-qpilmbtpduqfkuxvqrlypjvjztrdlhdslbeeqvbrufdlfqnf` | ❌ Invalid (401) |

### Tier 3: Cloud & Infrastructure

| Provider | Environment Variable | Key | Status |
|----------|---------------------|-----|--------|
| **Google Cloud** | `GOOGLE_CLOUD_API_KEY` | `AIzaSyAH2gbGmd6aEPaLs-3x8wVb7ZjIlOlKknE` | ✅ Working |
| **Alibaba** | `ALIBABA_API_KEY` | `sk-bd03e550028d4348b075619d581f9d19` | ✅ Working |
| **OCI OCID** | `OCI_OCID` | `ocid1.generativeaiapikey.oc1.sa-saopaulo-1.amaaaaaaopv77laakuodscno4fhrg6pcq3as4k5qh6ge3brzf5t4uurlzlgq` | ✅ Working |
| **OCI Key** | `OCI_KEY_ACTIVE` | `sk-rGyXLHcPX4Z2793yCGTocM7AkOXrw7RhOjbUSnQgP0eILUTp` | ✅ Working |

### Tier 4: Media, Research & Referrals

| Provider | Environment Variable | Key/Link |
|----------|---------------------|----------|
| **ElevenLabs** | `ELEVENLABS_API_KEY` | `78f758114b2a42427a3cfa8ed6b0dd33f65071ea4229cd873032efb24178b1ed` |
| **OpenCode** | `OPENCODE_API_KEY` | `sk-xqvmTEaSPryrs92QQ0XMDCQ0owkhGtgw5SDSOItekD4VVtTmiv62SHVTj8Nro5dX` |
| **GitHub** | `GITHUB_TOKEN` | `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` |

### Database & Infrastructure

```bash
# Database (PostgreSQL) - REQUIRED
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solstein

# Redis (Optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Supabase (Optional)
SUPABASE_URL=https://hzamrpxmzutfegnbvhqj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6YW1ycHhtenV0ZmVnbmJ2aHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4NjIxMDAsImV4cCI6MjA1NDQzODEwMH0.BAqxBcyjY4AwFS7zGK_hoI7_k2B3nczNnqHyuqVH2g4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6YW1ycHhtenV0ZmVnbmJ2aHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODg2MjEwMCwiZXhwIjoyMDU0NDM4MTAwaH.LSZbSfSNOPqLlWLSZHOVKYiY-UJY7v-zSCRmjiXkOW8
```

### Security Settings

```bash
# JWT Secret (generate a new one for production)
JWT_SECRET=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=30

# Other secrets
SECRET_KEY=your-secret-key-here
```

---

## Configuration Files

### `.env` Template

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/solstein
REDIS_URL=redis://localhost:6379/0

# AI Providers (add your keys)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
MISTRAL_API_KEY=
KIMI_API_KEY=
GROQ_API_KEY=
FIREWORKS_API_KEY=
DEEPINFRA_API_KEY=
NVIDIA_NIM_API_KEY=
CEREBRAS_API_KEY=

# LLM Configuration
LLM_PROVIDER=auto
OPENAI_MODEL=gpt-4o-mini
GROQ_MODEL=llama-3.3-70b-versatile
FIREWORKS_MODEL=accounts/fireworks/models/mixtral-8x22b-instruct
MISTRAL_MODEL=mistral-large-2411
DEEPINFRA_MODEL=meta-llama/Llama-3.3-70B-Instruct
GEMINI_MODEL=gemini-1.5-flash
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
CEREBRAS_MODEL=llama-3.3-70b
KIMI_MODEL=kimi-k2-32k

# Security
JWT_SECRET=your-secret-here
SECRET_KEY=your-secret-here

# Supabase (optional)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

### Model Configuration

The system supports these models per provider:

| Provider | Default Model | Available Models |
|----------|---------------|------------------|
| **OpenAI** | `gpt-4o-mini` | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| **Groq** | `llama-3.3-70b-versatile` | llama-3.3-70b, mixtral-8x7b |
| **Fireworks** | `accounts/fireworks/models/mixtral-8x22b-instruct` | mixtral-8x22b, qwen2-72b |
| **Mistral** | `mistral-large-2411` | mistral-large, pixtral-large, codestral |
| **DeepInfra** | `meta-llama/Llama-3.3-70B-Instruct` | Llama-3.3-70B, Llama-4-Scout |
| **Gemini** | `gemini-1.5-flash` | gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash |
| **NVIDIA** | `meta/llama-3.3-70b-instruct` | llama-3.3-70b, nemotron-4 |
| **Cerebras** | `llama-3.3-70b` | llama-3.3-70b |
| **Kimi** | `kimi-k2-32k` | kimi-k2.5, kimi-k2-turbo-preview, kimi-k2-thinking |
| **Ollama** | `llama3.2:latest` | Any local Ollama model |

---

## Current Provider Status

### Summary (as of 2026-03-01)

| Status | Count | Providers |
|--------|-------|-----------|
| ✅ Working | 9 | Ollama, Groq, Fireworks, Mistral, DeepInfra, Gemini, NVIDIA, Cerebras, Kimi |
| ⚠️ Limited | 1 | OpenAI (rate limited, resets Mar 2) |
| ❌ Failed | 1 | SiliconFlow (invalid key) |

### Detailed Status

| Provider | Status | Response Time | Cost (per 1K tokens) | Best For |
|----------|--------|---------------|---------------------|----------|
| **Ollama** | ✅ Healthy | ~100-500ms | Free (local) | Privacy, cost-sensitive |
| **Groq** | ✅ Healthy | ~50-100ms | $0.00059/$0.00079 | Speed |
| **Fireworks** | ✅ Healthy | ~100-200ms | $0.0009 | Cost-effective |
| **Mistral** | ✅ Healthy | ~100-300ms | Varies | EU data residency |
| **DeepInfra** | ✅ Healthy | ~100-300ms | Low | Latest Llama models |
| **Gemini** | ✅ Healthy | ~100-300ms | Low | Large context (1M) |
| **NVIDIA** | ✅ Healthy | ~50-150ms | Medium | GPU inference |
| **Cerebras** | ✅ Healthy | ~50-100ms | Medium | Specialized hardware |
| **Kimi** | ✅ Healthy | ~100-300ms | Low | Chinese/Asian market |
| **OpenAI** | ⚠️ Rate Limited | N/A | $0.00015/$0.0006 | High quality (when available) |

### Fallback Priority

```
1. Ollama → 2. Groq → 3. Fireworks → 4. SiliconFlow → 5. Alibaba → 6. Mistral → 7. DeepInfra
→ 8. Gemini → 9. NVIDIA → 10. Cerebras → 11. Kimi → 12. Anthropic → 13. OpenAI
```

### Rate Limits & Quotas

| Provider | RPM | TPM | Reset Period |
|----------|-----|-----|--------------|
| OpenAI | 60 | 60,000 | Mar 2, 2026 12:04 PM |
| Groq | 30 | 6,000 | Unknown |
| Fireworks | 60 | 60,000 | Unknown |
| Mistral | 60 | 60,000 | Unknown |
| DeepInfra | 60 | 60,000 | Unknown |
| Gemini | 60 | 60,000 | Unknown |
| NVIDIA | 30 | 6,000 | Unknown |
| Cerebras | 60 | 60,000 | Unknown |
| Kimi | 60 | 60,000 | Unknown |

---

## Troubleshooting

### LLM Provider Issues

```bash
# Check provider health
cd /home/ai-whisperers/solstein
python3 scripts/check_providers.py

# Test specific provider
python3 -c "
import asyncio
from src.solstein.llm import get_health_checker

async def test():
    checker = get_health_checker()
    health = await checker.check_provider('groq')
    print(f'Status: {health.status.value}')

asyncio.run(test())
"
```

### OpenAI Rate Limit

**Error**: `429 Too Many Requests`
**Solution**: Wait until Mar 2, 2026 12:04 PM or use alternative providers

### Invalid Authentication

**Error**: `401 Invalid Authentication`
**Causes**:
- Wrong API key
- Key expired
- Using Kimi Code key instead of Moonshot AI key (they're different!)
**Solution**: Get new key from correct platform

### Database Connection

```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Verify credentials
python3 -c "from src.solstein.config import get_settings; print(get_settings().database.url)"
```

### MCP Server Issues

```bash
# Run diagnostics
./scripts/opencode-mcp-doctor.sh

# Test MCP servers
./scripts/opencode-mcp-smoke-test.sh
```

---

## Architecture Overview

### LLM Client Architecture

```
┌─────────────────────────────────────────────┐
│        EnhancedLLMClient                    │
│  - Automatic provider failover              │
│  - Health checking                          │
│  - Rate limit detection                     │
│  - Cost tracking                            │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴───────┐
       │ ProviderHealthChecker
       └───────┬───────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│ Groq  │ │Fireworks│ │Mistral│
└───────┘ └───────┘ └───────┘
```

### Provider Failover Flow

```
User Request
    ↓
Try Provider 1 (e.g., Groq)
    ↓ Rate Limited?
Try Provider 2 (e.g., Fireworks)
    ↓ Failed?
Try Provider 3 (e.g., Mistral)
    ↓ ...
Success or Template Fallback
```

### Key Files

| File | Purpose |
|------|---------|
| `src/solstein/llm/enhanced_client.py` | Main LLM client with failover |
| `src/solstein/llm/health_checker.py` | Provider health monitoring |
| `src/solstein/config.py` | Configuration management |
| `src/solstein/api/middleware/security.py` | Authentication middleware |
| `src/solstein/api/middleware/rate_limit.py` | Rate limiting |
| `src/solstein/api/middleware/tracing.py` | Request tracing |

---

## Usage Examples

### Basic LLM Query

```python
from src.solstein.llm import get_enhanced_llm_client

client = get_enhanced_llm_client()
result = await client.generate(
    prompt="Explain quantum computing",
    preferred_provider="groq"  # Optional
)
print(result)
```

### Check Cost Tracking

```python
from src.solstein.llm import get_usage_tracker

tracker = get_usage_tracker()
summary = tracker.get_summary()
print(f"Total cost: ${summary['total_cost_usd']:.4f}")
print(f"Requests by provider: {summary['requests_by_provider']}")
```

### Health Check

```python
from src.solstein.llm import get_health_checker

checker = get_health_checker()
health = await checker.check_all_providers()
available = checker.get_available_providers()
print(f"Available: {available}")
```

---

## Security Notes

1. **Never commit API keys** - `.env` is in `.gitignore`
2. **Rotate keys regularly** - Especially if exposed
3. **Use environment variables** - Don't hardcode keys
4. **Enable rate limiting** - Protects against abuse
5. **Monitor usage** - Check for unexpected spikes
6. **Use local models when possible** - Ollama for sensitive data

---

## Cost Optimization Tips

1. **Use cheaper providers first**:
   - Fireworks: $0.0009/1K tokens
   - Groq: $0.00059/$0.00079 per 1K
   - Gemini: Low cost, high context

2. **Cache responses** when appropriate
3. **Use smaller models** for simple tasks
4. **Monitor usage** with `get_usage_tracker()`

---

## Changelog

### 2026-03-01
- ✅ Fixed Kimi API endpoint (CN → Global)
- ✅ Updated Groq API key
- ✅ Added 9 working providers
- ✅ Created comprehensive setup guide

### 2026-02-28
- ✅ Implemented LLM health checking system
- ✅ Added automatic provider failover
- ✅ Added cost tracking
- ✅ Upgraded to OpenCode v1.0+
- ✅ Fixed authentication middleware bypass
- ✅ Fixed N+1 query in market search

---

## Support & Resources

- **OpenCode Docs**: https://docs.opencode.ai
- **Kimi Console**: https://www.kimi.com/code/console
- **Moonshot AI Platform**: https://platform.moonshot.ai
- **Groq Console**: https://console.groq.com
- **Fireworks Console**: https://fireworks.ai

---

*This document is auto-generated and maintained as part of the Solstein project.*
