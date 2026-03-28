## Summary

<!-- What does this PR do? Keep it to 2-3 sentences. -->

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor / cleanup
- [ ] Documentation
- [ ] CI / tooling
- [ ] Other: ___

## Story Reference

<!-- Link to the story or epic this PR addresses, e.g., STORY-168 / EPIC-043 -->

Story:

## Testing

<!-- Describe how you tested this change. -->

- [ ] Unit tests added / updated
- [ ] Integration tests added / updated
- [ ] Manually tested locally

## Quality Gates

<!-- Run `make quality` before submitting. All gates must pass. -->

- [ ] `make lint` passes
- [ ] `make type-check` passes
- [ ] `make test` passes
- [ ] No new code smells (`make smell`)
- [ ] File sizes within limits (`make check-sizes`)

## Docs Quality Gates (if this PR touches docs/ or backlog/)

<!-- See docs/guides/docs-change-control.md for the full checklist. -->

- [ ] `make docs-quality-check` passes (placeholder tokens + metadata)
- [ ] `make docs-generated-check` passes (if generated docs were re-generated)
- [ ] Link integrity: no broken relative links
- [ ] Governance / standards docs: blockquote metadata updated (`Last Reviewed` → today)
- [ ] Major change impact summary included (required for governance/standards/architecture docs)

## Repository Organization

<!-- See REPOSITORY_STRUCTURE.md for placement rules. -->

- [ ] New files are placed in the correct location (not dumped at repo root)
- [ ] Documentation added under `docs/<appropriate-subdirectory>/`
- [ ] No sensitive data (API keys, secrets) added to committed files

## Checklist

- [ ] PR title follows convention: `<type>(<scope>): <description>`
- [ ] Branch targets `develop` (not `main`)
- [ ] `planning/QUEUE.md` updated on `develop` **after** this PR merges (not in this branch)
- [ ] Breaking changes documented in PR description
