# FD-030: Perplexity AI Integration

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Accelerates**: All research prompts (`research-competitor`, `research-financial-growth`, `research-company-history`, `research-protocols`, `research-ai-maturity`, `research-competitive-overlap`, `assess-data-confidence`, `research-market-trends`, `research-customer-intelligence`)

## Objective

Integrate Perplexity AI as a research accelerator for the market analysis prompt library. Perplexity provides citation-backed web research with real-time data, making it ideal for the structured competitor research workflow. This ticket covers both the technical integration (API/MCP) and the prompt adaptations needed to leverage Perplexity effectively.

## Why Perplexity

Current research workflow relies on manual web searches through the Cursor agent's built-in web tools. Perplexity offers:

- **Citation-backed answers**: Every claim comes with source URLs, matching the source attribution requirements of all research prompts
- **Real-time data**: Access to current web content (annual reports, press releases, LinkedIn)
- **Structured queries**: Natural language queries return structured, summarized answers
- **Follow-up capability**: Iterative questioning to drill deeper on specific data points
- **Speed**: Significantly faster than manual web search for multi-dimensional competitor research

## Scope

### In Scope

1. **Perplexity MCP Server Integration**: Configure Perplexity as an MCP tool server in Cursor
2. **Research Prompt Adaptation**: Update all market analysis prompts to include Perplexity-specific search strategies alongside manual web search
3. **Citation Mapping**: Define how Perplexity citations map to the Confirmed/Estimated/Unknown confidence levels used across prompts
4. **Batch Research Workflow**: Define how to use Perplexity to research multiple competitors efficiently (avoid redundant queries)
5. **Rate Limiting & Cost Management**: Document API usage patterns and cost considerations

### Out of Scope

- Building a fully automated research pipeline (prompts remain agent-driven, Perplexity is a tool)
- Replacing manual verification (Perplexity augments, doesn't replace primary source checking)
- Custom Perplexity fine-tuning

## Requirements

1. Configure Perplexity as an MCP tool server in the Cursor workspace with API key management via environment variables
2. Update at least 3 existing research prompts with a "Perplexity Search Strategy" section that includes recommended query patterns, citation interpretation guidance, and tool selection criteria (Perplexity vs direct web search)
3. Define a citation-to-confidence mapping that translates Perplexity source types (annual reports, news articles, LinkedIn, uncited) to the Confirmed/Estimated/Unknown confidence levels used across all research prompts
4. Document a batch research workflow for running Perplexity-accelerated research across N competitors while minimizing redundant queries
5. Document API rate limiting behavior and cost management guidelines, including per-query cost awareness for 33+ competitor research runs
6. Update Prompt Registry frontmatter (`tools:` field) in all adapted prompts to reference the Perplexity MCP tool

## Acceptance Criteria

- [ ] Perplexity MCP server configured and working in Cursor workspace
- [ ] At least 3 existing research prompts updated with Perplexity search strategy sections
- [ ] Citation-to-confidence mapping documented (Perplexity citation -> Confirmed/Estimated/Unknown)
- [ ] Batch research workflow documented (how to research N competitors efficiently)
- [ ] Cost/usage guidelines documented
- [ ] Integration tested on at least 2 competitors with before/after comparison (speed + data quality)
- [ ] Prompt Registry updated with Perplexity tool references in frontmatter

## Complexity Assessment

- **Track**: Complex Implementation
- **Rationale**: Involves external API integration, updates across multiple prompt files, and new workflow design -- no single-file fix
- **Effort**: 3-4 hours
- **Risk**: Medium (API availability, cost management, citation quality varies)

**Criteria Met**:
- Root Cause: Multiple (API setup + prompt adaptation + workflow documentation)
- Files Affected: >3 (MCP config, 3+ prompt files, documentation files)
- Lines Changed: >10 (new sections in each prompt, new documentation files)
- Risk Level: Medium (external API dependency, cost implications at scale)
- Solution Pattern: Partially known (MCP integration is established; Perplexity-specific patterns need research)

## Implementation Strategy

### Phase A: MCP Integration (1-2h)

1. Research Perplexity MCP server options (official vs community)
2. Configure MCP server in `.cursor/mcp.json` or equivalent
3. Test basic queries through MCP tools
4. Document setup in `.cursor/prompts/analysis/market/` README or integration guide

### Phase B: Prompt Adaptation (1-2h)

1. Add `perplexity` to `tools:` frontmatter in research prompts
2. Add "Perplexity Search Strategy" section to each prompt with:
   - Recommended query patterns for each research category
   - How to interpret Perplexity citations vs manual sources
   - When to use Perplexity vs direct web search (Perplexity for broad questions, direct search for specific documents like annual reports)
3. Update citation-to-confidence mapping:
   - Perplexity citing annual report / SEC filing -> Confirmed
   - Perplexity citing news article / LinkedIn -> Estimated
   - Perplexity with no citation or weak source -> needs manual verification

### Phase C: Workflow Documentation (30min)

1. Document batch research pattern (how to run Perplexity-accelerated research across N competitors)
2. Document cost management guidelines
3. Add integration guide to prompts folder

## Technical Approach

### MCP Server Configuration

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@anthropic/perplexity-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    }
  }
}
```

(Exact package name and configuration to be researched during implementation.)

### Query Patterns

| Research Category | Perplexity Query Pattern |
|---|---|
| Revenue & Financials | "[COMPANY] revenue 2024 2025 annual report financial results" |
| Funding & Investment | "[COMPANY] funding round investors valuation 2024 2025" |
| Employee Growth | "[COMPANY] employees headcount growth 2024 2025 LinkedIn" |
| AI & Innovation | "[COMPANY] AI features machine learning product energy software" |
| M&A Activity | "[COMPANY] acquisition merger 2023 2024 2025 energy software" |
| Geographic Expansion | "[COMPANY] new markets countries offices 2024 2025" |
| Customer Wins | "[COMPANY] new customer contract win energy utility 2024 2025" |

## Dependencies

- Perplexity API key (user must obtain)
- MCP server package availability
- Cursor MCP support (confirmed available)

## Notes

- Perplexity Pro subscription recommended for higher rate limits and access to more recent data
- API costs are per-query; batch efficiency matters for 33+ competitors
- Perplexity Sonar model recommended for research tasks (better citations than standard)

## Status

Planning
