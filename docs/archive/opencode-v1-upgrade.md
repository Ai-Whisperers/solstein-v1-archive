# OpenCode v1.0+ Integration Guide

> **Status**: Updated 2026-02-28
> **OpenCode Version**: v1.0+ (Minimum: 1.0.216 for security)
> **AGENTS.md Version**: v2.0

## Overview

This codebase has been upgraded to support **OpenCode v1.0+**, the open-source AI coding agent platform. This guide explains the improvements and how to use them.

## What's New in OpenCode v1.0+

### 1. Granular Permissions System

Instead of binary `tools: ["write", "edit", "bash"]` permissions, OpenCode v1.0+ supports pattern-based permissions:

```json
{
  "permissions": {
    "bash": {
      "uv *": "allow",
      "pip *": "allow",
      "pytest *": "allow",
      "rm *": "deny",
      "sudo *": "deny",
      "*": "ask"
    },
    "read": {
      "**/*.py": "allow",
      "**/.env*": "deny"
    },
    "write": {
      "**/*.py": "allow",
      "**/.env*": "deny"
    }
  }
}
```

**Benefits**:
- Finer control over what AI can do
- Prevent dangerous operations (`rm -rf`, `sudo`)
- Block access to sensitive files (`.env`, credentials)
- Allow common development commands without prompting

### 2. Subagent Delegation with Budgets

Agents can now delegate to specialized subagents with "call budgets" to prevent infinite loops:

```json
{
  "agents": {
    "build": {
      "budget": 500,
      "tools": ["write", "edit", "bash"]
    },
    "plan": {
      "budget": 300,
      "tools": ["read", "analyze"],
      "readOnly": true
    }
  }
}
```

**Available Agents**:

| Agent | Purpose | Budget | Mode |
|-------|---------|--------|------|
| `@build` | Implementation | 500 | Read/Write |
| `@plan` | Architecture | 300 | Read-Only |
| `@review` | Code Quality | 200 | Read-Only |
| `@test` | Test Generation | 200 | Read/Write |
| `@docs` | Documentation | 150 | Read/Write |

### 3. Multi-Session Workflows

Run different agents in parallel sessions:

```bash
# Terminal 1: Plan Agent analyzes codebase
opencode @plan

# Terminal 2: Build Agent implements changes
opencode @build
```

### 4. Command Bar (Ctrl+P)

Quick access to:
- Switch agents
- Change LLM providers
- Manage sessions
- View history

## Configuration Files

### 1. `.mcp.json` - MCP Server Configuration

**Location**: `/.mcp.json`

Configures MCP (Model Context Protocol) servers:

```json
{
  "version": "2.0",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  },
  "permissions": { ... },
  "agents": { ... }
}
```

### 2. `opencode.yml` - Project Configuration

**Location**: `/opencode.yml`

Comprehensive project configuration:

```yaml
version: "2.0"
project:
  name: solstein
  language: python

permissions:
  bash:
    allow: ["pytest *", "python *", "git *"]
    deny: ["rm -rf *", "sudo *"]

agents:
  build:
    budget: 500
    tools: ["write", "edit", "bash"]

providers:
  primary: auto
  fallback_chain:
    - ollama
    - fireworks
    - openai
    - groq
```

### 3. `.opencode/settings.json` - Team Settings

**Location**: `/.opencode/settings.json`

Team-shared configuration:

```json
{
  "permissions": { ... },
  "hooks": { ... },
  "commands": { ... },
  "agents": { ... }
}
```

### 4. `.opencode/agents/*.json` - Agent Definitions

**Location**: `/.opencode/agents/`

Individual agent configurations with system prompts.

## Provider Configuration

### Multi-Provider Support

This codebase supports multiple LLM providers with automatic failover:

```
Priority: Ollama (local) → Fireworks → OpenAI → Groq
```

### Health Checking

Proactive health monitoring detects:
- **Rate limits** (429) → Retry after delay
- **Quota exhaustion** (402) → Switch provider
- **Auth failures** (401) → Alert user

See: `src/solstein/llm/health_checker.py`

### Configuration

```yaml
# opencode.yml
providers:
  primary: auto
  fallback_chain:
    - ollama      # Local, for sensitive data
    - fireworks   # Cost-effective
    - openai      # General purpose
    - groq        # Fast inference

  models:
    ollama: llama3.2:latest
    openai: gpt-4o-mini
    groq: llama-3.3-70b-versatile
    fireworks: qwen2-72b-instruct
```

## Usage Patterns

### 1. Quick Start

```bash
# Check OpenCode is installed and configured
./scripts/opencode-mcp-doctor.sh

# Start OpenCode CLI
opencode

# Check version
opencode --version  # Should be >= 1.0.216
```

### 2. Using Agents

