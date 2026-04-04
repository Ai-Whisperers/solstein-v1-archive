# STORY-194: Build hiring signal adapters (employee trend, open jobs)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-051 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-050 (Web Acquisition Pipeline), EPIC-028 |

## Description

Build adapters that extract hiring signals: employee count trend (from LinkedIn/web) and open job count by department (from LinkedIn jobs, Indeed, company careers page).

## Acceptance Criteria

- [ ] `HiringSignalAdapter` extracts: employee_count_estimate, employee_growth_yoy, open_positions, top_hiring_departments
- [ ] Sources: LinkedIn company page (via web scraping), careers page (via crawl output from EPIC-050)
- [ ] Fields carry source provenance and confidence
- [ ] `unknown` returned when sources unavailable (no fabricated defaults)
- [ ] Unit tests with mocked source responses
