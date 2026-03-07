# OMC-EPIC-001: MCP Server Catalog & Discovery

|**Status:** 🔴 Not Started  
|**Priority:** HIGH (P1)  
|**Story Points:** 34  
|**Sprint Allocation:** 3 sprints  
|**Target Date:** Week 1-3

---

## Problem Statement

OhMyOpenCode (OMO) lacks a centralized catalog of MCP (Model Context Protocol) servers and tools. The OpenClaw API list contains 131 MCP servers, but there's no systematic way to discover, evaluate, or integrate them into the OMO ecosystem. Users cannot easily find MCP servers relevant to their workflows.

### Impact
- Users cannot discover available MCP servers
- No quality assessment of MCP servers
- Integration is ad-hoc and inconsistent
- Missing valuable tools from the OpenClaw list
- No community contributions to MCP catalog

---

## Success Criteria

1. ✅ Centralized MCP server catalog with structured metadata
2. ✅ 100+ MCP servers from OpenClaw imported and categorized
3. ✅ Quality scoring for MCP servers (reliability, documentation, functionality)
4. ✅ Easy integration path for users
5. ✅ Community contribution workflow for new MCP servers

---

## Stories

### Story 1.1: MCP Catalog Data Model (8 pts)
**Task:** Design catalog schema for MCP servers

**Acceptance Criteria:**
- [ ] Schema includes: name, description, provider, category, auth_type
- [ ] Capabilities metadata: tools, resources, prompts supported
- [ ] Quality metrics: documentation_score, reliability_score, community_score
- [ ] Installation metadata: package name, npm/pip install commands
- [ ] Configuration schema for each MCP server

**Schema:**
```yaml
# .omocode/mcp-catalog-schema.yaml
mcp_server:
  id: string
  name: string
  description: string
  provider: string
  
  # Categorization
  category: enum[filesystem, web_search, database, api_integration, devtools, other]
  tags: [string]
  
  # Capabilities
  capabilities:
    tools: [string]  # List of available tools
    resources: [string]  # Available resources
    prompts: [string]  # Available prompts
    
  # Installation
  package:
    type: enum[npm, pip, docker, binary]
    name: string
    install_command: string
    
  # Configuration
  config:
    required_env_vars: [string]
    optional_env_vars: [string]
    config_schema: object  # JSON Schema
    
  # Quality Scores (0-1)
  quality:
    documentation: float
    reliability: float
    functionality: float
    community: float  # Stars, usage, activity
    overall: float
    
  # Metadata
  added_date: date
  last_verified: date
  status: enum[active, deprecated, experimental]
```

---

### Story 1.2: MCP Catalog CLI (8 pts)
**Task:** Build CLI for MCP server management

**Acceptance Criteria:**
- [ ] `omo mcp list` - List all MCP servers with filters
- [ ] `omo mcp search <query>` - Search by name, category, capability
- [ ] `omo mcp show <server_id>` - Display detailed server info
- [ ] `omo mcp install <server_id>` - Install and configure MCP server
- [ ] `omo mcp config <server_id>` - Interactive configuration
- [ ] `omo mcp test <server_id>` - Test MCP server connection

**Implementation:**
```python
# src/omocode/cli/mcp_commands.py
@click.group()
def mcp():
    """Manage MCP servers and integrations."""
    pass

@mcp.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--capability', '-cap', help='Filter by capability')
@click.option('--quality', '-q', type=float, help='Minimum quality score')
def list(category, capability, quality):
    """List available MCP servers."""
    catalog = MCPCatalog.load()
    servers = catalog.filter(
        category=category,
        capability=capability,
        min_quality=quality
    )
    
    table = Table(title="Available MCP Servers")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Quality", style="yellow")
    table.add_column("Status", style="blue")
    
    for server in servers:
        table.add_row(
            server.name,
            server.category,
            f"{server.quality.overall:.2f}",
            server.status
        )
    
    console.print(table)

@mcp.command()
@click.argument('server_id')
def install(server_id):
    """Install an MCP server."""
    catalog = MCPCatalog.load()
    server = catalog.get(server_id)
    
    if not server:
        console.print(f"[red]MCP server '{server_id}' not found[/red]")
        return
    
    # Run installation
    installer = MCPInstaller(server)
    installer.install()
    
    # Configure
    configurer = MCPConfigurer(server)
    configurer.interactive_setup()
    
    console.print(f"[green]✓ MCP server '{server.name}' installed successfully[/green]")
```

---

### Story 1.3: OpenClaw MCP Import (8 pts)
**Task:** Import and categorize MCP servers from OpenClaw

**Acceptance Criteria:**
- [ ] Importer for OpenClaw MCP server list
- [ ] 131 MCP servers imported into catalog
- [ ] Automatic categorization based on capabilities
- [ ] Quality scoring based on available metadata
- [ ] Duplicate detection with existing catalog

---

### Story 1.4: MCP Quality Scoring (5 pts)
**Task:** Implement quality assessment for MCP servers

**Acceptance Criteria:**
- [ ] Documentation quality scoring (README completeness)
- [ ] Reliability testing (connection, basic operations)
- [ ] Functionality scoring (tool count, capability coverage)
- [ ] Community metrics (GitHub stars, last update)
- [ ] Overall quality score calculation

---

### Story 1.5: MCP Community Contributions (5 pts)
**Task:** Enable community to suggest new MCP servers

**Acceptance Criteria:**
- [ ] GitHub issue template for MCP suggestions
- [ ] Submission form for new MCP servers
- [ ] Review workflow for community submissions
- [ ] Recognition for contributors

---

## Definition of Done

- [ ] MCP catalog schema defined
- [ ] CLI commands operational
- [ ] 100+ MCP servers imported from OpenClaw
- [ ] Quality scoring system active
- [ ] Community contribution workflow live
- [ ] Documentation published

---

## Resources

- **Developers:** 1-2 engineers
- **Time:** 3 weeks
- **Dependencies:** None

---

*Epic for OhMyOpenCode - MCP Server Catalog*
