# STORY-060: Define Environment Configuration via Infrastructure-as-Code

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-007: Remove Hardcoded Credentials](../../EPIC-001-security-restoration/STORIES/STORY-007.md), [STORY-059: Dockerize Application](STORY-059-dockerize-application.md) |

---

## The Audit Verdict
> Environment configuration is managed manually. Which environment variables are set in production, who set them, when they were last updated, and whether they match what the application expects are all unknowable without direct server access. Configuration drift between environments is undetectable.

## Problem Statement
Manual environment configuration is not auditable, not version-controlled, and not reproducible. A production environment that differs from staging in a non-obvious configuration variable produces bugs that cannot be reproduced locally. No one knows the complete list of configuration variables required in production because no authoritative list exists. Configuration changes are applied by SSH-ing into a server and editing files — a process that leaves no audit trail and is one typo away from an outage.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Configuration drift between environments causes environment-specific bugs that are unreproducible and undiagnosable |
| **Auditability** | No record of when configuration changed or who changed it — compliance and incident investigation are impaired |
| **Disaster Recovery** | Recreating the production environment requires knowledge that may not be documented — a total loss scenario has unknown recovery time |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `infrastructure/` | Add | New directory: IaC configuration files (Terraform, Ansible, or equivalent) |
| `docs/environment-variables.md` | Add | Comprehensive environment variable documentation |
| CI/CD secrets configuration | Add | Secret references for the CI/CD platform |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: All environment variables required by the application must be defined in version-controlled IaC files (Terraform variables, Ansible vars, or equivalent)
- **REQ-2**: Environment-specific values (staging vs production) must be separated — not co-mingled in one file
- **REQ-3**: Secret values must be referenced from a secrets manager — not stored in plaintext in IaC files
- **REQ-4**: A `docs/environment-variables.md` must document every environment variable: name, description, required/optional, default value (if any), and format
- **REQ-5**: Applying the IaC configuration to a new environment must be a documented, runnable procedure

## Acceptance Criteria
- [ ] All environment variables are defined in version-controlled IaC files
- [ ] `docs/environment-variables.md` documents every environment variable with name, description, required/optional, default, and format
- [ ] Secret values are not stored in plaintext in any committed file
- [ ] Environment-specific configurations are separated (not mixed in one file)
- [ ] A new environment can be provisioned by following the documented IaC procedure

## Definition of Done

**Tests Required:**
- [ ] Automated scan of IaC files for plaintext secrets (must find zero)
- [ ] Apply IaC to a test environment and verify the application starts correctly

**Documentation Required:**
- [ ] `docs/environment-variables.md` complete and peer-reviewed
- [ ] IaC apply procedure documented step-by-step

**Code Review Gate:**
- [ ] Reviewer confirms no plaintext secrets in any committed file
- [ ] Reviewer confirms environment separation (staging and production are distinct)

## Notes
This story depends on STORY-007 (hardcoded credentials removed) because IaC formalises the environment variable injection that replaces those hardcoded values. It depends on STORY-059 (Dockerfile) because the Docker image is the deployment artifact that consumes these environment variables. The choice of IaC tool (Terraform, Ansible, Pulumi, etc.) should be made based on the team's existing expertise and the deployment target — the requirements here are tool-agnostic.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
