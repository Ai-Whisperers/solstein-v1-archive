# LinkedIn And Proxycurl

Verified on `2026-03-26`.

## Local Usage

- [linkedin.py](../../../src/solstein/data/sources/linkedin.py)
- [linkedin_refresh.py](../../../src/solstein/infrastructure/connectors/linkedin_refresh.py)
- [linkedin.py](../../../src/solstein/connectors/social/linkedin.py)
- [linkedin_unified.py](../../../src/solstein/adapters/enrichment/linkedin_unified.py)

## Current Reality In Solstein

Solstein does not currently have a real production LinkedIn contract.

What exists today:

- a placeholder official-API connector at `https://api.linkedin.com/v2`
- news-derived heuristics that produce `LinkedInData`
- refresh facts that are explicitly marked as `news_heuristic`

So the live pipeline should currently be treated as:

- LinkedIn-themed evidence
- not authoritative LinkedIn company API data

## Official Surfaces

### LinkedIn

- API family referenced in code: `https://api.linkedin.com/v2`
- `robots.txt`: `https://www.linkedin.com/robots.txt`
- `llms.txt`: `https://www.linkedin.com/llms.txt` returned `404` in this pass

The current robots file explicitly warns that automated access without permission is prohibited.

### Proxycurl

- Docs URL attempted in this pass: `https://nubela.co/proxycurl/docs`
- `robots.txt`: `https://nubela.co/robots.txt`
- `llms.txt`: `https://nubela.co/proxycurl/llms.txt` returned `404` in this pass

The docs URL returned `403` in this pass, so discoverability is only partially verified from the public web surface.

## Good Patterning

- Treat official LinkedIn API access as a separate integration class from Proxycurl.
- Treat news-derived hiring heuristics as a third class, lower confidence than both.
- Never collapse these three evidence classes into one generic `linkedin` contract.
- Keep `source`, `method`, and `authority` explicit in normalized payloads.
- If Proxycurl is added, its payloads should have their own strict schema and confidence policy.

## Current Contract Drift

- [linkedin.py](../../../src/solstein/connectors/social/linkedin.py) presents an official API connector shell but does not implement search.
- [linkedin.py](../../../src/solstein/data/sources/linkedin.py) is explicitly heuristic and news-derived.
- [linkedin_refresh.py](../../../src/solstein/infrastructure/connectors/linkedin_refresh.py) emits facts from the heuristic path.

These are different contracts and should not share one mental model.

## Caveats

- LinkedIn is explicitly automation-hostile without approved access.
- Proxycurl may be operationally useful, but it is not the same thing as official LinkedIn API access.
- The current pipeline uses heuristic hiring signals and must keep that lower-confidence label end-to-end.

## Test Gates

- heuristic LinkedIn payload schema
- source-method tagging regression tests
- confidence-policy tests proving heuristics cannot silently masquerade as authoritative profile data
- contract tests for Proxycurl if and when it is added
