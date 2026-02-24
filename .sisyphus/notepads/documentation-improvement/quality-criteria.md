# Documentation Quality Criteria & Acceptance Standards

**Version**: 1.0  
**Date**: February 24, 2026  
**Purpose**: Define measurable criteria for "complete and professional" documentation  
**Applies to**: All Solstein project documentation (README, guides, API docs, architecture docs, etc.)

---

## Executive Summary

This document establishes objective, measurable standards for documentation quality. It provides:
- Clear definitions of "complete" and "professional"
- Quantifiable metrics for verification
- Checklists for systematic review
- Quality gates for phased improvement

**Target Audiences**:
- PE firms (investors evaluating the platform)
- Technical teams (developers implementing features)
- Operators (devops, support, maintenance)

---

## 1. COMPLETENESS CRITERIA

### 1.1 Mandatory Information Elements

For any document to be considered **complete**, it MUST contain:

| Element | Requirement | Verification Method |
|---------|-------------|---------------------|
| **Purpose Statement** | Single sentence explaining why document exists | Check: First paragraph contains "This document..." or clear purpose statement |
| **Audience Definition** | Explicit statement of who should read this | Check: "For [audience]" or "Prerequisites: [knowledge required]" |
| **Table of Contents** | For documents >500 words | Check: TOC present with working anchors |
| **Quick Start** | Minimal steps to get value within 5 minutes | Check: "Quick Start" or "Getting Started" section exists |
| **Key Concepts** | Definitions of domain-specific terms | Check: Glossary or inline definitions for non-obvious terms |
| **Examples** | At least one concrete, copy-paste ready example | Check: Code blocks or usage examples present |
| **Troubleshooting** | Common issues and solutions | Check: "Troubleshooting", "FAQ", or "Common Issues" section |
| **Related Resources** | Links to next steps or related docs | Check: "See Also" or "Next Steps" section with working links |
| **Last Updated** | Date of last meaningful update | Check: Footer or header with date/version |

### 1.2 Document-Type Specific Requirements

#### README.md
- [ ] Project description (1-2 sentences)
- [ ] Installation instructions
- [ ] Quick start example
- [ ] Feature list (3-5 key features)
- [ ] Architecture overview or link
- [ ] Link to full documentation
- [ ] License information
- [ ] Contact/support information

#### API Reference
- [ ] Authentication requirements
- [ ] Base URL and environment info
- [ ] Every endpoint documented:
  - Method + Path
  - Request parameters (required/optional)
  - Request body schema
  - Response schema (all status codes)
  - Error response examples
- [ ] Rate limiting info
- [ ] SDK/client library links

#### Developer Guides
- [ ] Prerequisites and dependencies
- [ ] Step-by-step setup instructions
- [ ] Development workflow
- [ ] Testing instructions
- [ ] Contribution guidelines (if applicable)
- [ ] Environment configuration

#### Architecture Documentation
- [ ] System context diagram
- [ ] Component descriptions
- [ ] Data flow explanation
- [ ] Decision rationale (ADRs)
- [ ] Technology stack with versions
- [ ] Deployment architecture

#### Operations Guides
- [ ] Infrastructure requirements
- [ ] Deployment procedures
- [ ] Monitoring and alerting setup
- [ ] Backup and recovery procedures
- [ ] Incident response playbooks
- [ ] Rollback procedures

### 1.3 Coverage Metrics

| Metric | Minimum Acceptable | Target | Professional Standard |
|--------|-------------------|--------|----------------------|
| **Topic Coverage** | 70% of expected sections present | 85% | 95%+ |
| **Code Example Coverage** | 1 example per 500 words | 1 per 300 words | 1 per 200 words |
| **Link Validity** | 80% of internal links work | 90% | 95%+ |
| **Cross-Reference Coverage** | Links to 2+ related docs | Links to 3+ related docs | Links to all related docs |

---

## 2. PROFESSIONAL CRITERIA

### 2.1 Writing Quality Standards

#### Clarity
- **Requirement**: 8th-10th grade reading level (Flesch-Kincaid)
- **Verification**: Run through readability checker
- **Acceptance**: Score ≤ 10.0 on Flesch-Kincaid Grade Level

#### Conciseness
- **Requirement**: No redundant sentences, no filler words
- **Verification**: Manual review + automated checks
- **Acceptance**: < 5% of sentences can be shortened by 20%+ without losing meaning

#### Consistency
- **Requirement**: Same terms used throughout, consistent formatting
- **Verification**: Glossary adherence check
- **Acceptance**: No undefined jargon, consistent capitalization of proper nouns

#### Accuracy
- **Requirement**: All technical claims verifiable, code examples runnable
- **Verification**: Execute all code examples, verify technical claims
- **Acceptance**: 100% of code examples run without errors, all claims have sources

