# 📁 Documentation Folder Organization

**Last Updated:** February 24, 2026
**Status:** ✅ Organized and Clean

---

## 📂 Directory Structure

```
docs/
├── README.md                          ← Main docs entry point
├── index.md                           ← GitHub Pages index (if hosted)
├── STRUCTURE.md                       ← Repository structure guide
├── QUICK-REFERENCE.md                 ← One-page command cheat sheet
├── GLOSSARY.md                        ← 80+ terms defined
│
├── api/
│   └── reference.md                   ← Complete API documentation
│
├── architecture/
│   ├── decisions.md                   ← 8 Architecture Decision Records
│   ├── layer-boundaries.md            ← Layer compatibility policy
│   ├── modules.md                     ← Module documentation
│   ├── json-to-database-roadmap.md    ← Migration planning
│   └── DATA_SOURCE_WIRING_REFERENCE.md ← Data source configuration
│
├── audits/                            ← Audit reports
│   ├── DATA_PIPELINE_AUDIT_2026-02-23.md
│   ├── NYX_REMOTE_DIFF_ANALYSIS.md    ← Nyx commit diff analysis
│   ├── YAHOO_EXTRACTION_AUDIT.md      ← Yahoo Finance extraction audit
│   └── CODEBASE_AUDIT_REPORT.md       ← Comprehensive codebase audit
│
├── communications/                    ← Team communications
│   ├── phase-1-announcement.md
│   ├── phase-1-quickstart.md
│   └── phase-2-4-specifications.md
│
├── examples/                          ← Code examples by language
│   ├── README.md                      ← Examples index
│   ├── curl/
│   │   └── curl-examples.md           ← Command-line examples
│   ├── javascript/
│   │   └── javascript-client.md       ← JS/TS examples
│   ├── python/
│   │   └── python-client.md           ← Python examples
│   └── scenarios/                     ← Use case scenarios
│
├── guides/                            ← How-to guides
│   ├── ci-cd.md                       ← CI/CD documentation
│   ├── code-conventions.md            ← Coding standards (886 lines)
│   ├── database.md                    ← Database setup (611 lines)
│   ├── data-gathering-stages.md       ← Data pipeline stages
│   ├── developer.md                   ← Developer guide (666 lines)
│   ├── documentation-review.md        ← Doc review checklist
│   ├── documentation-style-guide.md   ← Style guide (805 lines)
│   ├── extending-solstein.md          ← Extension guide (801 lines)
│   ├── operator.md                    ← Operations guide (203 lines)
│   └── troubleshooting.md             ← Troubleshooting (938 lines)
│
├── LORE/                              ← Storytelling & analogies
│   ├── grimoire.md                    ← Metaphors & analogies guide
│   ├── origin.md                      ← Origin story
│   └── the-play.md                    ← Three-entity strategy
│
├── PITCH/                             ← Business & investor docs
│   ├── business-model.md              ← Commercial model
│   ├── case-study.md                  ← 29-company case study
│   ├── executive-brief.md             ← One-page brief
│   └── full-proposal.md               ← Complete proposal
│
├── archive/                           ← Historical documents
│   ├── ANALYSIS.md
│   ├── COMPREHENSIVE_TODO_AND_GAP_ANALYSIS.md
│   ├── CRITICAL_ANALYSIS.md
│   ├── REORGANIZATION_SUMMARY.md
│   ├── CI_CD_CURSOR_INTEGRATION_PLAN.md
│   ├── plans/                         ← Implementation plans
│   ├── proposals/                     ← Business proposals
│   ├── root-docs/                     ← Archived root docs
│   └── ...
│
└── assets/                            ← Static assets (images, styles)
    ├── images/
    ├── javascripts/
    └── stylesheets/
```

---

## 📊 Statistics

| Category | Files | Lines | Status |
|----------|-------|-------|--------|
| **Guides** | 10 | 6,000+ | ✅ Complete |
| **API & Architecture** | 6 | 1,500+ | ✅ Complete |
| **Business (PITCH)** | 4 | 800+ | ✅ Complete |
| **Storytelling (LORE)** | 3 | 600+ | ✅ Complete |
| **Examples** | 4+ | 1,500+ | ✅ Complete |
| **Archive** | 20+ | N/A | ✅ Archived |
| **Total** | **46+** | **15,000+** | ✅ **Organized** |

---

## 🎯 Organization Principles

### 1. Clear Separation of Concerns
- **guides/**: How-to documentation for developers and operators
- **api/**: API reference documentation
- **architecture/**: Technical architecture and decisions
- **PITCH/**: Business-facing documentation for investors
- **LORE/**: Storytelling and conceptual documentation
- **examples/**: Runnable code examples
- **archive/**: Historical documents (not part of active docs)

### 2. Consistent Naming
- All files use kebab-case: `my-document.md`
- README.md in each folder serves as index
- No spaces in filenames
- Clear, descriptive names

### 3. Cross-References
- 312 internal links validated
- All links use relative paths
- No broken internal links
- Consistent link text

---

## 🔍 Finding What You Need

### By Role

**Investors / Business Stakeholders:**
1. Start: `docs/README.md`
2. Read: `PITCH/executive-brief.md`
3. Review: `PITCH/case-study.md`
4. Deep dive: `LORE/the-play.md`

**Developers:**
1. Start: `docs/README.md`
2. Setup: `guides/developer.md`
3. Code: `guides/code-conventions.md`
4. API: `api/reference.md`
5. Examples: `examples/README.md`

**Operators:**
1. Start: `docs/README.md`
2. Deploy: `guides/operator.md`
3. Database: `guides/database.md`
4. Troubleshoot: `guides/troubleshooting.md`
5. Quick ref: `QUICK-REFERENCE.md`

**Architects:**
1. Start: `architecture/decisions.md`
2. Layers: `architecture/layer-boundaries.md`
3. Modules: `architecture/modules.md`

---

## ✅ Organization Checklist

- [x] No duplicate directories (audit/audits merged)
- [x] Consistent file naming (kebab-case)
- [x] README.md in each major directory
- [x] Archive folder for historical docs
- [x] Clear separation by audience
- [x] All TODOs updated to reflect completion
- [x] Cross-references validated (312 links)
- [x] Examples organized by language
- [x] Assets separated from content
- [x] No orphaned files

---

## 📋 Maintenance

**Quarterly Reviews:**
- Check for broken external links
- Review archive for outdated files
- Update statistics in this file
- Verify all README.md files are current

**Per-Release Updates:**
- Add new examples for new features
- Update API reference
- Update CHANGELOG
- Review organization structure

---

## 🆘 Need Help?

- **Can't find something?** Check `DOCUMENTATION_INDEX.md`
- **Quick commands?** See `QUICK-REFERENCE.md`
- **Terminology?** Check `GLOSSARY.md`
- **Structure?** See `STRUCTURE.md`

---

*Documentation organized by: Atlas*
*Last organization pass: February 24, 2026*