```bash
# Plan phase (read-only analysis)
@plan Analyze the scoring algorithm and propose improvements

# Build phase (implementation)
@build Implement the proposed scoring changes with tests

# Review phase (quality check)
@review Check the implementation against our standards

# Test phase (generate tests)
@test Write comprehensive tests for the new scoring module
```

### 3. Slash Commands

Available commands defined in `.opencode/settings.json`:

```bash
/test          # Run test suite
/lint          # Run linting checks
/format        # Format all code
/typecheck     # Run type checking
/mcp-check     # Check MCP servers
/health        # Check LLM provider health
```

### 4. Hooks and Automation

**Session Start Hook**:
```json
{
  "hooks": {
    "SessionStart": [{
      "type": "notification",
      "message": "🚀 Solstein | OpenCode v1.0+ session started"
    }]
  }
}
```

**Pre-Tool Hook** (block dangerous operations):
```json
{
  "PreToolUse": [{
    "matcher": "Write(**/.env*)",
    "hooks": [{
      "type": "confirm",
      "message": "⚠️ Attempting to write to .env file. Confirm?"
    }]
  }]
}
```

## Security

### Minimum Version

**⚠️ CRITICAL**: Must use OpenCode v1.0.216+ for security fix:

- **CVE-2026-22812**: Fixed in v1.0.216
- **Issue**: Unauthenticated HTTP server vulnerability
- **Impact**: Local privilege escalation
- **Fix**: Update immediately

```bash
# Check current version
opencode --version

# Update if needed
npm update -g @opencode-ai/cli
```

### Secret Protection

The following are **automatically blocked**:

```json
{
  "permissions": {
    "read": {
      "deny": [
        "**/.env*",
        "**/credentials*",
        "**/secrets*",
        "**/*.key",
        "**/*.pem"
      ]
    }
  }
}
```

## Troubleshooting

### MCP Servers Not Working

```bash
# Run diagnostics
./scripts/opencode-mcp-doctor.sh

# Test MCP servers
./scripts/opencode-mcp-smoke-test.sh
```

### Provider Failures

```bash
# Check LLM provider health
python3 -c "
from src.solstein.llm import get_health_checker
import asyncio
health = asyncio.run(get_health_checker().check_all_providers())
print(health)
"
```

### Configuration Issues

```bash
# Validate JSON configs
python3 -m json.tool .mcp.json > /dev/null && echo "✓ .mcp.json valid"

# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('opencode.yml'))" && echo "✓ opencode.yml valid"
```

## Migration from OpenCode < v1.0

### Old Format (Deprecated)

```json
{
  "tools": ["write", "edit", "bash"],
  "mcpServers": { ... }
}
```

### New Format (v1.0+)

```json
{
  "version": "2.0",
  "permissions": {
    "bash": { "pytest *": "allow", "rm *": "deny" },
    "write": { "**/*.py": "allow" }
  },
  "mcpServers": { ... },
  "agents": { ... }
}
```

### Migration Steps

1. Add `"version": "2.0"` to `.mcp.json`
2. Replace `tools` array with `permissions` object
3. Create `opencode.yml` for project config
4. Create `.opencode/settings.json` for team config
5. Update AGENTS.md to v2.0 format

## Best Practices

### 1. Use Read-Only Agents for Analysis

```bash
# Good: Plan agent is read-only
@plan Analyze the database schema

# Good: Review agent is read-only
@review Check this PR for issues
```

### 2. Parallel Sessions

```bash
# Terminal 1: Long-running analysis
@plan Research microservices patterns

# Terminal 2: Quick implementation
@build Fix this type error
```

### 3. Provider Fallbacks

Configure multiple providers for reliability:

```yaml
providers:
  fallback_chain:
    - ollama
    - fireworks
    - openai
    - groq
```

### 4. Budget Management

Set appropriate budgets to prevent runaway costs:

```json
{
  "agents": {
    "build": { "budget": 500 },
    "plan": { "budget": 300 }
  }
}
```

## Resources

- [OpenCode Documentation](https://docs.opencode.ai)
- [AGENTS.md Standard](https://docs.opencode.ai/agents.md)
- [MCP Specification](https://modelcontextprotocol.io)
- [Project AGENTS.md](../../AGENTS.md)

## Changelog

### 2026-02-28 - OpenCode v1.0+ Upgrade

- ✅ Updated AGENTS.md to v2.0 format
- ✅ Added granular permissions to `.mcp.json`
- ✅ Created `opencode.yml` configuration
- ✅ Created `.opencode/settings.json` team config
- ✅ Created subagent definitions in `.opencode/agents/`
- ✅ Updated MCP scripts for v1.0+ compatibility
- ✅ Added health checking for LLM providers
- ✅ Configured provider fallback chain
