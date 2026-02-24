# 📋 Documentation Review Checklist

**Use this checklist when reviewing code PRs to verify documentation completeness.**

This checklist ensures that all code changes have corresponding documentation updates before merging.

---

## PR Type: Code Change with Documentation

When reviewing PRs that include code changes, **reviewer MUST verify documentation coverage**.

### 1. Coverage: Does PR include documentation for code changes?

**Check for these triggers and required documentation updates:**

#### API Changes
- [ ] **New endpoint added?** → MUST update `docs/api/reference.md`
  - [ ] Endpoint path and method documented
  - [ ] Request/response schemas documented
  - [ ] Success and error status codes listed
  - [ ] Example curl/Python requests provided
  - [ ] Authorization requirements documented

- [ ] **Existing endpoint modified?** → MUST update `docs/api/reference.md`
  - [ ] Parameter changes documented
  - [ ] Response format changes documented
  - [ ] Deprecation notices added if breaking
  - [ ] Migration guide provided if breaking

- [ ] **API error response changed?** → MUST update `docs/api/reference.md#error-responses`
  - [ ] Error codes documented
  - [ ] Error message format documented
  - [ ] Example error responses included

#### Code Structure Changes
- [ ] **New module/package added?** → MUST update `docs/architecture/modules.md`
  - [ ] Module purpose explained
  - [ ] Key classes/functions documented
  - [ ] Module responsibilities listed
  - [ ] Data flow illustrated
  - [ ] Extension points identified

- [ ] **New class or interface?** → MUST update `docs/architecture/modules.md` or new example
  - [ ] Class purpose and usage documented
  - [ ] Constructor parameters documented
  - [ ] Public methods documented
  - [ ] Example usage provided

- [ ] **New feature or capability?** → SHOULD add example to `docs/examples/`
  - [ ] Complete working example provided
  - [ ] Example is self-contained and runnable
  - [ ] Example includes comments explaining each step

#### Configuration Changes
- [ ] **New environment variable?** → MUST update `docs/guides/code-conventions.md`
  - [ ] Variable name and purpose documented
  - [ ] Default value listed
  - [ ] Valid values/constraints documented
  - [ ] When it's required vs optional

- [ ] **New configuration parameter?** → MUST update `docs/guides/code-conventions.md`
  - [ ] Parameter documented
  - [ ] Data type and valid values documented
  - [ ] Default behavior explained
  - [ ] Example usage provided

#### Behavioral Changes
- [ ] **Scoring logic changed?** → MUST update `docs/guides/troubleshooting.md` (Scoring section)
  - [ ] Describe what changed
  - [ ] Explain why it changed
  - [ ] Note any implications for existing data

- [ ] **Database schema changed?** → MUST update `docs/guides/database.md`
  - [ ] Schema migration documented
  - [ ] Backward compatibility considerations
  - [ ] Manual data migration steps if needed

- [ ] **New Celery task?** → MUST update `docs/guides/operator.md`
  - [ ] Task name and purpose documented
  - [ ] Input parameters documented
  - [ ] Expected output documented
  - [ ] Failure scenarios documented
  - [ ] Manual invocation instructions provided

- [ ] **New testing pattern?** → MUST update `docs/guides/developer.md`
  - [ ] Pattern explained with rationale
  - [ ] Example test code provided
  - [ ] Common mistakes/gotchas noted

- [ ] **Breaking change?** → MUST update `docs/guides/troubleshooting.md`
  - [ ] Clearly marked as breaking change
  - [ ] Migration guide provided
  - [ ] Timeline for deprecation (if applicable)
  - [ ] Alternative solutions documented

#### Dependency Changes
- [ ] **Major version upgrade?** → MUST update affected guides
  - [ ] New version number documented in examples
  - [ ] Breaking changes noted
  - [ ] Migration steps documented if needed
  - [ ] Compatibility matrix updated

- [ ] **New dependency added?** → MUST update `docs/guides/developer.md`
  - [ ] Dependency purpose documented
  - [ ] Why it was chosen (vs alternatives)
  - [ ] Installation instructions
  - [ ] Configuration requirements
  - [ ] Example usage

### 2. Quality: Are examples accurate and current?

- [ ] **Code examples work** — Do examples in the documentation actually work with the current code?
  - Run example code mentally through current codebase
  - Check for API changes that would break examples
  - Verify imports are correct for current structure

- [ ] **Examples follow current patterns** — Do examples match existing code style?
  - Check if new examples follow conventions in `docs/guides/code-conventions.md`
  - Verify examples use current recommended approaches (not deprecated patterns)
  - Confirm examples match style of existing documentation