### 2.2 Tone and Voice Standards

| Aspect | Requirement | Example |
|--------|-------------|---------|
| **Formality** | Professional but accessible | "The API returns" not "The API spits out" |
| **Active Voice** | Prefer active (70%+) | "Configure the file" not "The file should be configured" |
| **Direct Address** | Speak to reader directly | "You can configure" not "One can configure" |
| **Positive Framing** | State what TO do, not what NOT to do | "Use 256-bit encryption" not "Don't use weak encryption" |
| **Confidence** | State facts definitively | "The endpoint returns" not "The endpoint should return" |

**Tone Verification**:
- Check: Run `proselint` or similar tool
- Acceptance: < 5 instances of passive voice per 1000 words
- Acceptance: 0 instances of hedging language ("maybe", "perhaps", "might") in instructional content

### 2.3 Formatting and Presentation

#### Visual Hierarchy
- [ ] H1 for document title only
- [ ] H2 for major sections
- [ ] H3 for subsections
- [ ] H4+ rarely used (consider restructuring if needed)
- [ ] Consistent heading capitalization (Title Case for H1-H2, Sentence case for H3+)

#### Code Formatting
- [ ] All code blocks have language identifier
- [ ] Syntax highlighting renders correctly
- [ ] Line numbers for long examples (>10 lines)
- [ ] Comments explain non-obvious code
- [ ] Placeholders clearly marked (e.g., `<YOUR_API_KEY>`)

#### Lists and Tables
- [ ] Use tables for structured comparisons (3+ related items)
- [ ] Use bullet lists for unordered items
- [ ] Use numbered lists for sequential steps
- [ ] Keep list items parallel (same grammatical structure)
- [ ] Maximum 7 items per list (split if longer)

#### Visual Elements
- [ ] Diagrams have captions
- [ ] Images have alt text
- [ ] Screenshots show current UI (dated within 3 months)
- [ ] Diagrams use consistent notation (UML, C4, etc.)

### 2.4 Professional Polish Metrics

| Metric | Minimum | Target | Professional |
|--------|---------|--------|--------------|
| **Spelling Errors** | < 5 per 1000 words | < 2 per 1000 words | 0 |
| **Grammar Errors** | < 3 per 1000 words | < 1 per 1000 words | 0 |
| **Formatting Consistency** | 90% consistent | 95% consistent | 98%+ consistent |
| **Broken Links** | < 5% | < 2% | 0% |
| **Outdated Information** | < 10% | < 5% | < 2% |

---

## 3. MEASURABLE QUALITY METRICS

### 3.1 Automated Metrics

These can be checked automatically:

| Metric | Tool/Method | Threshold | Weight |
|--------|-------------|-----------|--------|
| **Readability Score** | Flesch Reading Ease | > 50 | 10% |
| **Grade Level** | Flesch-Kincaid | ≤ 10.0 | 10% |
| **Sentence Length** | Average words per sentence | < 20 | 5% |
| **Paragraph Length** | Average sentences per paragraph | < 5 | 5% |
| **Spelling Errors** | `aspell` or `codespell` | 0 | 15% |
| **Link Validity** | `markdown-link-check` | 95%+ valid | 15% |
| **Code Example Validity** | Execute in CI | 100% | 20% |
| **Heading Hierarchy** | `markdownlint` | No skips | 10% |
| **Line Length** | `markdownlint` | ≤ 120 chars | 5% |
| **Trailing Whitespace** | `markdownlint` | 0 | 5% |

**Quality Score Calculation**:
```
Quality Score = Σ(metric_value × weight)
```

| Score Range | Rating | Action |
|-------------|--------|--------|
| 90-100 | Excellent | Approved |
| 80-89 | Good | Minor revisions |
| 70-79 | Acceptable | Revisions required |
| 60-69 | Needs Work | Significant rework |
| < 60 | Unacceptable | Rewrite required |

### 3.2 Manual Review Metrics

These require human judgment:

| Metric | Criteria | Scoring |
|--------|----------|---------|
| **Accuracy** | Technical correctness | 0-10 scale |
| **Completeness** | Coverage of topic | 0-10 scale |
| **Clarity** | Ease of understanding | 0-10 scale |
| **Organization** | Logical flow | 0-10 scale |
| **Examples Quality** | Helpfulness of examples | 0-10 scale |
| **Visual Appeal** | Professional appearance | 0-10 scale |

**Reviewer Score Calculation**:
```
Reviewer Score = Average of all metrics × 10
```

### 3.3 Example Coverage Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Example Density** | Code blocks / Total word count | > 0.15 |
| **Example Diversity** | Different use cases covered | ≥ 3 per feature |
| **Example Freshness** | Last verified date | < 3 months |
| **Example Success Rate** | % of examples that run | 100% |

