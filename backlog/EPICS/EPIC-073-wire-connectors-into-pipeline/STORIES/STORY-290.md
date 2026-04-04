# STORY-290: Create GitHub enrichment adapter

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None (GITHUB_TOKEN exists) |

## Description

Create an enrichment adapter that uses the GitHub API to detect tech stack, repo activity, and open source signals for companies with known GitHub organizations.

## Acceptance Criteria

- [ ] Adapter implements `EnrichmentAdapter` interface
- [ ] Fetches repos, stars, contributors, dependency languages for org
- [ ] Detects ML frameworks (tensorflow, pytorch, sklearn) in dependencies
- [ ] Uses GITHUB_TOKEN for authentication
- [ ] Handles missing org gracefully (returns empty result)
- [ ] Unit tests with mocked GitHub API responses