- [ ] **Links are valid** — Do all cross-links work?
  - Check that referenced sections exist
  - Verify file paths are correct (relative links should resolve)
  - Confirm anchor links (#section) exist in target files

- [ ] **Documentation is complete** — Does it answer obvious questions?
  - "What is this?"
  - "Why would I use this?"
  - "How do I use this?"
  - "What are edge cases or gotchas?"
  - "Where can I find more information?"

### 3. Consistency: Does documentation fit existing style/format?

- [ ] **Follows documentation structure** — Does new documentation match existing pattern?
  - Same heading hierarchy (not skipping H2/H3 levels)
  - Same terminology as existing docs (don't introduce synonyms)
  - Same tone and voice (direct, active voice)
  - Code blocks properly marked with language (`python`, `bash`, etc.)

- [ ] **Consistent with existing examples** — Do new examples match existing style?
  - Same code style (naming conventions, formatting)
  - Same level of detail in comments
  - Same structure and organization
  - Similar complexity for similar topics

- [ ] **Cross-links included** — Does documentation reference related topics?
  - Link from new doc to related existing docs
  - Link from existing docs to new doc (if relevant)
  - Use "See also" section for related topics
  - Provide both conceptual and reference links

### 4. Automated Checks

Before approval, verify automated checks pass:

- [ ] **Pre-commit hooks passed**
  - [ ] Documentation lint: `bash scripts/lint-docs.sh`
  - [ ] Link validation: `python3 scripts/validate-links.py --no-external`
  - [ ] Code examples: `python3 scripts/validate-examples.py`

- [ ] **Manual verification**
  - [ ] Can build mkdocs locally: `mkdocs build`
  - [ ] Navigation looks correct in `site-build/index.html`
  - [ ] No broken internal links on generated site

### 5. Rejection Criteria

**Reject PR if ANY of these are true:**

- ❌ Code changes without corresponding documentation updates
- ❌ Documentation examples don't match actual code behavior
- ❌ Links point to non-existent files/anchors
- ❌ Documentation is incomplete or unclear for new developers
- ❌ Pre-commit hook failures (lint, link validation, examples)
- ❌ Breaking changes not documented with migration guide
- ❌ New external dependencies not mentioned in docs

---

## PR Type: Documentation-Only Changes

When reviewing PRs that only update documentation (no code changes):

### Verification Steps

1. **Accuracy** — Does it reflect current code behavior?
   - Run examples mentally through current code
   - Check for any recent code changes that affected the docs
   - Verify API examples match actual endpoints

2. **Completeness** — Are all related topics covered?
   - Are prerequisites mentioned?
   - Are related links provided?
   - Are edge cases documented?

3. **Clarity** — Is it understandable to new developers?
   - Can a new dev follow the steps successfully?
   - Are technical terms explained or linked to glossary?
   - Are assumptions about reader knowledge made clear?

4. **Consistency** — Does it match existing style/format?
   - Does it follow the same structure as similar docs?
   - Is terminology consistent with existing docs?
   - Are code examples consistent with existing examples?

5. **Quality Checks** — Did author run automated validation?
   - [ ] `bash scripts/lint-docs.sh` passed
   - [ ] `python3 scripts/validate-links.py --no-external` passed
   - [ ] `python3 scripts/validate-examples.py` passed

### Rejection Criteria for Docs-Only

- ❌ Inaccurate information (doesn't match current code)
- ❌ Broken links to non-existent files/sections
- ❌ Code examples with syntax errors
- ❌ Hardcoded secrets/credentials in examples
- ❌ Inconsistent with existing documentation style
- ❌ Pre-commit hook failures

---

## How to Use This Checklist

### For Code Reviewers

1. Determine PR type: **Code Change** or **Docs-Only**
2. Go to appropriate section above (1 or 5)
3. Review each checklist item
4. Provide specific feedback if items are missing
5. Use "Request Changes" if major items unchecked
6. Use "Comment" if minor improvements suggested
7. Use "Approve" only when all items verified ✅

### For PR Authors

1. **Before creating PR**: Review this checklist
2. **Before requesting review**: Verify all items
3. **If reviewer requests changes**: Update documentation and re-request review
4. **When approved**: Merge with confidence that documentation is complete

---

## Template for Reviewers

Copy and paste this into PR review comments:

```markdown
## Documentation Review

**PR Type**: [ ] Code Change [ ] Docs-Only

### Coverage
- [ ] All code changes documented
- [ ] Examples match current code
- [ ] Links are valid

### Quality
- [ ] Examples are accurate
- [ ] Documentation is clear
- [ ] Completeness verified

### Consistency
- [ ] Follows existing style
- [ ] Terminology consistent
- [ ] Cross-links included

### Automated Checks
- [ ] Lint passed
- [ ] Link validation passed
- [ ] Example validation passed

**Status**: [ ] Approved [ ] Changes Requested [ ] Comment
```

---

## FAQ

**Q: What if the PR only changes one thing, like a typo in API response?**  
A: Still check if ANY documentation references that response format. Update if it does.

**Q: What if the code change is internal and users won't see it?**  
A: If developers might benefit from knowing about it (optimization, new pattern), document it. If it's purely internal refactoring with zero user impact, documentation may not be needed.

**Q: What if the PR author says "I'll document it in a follow-up PR"?**  
A: Request documentation before merge. Follow-up PRs for documentation rarely happen. Set the expectation upfront.

**Q: What if there's disagreement about whether something needs documentation?**  
A: Default to "document it." It's easier to deprecate overly-comprehensive documentation than to retrofund missing docs.

**Q: Can I suggest documentation improvements in the review?**  
A: Yes! But distinguish between:
- **Must have** (blocking) — Use "Request Changes"
- **Should have** (nice to have) — Use "Comment"

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-02-20 | Initial documentation review checklist created | AI Whisperers |
