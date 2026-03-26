# Solstein TypeScript Contracts

Phase-zero TypeScript schema package for the highest-risk external integration boundaries.

Purpose:

- validate serialized external payloads outside the Python runtime
- preserve provenance for heuristic and fallback evidence
- become the future shared contract layer for frontend and tooling

Current scope:

- normalized search results
- LinkedIn heuristic output
- external evidence envelope
- patent search and patent fact payloads
- news-signal payloads and market-signal fact values

Recommended use:

- validate serialized connector outputs before frontend/tooling consumption
- keep heuristic and authoritative acquisition methods explicit in the schema
- reject payload drift before it becomes another Python-only runtime surprise

This package is intentionally isolated because the repo does not yet have a general TypeScript workspace.