---

## 4. ACCEPTANCE CHECKLIST

### 4.1 Pre-Review Checklist (Author)

Before submitting documentation for review, the author MUST:

- [ ] Spell-check the entire document
- [ ] Verify all links work
- [ ] Run all code examples
- [ ] Check formatting renders correctly in target viewer
- [ ] Verify last updated date is current
- [ ] Review against this quality criteria document
- [ ] Complete self-assessment (see below)

### 4.2 Self-Assessment Form

**Document**: _________________  
**Author**: _________________  
**Date**: _________________  

#### Completeness (Rate 1-5)
- [ ] Purpose clear: ___
- [ ] Audience defined: ___
- [ ] Prerequisites listed: ___
- [ ] All topics covered: ___
- [ ] Examples included: ___
- [ ] Troubleshooting present: ___
- [ ] Related links provided: ___

**Completeness Score**: ___/35

#### Professionalism (Rate 1-5)
- [ ] Grammar and spelling: ___
- [ ] Consistent tone: ___
- [ ] Proper formatting: ___
- [ ] Clear organization: ___
- [ ] Professional appearance: ___

**Professionalism Score**: ___/25

#### Accuracy (Rate 1-5)
- [ ] Technical accuracy: ___
- [ ] Code examples run: ___
- [ ] Links valid: ___
- [ ] Information current: ___

**Accuracy Score**: ___/20

**TOTAL SELF-ASSESSMENT**: ___/80

**Minimum to proceed to review: 60/80**

### 4.3 Reviewer Checklist

**Reviewer**: _________________  
**Date**: _________________  

#### Content Review
- [ ] All claims verifiable
- [ ] Examples are accurate and runnable
- [ ] No outdated information
- [ ] No missing critical information
- [ ] Appropriate depth for audience

#### Style Review
- [ ] Consistent with style guide
- [ ] Appropriate tone for audience
- [ ] Clear and concise writing
- [ ] Proper grammar and spelling
- [ ] Consistent terminology

#### Technical Review
- [ ] Code examples work as documented
- [ ] API calls return expected responses
- [ ] Configuration examples are valid
- [ ] Commands execute without errors
- [ ] Environment requirements are accurate

#### Structural Review
- [ ] Logical organization
- [ ] Clear navigation
- [ ] Proper heading hierarchy
- [ ] Working internal links
- [ ] Working external links

**APPROVAL STATUS**:
- [ ] Approved as-is
- [ ] Approved with minor revisions
- [ ] Requires revisions (specify below)
- [ ] Rejected (specify below)

**Required Revisions**:
_________________________________
_________________________________
_________________________________

---

## 5. VERIFICATION PROCEDURES

### 5.1 Automated Verification (CI/CD)

```yaml
# Example GitHub Actions workflow
name: Documentation Quality Check
on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check spelling
        uses: codespell-project/actions-codespell@v2
        
      - name: Check links
        uses: lycheeverse/lychee-action@v1
        
      - name: Check markdown
        uses: DavidAnson/markdownlint-cli2-action@v11
        
      - name: Validate code examples
        run: ./scripts/verify-examples.sh
```

### 5.2 Manual Verification Process

**Step 1: Initial Review (15 min)**
1. Read document start to finish
2. Check structure and organization
3. Note obvious issues

**Step 2: Technical Verification (30 min)**
1. Execute all code examples
2. Verify all API calls
3. Check all commands
4. Validate configurations

**Step 3: Style Review (15 min)**
1. Check against style guide
2. Verify tone consistency
3. Check formatting

**Step 4: Final Verification (10 min)**
1. Re-read changed sections
2. Confirm all checklist items
3. Document findings

### 5.3 Stakeholder Verification

For enterprise-grade documentation:

1. **Subject Matter Expert Review**
   - Technical accuracy verified by SME
   - Sign-off required before publication

2. **Editorial Review**
   - Professional writer reviews clarity
   - Style consistency check

3. **Stakeholder Approval**
   - Business owner approves content
   - Legal review if required
   - Final sign-off

---

## 6. QUALITY GATES BY WAVE

### Wave 1: Foundation & Structure

**Gate W1.1: README Enhancement**
- [ ] Completeness: 8/9 mandatory elements present
- [ ] Professionalism: Self-assessment ≥ 60/80
- [ ] Accuracy: All code examples verified
- [ ] Links: 90%+ internal links valid

**Gate W1.2: Style Guide Completion**
- [ ] All style rules documented
- [ ] Examples for each rule type
- [ ] Approved by 2+ reviewers

**Gate W1.3: Structure Audit**
- [ ] All docs have proper structure
- [ ] TOC present where required
- [ ] Navigation between docs working

### Wave 2: Content Enhancement

