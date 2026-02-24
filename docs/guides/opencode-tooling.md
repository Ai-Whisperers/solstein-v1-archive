# OpenCode Tooling Guide

This repository now includes a project-local MCP baseline for OpenCode-compatible clients.

## What Was Added

- `.mcp.json` in the repository root with these baseline MCP servers:
  - `filesystem` via `@modelcontextprotocol/server-filesystem`
  - `sequential-thinking` via `@modelcontextprotocol/server-sequential-thinking`
- `.mcp.local.example.json` as a template for optional local-only extras:
  - `memory`
  - `playwright`
  - `github` (token-based)
- `scripts/opencode-mcp-doctor.sh` to validate local prerequisites and package availability.
- `scripts/opencode-mcp-smoke-test.sh` to prove servers stay active on stdio.

## Prerequisites

- Node.js 18+
- npm / npx

## Validate Your Machine

```bash
./scripts/opencode-mcp-doctor.sh
```

Then run runtime smoke tests:

```bash
./scripts/opencode-mcp-smoke-test.sh
```

The script checks:
- required commands (`node`, `npm`, `npx`)
- the presence of `.mcp.json`
- npm resolution for baseline MCP packages
- optional checks for local-only extras (non-blocking)
- runtime start checks that confirm server processes remain active over stdio

## Security Notes

- `.mcp.json` intentionally contains no secrets.
- Keep token-based MCP servers (for example GitHub integrations) in local config, not committed repo config.
- File access is intentionally scoped to `.` in the filesystem MCP server.

## Optional Add-ons (User-Local)

Copy `.mcp.local.example.json` to `.mcp.local.json` and customize locally.

```bash
cp .mcp.local.example.json .mcp.local.json
```

Then add personal, token-based MCP servers there so credentials are not committed.

Recommended examples:
- GitHub MCP (requires `GITHUB_TOKEN`)
- Database MCP servers for local development databases

## Updating MCP Packages

The configuration uses `npx -y` so packages are fetched on demand.
If you prefer pinned versions, replace package names in `.mcp.json` with explicit versions, for example:

```json
"args": ["-y", "@modelcontextprotocol/server-memory@2026.2.0"]
```
