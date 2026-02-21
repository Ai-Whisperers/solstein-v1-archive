# 📜 Documentation Maintenance & Governance

**Last Updated**: February 20, 2025  
**Owner**: AI Whisperers Development Team  
**Status**: Active

## Overview

This document establishes the governance framework, update triggers, maintenance procedures, and review processes for Solstein documentation. It ensures documentation remains current, accurate, and consistent as the codebase evolves.

---

## 1. Documentation Coverage Goals

| Area | Target | Current | Status |
|------|--------|---------|--------|
| API Reference | 100% endpoints documented | 100% | ✅ Complete |
| Architectural Patterns | All modules explained | 10/10 modules | ✅ Complete |
| Troubleshooting | 40+ common issues | 40+ issues | ✅ Complete |
| Code Examples | Core use cases | 9 examples | ✅ Complete |
| Extension Patterns | 4+ templates | 4 templates | ✅ Complete |
| Code Conventions | 11 formalized rules | 11 rules | ✅ Complete |
| Testing Guide | 4-layer pyramid | 4 layers documented | ✅ Complete |
| **Overall Coverage** | **90%+** | **75%** | 🟡 In Progress |

---

## 2. Automatic Update Triggers

Documentation **MUST** be updated when:

### 2.1 Code Changes
| Trigger | Action | Owner | Deadline |
|---------|--------|-------|----------|
| New API endpoint | Update `docs/api/reference.md` | Feature author | Before merge |
| API response schema change | Update endpoint examples & response table | Feature author | Before merge |
| New domain model or entity | Update `docs/architecture/modules.md` | Feature author | Before merge |
| Scoring logic change | Update `docs/guides/troubleshooting.md` (Scoring section) | Feature author | Before merge |
| New Celery task | Update `docs/guides/operator.md` (Tasks section) | Feature author | Before merge |
| Configuration parameter added | Update `docs/guides/code-conventions.md` (Config section) | Feature author | Before merge |
| Major refactoring | Review ALL affected documentation sections | Lead dev | Within 3 days |
| Bug fix in common issue | Update `docs/guides/troubleshooting.md` | Bug fixer | Before close |

### 2.2 Dependency Changes
| Trigger | Action | Owner | Deadline |
|---------|--------|-------|----------|
| Major version upgrade | Update dependency version in guides + examples | DevOps | Before release |
| Deprecated dependency used | Update code examples, flag in troubleshooting | Feature author | Before merge |
| New optional dependency | Add to `docs/guides/developer.md` | Feature author | Before release |

### 2.3 Infrastructure Changes
| Trigger | Action | Owner | Deadline |
|---------|--------|-------|----------|
| Database schema change | Update `docs/guides/database.md` | DBA/DevOps | Before release |
| New environment variable | Update `docs/guides/operator.md` + `.env.example` | DevOps | Before release |
| CI/CD workflow change | Update `docs/guides/operator.md` (Deployment section) | DevOps | Before release |
| Monitoring/alerting rules change | Update `docs/examples/monitoring_setup.py` | DevOps | Before release |

### 2.4 Process Changes
| Trigger | Action | Owner | Deadline |
|---------|--------|-------|----------|
| New testing requirement | Update `docs/guides/developer.md` (Testing section) | QA lead | Immediate |
| New code review policy | Update `CONTRIBUTING.md` | Engineering lead | Immediate |
| New release process | Update `docs/guides/operator.md` | DevOps lead | Before first use |
| New security policy | Update `docs/guides/code-conventions.md` (Security section) | Security | Immediate |

---

## 3. Documentation Update Checklist

Before every code **merge to main**, documentation author MUST verify:

### Pre-Commit Checklist (Run Before `git commit`)

```bash
# 1. Lint documentation files
./scripts/lint-docs.sh

# 2. Validate all internal links
python scripts/validate-links.py

# 3. Check for broken references
grep -r "\[.*\](" docs/ | python scripts/check-links.py

# 4. Verify code examples are syntactically valid
python scripts/validate-examples.py

# 5. Build mkdocs locally and inspect output
mkdocs build
# Open site-build/index.html and spot-check navigation
```

### Pre-Merge Checklist (Before Creating PR)