**Gate W2.1: Technical Accuracy**
- [ ] 100% of code examples execute successfully
- [ ] All API documentation matches implementation
- [ ] All configurations validated

**Gate W2.2: Completeness Review**
- [ ] All documents meet 70% topic coverage
- [ ] All required sections present
- [ ] Examples added where missing

**Gate W2.3: Cross-Reference Check**
- [ ] All internal links valid
- [ ] Related documents linked
- [ ] Navigation paths clear

### Wave 3: Professional Polish

**Gate W3.1: Writing Quality**
- [ ] Grade level ≤ 10.0
- [ ] Spelling errors < 2 per 1000 words
- [ ] Grammar errors < 1 per 1000 words
- [ ] Active voice ≥ 70%

**Gate W3.2: Visual Consistency**
- [ ] Formatting consistent across all docs
- [ ] Visual elements captioned
- [ ] Diagrams use consistent notation

**Gate W3.3: Stakeholder Approval**
- [ ] SME sign-off on technical content
- [ ] Editorial review complete
- [ ] Business owner approval

### Wave 4: Advanced Features

**Gate W4.1: Interactive Elements**
- [ ] Search functionality working
- [ ] Navigation aids implemented
- [ ] Feedback mechanisms in place

**Gate W4.2: Accessibility**
- [ ] Alt text on all images
- [ ] Color contrast compliant
- [ ] Keyboard navigation works

**Gate W4.3: Final Certification**
- [ ] Quality score ≥ 90/100
- [ ] All quality gates passed
- [ ] Stakeholder final approval

---

## 7. EXCEPTIONS AND EDGE CASES

### 7.1 Allowable Exceptions

| Exception | Justification | Approval Required |
|-----------|---------------|-------------------|
| Intentional jargon | Domain-specific terminology for expert audience | Tech Lead |
| Complex examples | Advanced use cases require complexity | SME |
| Minimal README | Simple utility with self-evident use | Documentation Lead |
| Outdated screenshots | Pending UI update | Product Manager |

### 7.2 Handling Legacy Documentation

For documentation that cannot be brought to full standard immediately:

1. **Mark with Disclaimer**:
   ```markdown
   > ⚠️ **Documentation Status**: This document is being updated. 
   > Last comprehensive review: [DATE]. Some information may be outdated.
   ```

2. **Prioritize Updates**:
   - Critical path documentation first
   - User-facing before internal
   - New features before legacy

3. **Gradual Compliance**:
   - Wave 1: Add missing sections
   - Wave 2: Fix technical accuracy
   - Wave 3: Improve writing quality
   - Wave 4: Achieve full standard

---

## 8. APPENDICES

### Appendix A: Tools Reference

| Tool | Purpose | Command |
|------|---------|---------|
| `markdownlint` | Format checking | `markdownlint **/*.md` |
| `codespell` | Spell checking | `codespell docs/` |
| `lychee` | Link checking | `lychee docs/**/*.md` |
| `vale` | Style checking | `vale docs/` |
| `readable` | Readability | Various online tools |

### Appendix B: Scoring Worksheet

**Document**: _________________  
**Evaluator**: _________________  

| Category | Metric | Score | Weight | Weighted |
|----------|--------|-------|--------|----------|
| **Completeness** | Topic Coverage | /10 | 0.20 | |
| | Example Coverage | /10 | 0.10 | |
| | Link Validity | /10 | 0.05 | |
| **Professionalism** | Writing Quality | /10 | 0.15 | |
| | Formatting | /10 | 0.10 | |
| | Tone Consistency | /10 | 0.05 | |
| **Accuracy** | Technical Correctness | /10 | 0.20 | |
| | Example Validity | /10 | 0.10 | |
| | Currency | /10 | 0.05 | |
| **TOTAL** | | | 1.00 | /10 |

**Rating**:
- 9.0-10.0: Exceptional
- 8.0-8.9: Excellent
- 7.0-7.9: Good
- 6.0-6.9: Acceptable
- < 6.0: Needs Improvement

### Appendix C: Review Sign-Off

**Document**: _________________  
**Version**: _________________  

| Reviewer | Role | Date | Decision | Signature |
|----------|------|------|----------|-----------|
| | Author | | Self-assessment: ___/80 | |
| | Tech Lead | | Technical Review: | |
| | Documentation Lead | | Style Review: | |
| | SME | | Accuracy Review: | |
| | Product Owner | | Final Approval: | |

**Final Status**: [ ] Approved [ ] Approved with Revisions [ ] Rejected

---

**Document Control**:
- **Owner**: Documentation Team
- **Review Cycle**: Quarterly
- **Next Review**: May 24, 2026
- **Change Log**: See below

**Change Log**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-24 | Quality Team | Initial release |
