# Retired Discovery Adapters

## STORY-264: Replaceable Provider Surface Removal

These discovery adapters have been removed from the canonical registry
because they wrap replaceable third-party services that have self-hosted
or free alternatives already available in the stack.

### Moved Here

| File | Provider | Replacement | LOC |
|------|----------|-------------|-----|
| `web_search.py` | Exa Search | SearXNG (self-hosted) | 66 |

### Why Not Deleted

Code is retained so it can be referenced when building the SearXNG-backed
replacement adapter. Delete after the replacement is wired and passing
golden-run tests (EPIC-070).

### Deletion Trigger

EPIC-070 golden runs confirm the canonical runtime produces equivalent
results without these adapters.