- [ ] **API Changes**: Updated `docs/api/reference.md` with all new/modified endpoints
- [ ] **Code Changes**: Updated relevant module documentation in `docs/architecture/modules.md`
- [ ] **New Features**: Added example to `docs/examples/` if applicable
- [ ] **Breaking Changes**: Updated troubleshooting guide and upgrade notes
- [ ] **Dependencies**: Updated dependency table in relevant guide
- [ ] **Configuration**: Updated `docs/guides/code-conventions.md` if config changed
- [ ] **Tests**: Updated testing examples in `docs/guides/developer.md` if test patterns changed
- [ ] **All links verified**: Ran `python scripts/validate-links.py` with 0 errors

### Code Review Documentation Check (Reviewer MUST verify)

When reviewing PRs, reviewer MUST check:

1. **Coverage**: Does the PR include documentation updates for code changes?
   - New endpoint? → Must have API reference update
   - New module/class? → Must have architecture doc update
   - Breaking change? → Must have troubleshooting/migration note

2. **Accuracy**: Is documentation correct and up-to-date?
   - Examples still work?
   - Links valid?
   - No outdated references?

3. **Clarity**: Is documentation clear enough for a new developer?
   - Can someone understand the change in <5 min from docs alone?
   - Are edge cases documented?

**Reject PR if**:
- Code changes without corresponding documentation updates
- Examples in documentation don't match actual code behavior
- Links point to non-existent files

---

## 4. Documentation Maintenance Schedule

### Weekly (Every Monday)
- Check for **broken links** across all docs: `python scripts/validate-links.py`
- Review recent commits for undocumented changes: `git log --since="7 days ago" --grep="doc" --invert-grep`
- Update **DOCUMENTATION_INDEX.md** with any new docs added

### Monthly (1st of month)
- Audit **coverage gaps**: Compare code structure to documentation
- Review and update **troubleshooting guide** with issues from last 30 days of PRs
- Check for **outdated information** in getting-started guides
- Update **QUICK-REFERENCE.md** with common tasks from last month's PRs

### Quarterly (Jan 1, Apr 1, Jul 1, Oct 1)
- Full documentation audit (similar to `DOCUMENTATION_AUDIT.md`)
- Update **dependency tables** with current versions
- Review **code examples** and verify they still work with current codebase
- Identify **new documentation needs** from user questions/issues

### Annually (Jan 1)
- Complete **documentation refresh**: rewrite stale sections
- Update all **version numbers** and **release dates**
- Refresh **performance benchmarks** if applicable
- Review **commercial model** section if business terms changed

---

## 5. Documentation Tools & Scripts

### 5.1 Link Validation Script
**Location**: `scripts/validate-links.py`

Validates:
- Internal markdown links (`[text](../path/file.md)`)
- Absolute URLs are reachable (external links)
- No circular references in cross-links
- Link anchors exist

```bash
# Usage
python scripts/validate-links.py              # Check all links
python scripts/validate-links.py --fix        # Auto-fix relative paths
python scripts/validate-links.py --docs       # Check docs/ only
python scripts/validate-links.py --external   # Check external URLs only
```

### 5.2 Code Example Validator
**Location**: `scripts/validate-examples.py`

Validates code examples in documentation:
- Python examples parse without syntax errors
- Code blocks marked with correct language (`python`, `bash`, etc.)
- No hardcoded secrets in examples

```bash
# Usage
python scripts/validate-examples.py
python scripts/validate-examples.py --fix-syntax  # Auto-indent
python scripts/validate-examples.py --test        # Actually run examples
```

### 5.3 Documentation Linter
**Location**: `scripts/lint-docs.sh`

Checks:
- Markdown syntax (using `markdownlint`)
- Consistent heading hierarchy (H1 → H2 → H3, never skip)
- Maximum line length (120 chars for code blocks, 88 for text)
- Consistent link formatting

```bash
# Usage
./scripts/lint-docs.sh
./scripts/lint-docs.sh --fix     # Auto-fix formatting
```

### 5.4 Documentation Build & Preview
**Location**: `mkdocs.yml`

```bash
# Build static site (for review before deploy)
mkdocs build
open site-build/index.html

# Serve locally with live reload (while editing)
mkdocs serve
# Navigate to http://localhost:8000
```

---

## 6. Documentation Review Process

### Code Review Documentation Checklist

**Reviewer checks**:

```markdown
## Documentation Review Checklist

### Coverage
- [ ] API changes documented in `docs/api/reference.md`
- [ ] New modules documented in `docs/architecture/modules.md`
- [ ] Code examples added to `docs/examples/` (if applicable)
- [ ] Configuration changes noted in `docs/guides/code-conventions.md`
- [ ] Breaking changes documented in troubleshooting guide

### Quality
- [ ] Examples are syntactically valid (ran `validate-examples.py`)
- [ ] All internal links verified (ran `validate-links.py`)
- [ ] Markdown lint passes (ran `lint-docs.sh`)
- [ ] Documentation is clear enough for a new developer
- [ ] Edge cases and gotchas are documented

### Consistency
- [ ] Follows existing documentation style & format
- [ ] Uses same terminology as existing docs
- [ ] Code examples follow same conventions
- [ ] Cross-links to related documentation sections

### Reject if:
- ❌ Code changes without documentation updates
- ❌ Examples don't match actual code behavior
- ❌ Links point to non-existent files
- ❌ Documentation is incomplete or unclear
```

### Documentation-Only PR Review (for docs updates)

**Reviewer checks**:

1. **Accuracy**: Does it reflect current code?
2. **Completeness**: Are all related topics covered?
3. **Clarity**: Is it understandable to new developers?
4. **Consistency**: Does it match existing style/format?
5. **Validation**: Did author run `lint-docs.sh` and `validate-links.py`?

---

## 7. Documentation Deprecation & Archival

### When to Archive Documentation

Archive docs when:
- **Feature deprecated**: Move to `docs/archive/` with deprecation notice
- **Outdated guide**: Archive old version, create updated guide
- **Superseded by better doc**: Archive old version, cross-link to new
- **No longer relevant**: Archive with explanation of why

### Archival Process

1. Move file to `docs/archive/YYYYMMDD_[original-name].md`
2. Add header to archived file:
   ```markdown
   > ⚠️ **ARCHIVED on YYYY-MM-DD**
   > This documentation is no longer current.
   > **See instead**: [New guide name](../../guides/new-guide.md)
   > **Reason**: [Brief explanation]
   ```
3. Remove from `mkdocs.yml` nav
4. Update any cross-links to point to archived location
5. Update `docs/DOCUMENTATION_INDEX.md`

---

## 8. Documentation Standards & Style Guide

### Formatting Standards

**Headings**:
```markdown
# H1 - Page Title (only one per page)
## H2 - Section (never skip levels)
### H3 - Subsection
```

**Code Blocks**:
```markdown
(Specify language)
​```python
def example():
    return "code"
​```

(No language = plain text/output)
​```
$ command output
```
```

**Lists**:
```markdown
Unordered (use `-`):
- Item 1
- Item 2

Ordered (use `1.`):
1. First
2. Second
```

**Emphasis**:
- **Bold** for important terms
- `code` for file paths, variables, function names
- > Blockquotes for warnings/tips

### Tone & Voice

- **Direct**: "Here's how to do X" not "You might want to consider possibly doing X"
- **Active**: "Score the company" not "The company will be scored"
- **Clear**: Explain jargon, link to glossary for domain terms
- **Consistent**: Use same terminology throughout (e.g., always "Company" not "company" or "firm")

### Documentation Comments

Add inline comments for sections likely to need updates:

```markdown
<!-- MAINTENANCE: Update this table when scoring logic changes -->
## Scoring Dimensions

<!-- MAINTENANCE: Add new environment variables here -->
## Configuration
```

---

## 9. FAQ: Documentation Maintenance

**Q: How often should documentation be updated?**  
A: Continuously. Documentation updates should be part of every code change. Weekly/monthly audits catch gaps.

**Q: What if I find outdated documentation?**  
A: File an issue with label `docs:outdated` and optional PR with fix. Include what code changed that made docs stale.

**Q: How do I add a new guide?**  
A: Create `docs/guides/[name].md`, add to `mkdocs.yml` nav, update `docs/DOCUMENTATION_INDEX.md`, and run validation scripts.

**Q: Can I delete or rename a doc?**  
A: Archive instead. Move to `docs/archive/`, update mkdocs.yml, add deprecation header, and update all cross-links.

**Q: How do I preview my documentation changes?**  
A: Run `mkdocs serve` and navigate to http://localhost:8000. Changes live-reload.

**Q: What if a documentation PR conflicts with a code change?**  
A: Code change takes priority. Rebase documentation PR on updated code and verify all examples still work.

---

## 10. Contact & Escalation

**Questions about documentation?** File issue with label `docs:question`

**Found outdated content?** Label: `docs:outdated` + optional PR with fix

**Need help with documentation?** Contact documentation owner or file `docs:help` issue

**Documentation governance issues?** Escalate to engineering lead

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-02-20 | Initial documentation maintenance guide created | AI Whisperers |
