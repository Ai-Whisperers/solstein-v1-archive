# 📁 Solstein Repository Cleanup & Organization Plan

## Current State Analysis

### Repository Stats
- **Total Size**: 9.3 GB (7.8 GB is venv/)
- **Root Files**: 33 (too many)
- **Root Scripts**: 2 Python + 3 Shell
- **Root Config Files**: 4 JSON + 3 YAML/YML + 1 INI
- **Root Markdown Files**: 7 (scattered)
- **Root Evidence/Reports**: 3 files

### Root Directory Issues

| Issue | Count | Severity |
|-------|-------|----------|
| **Scripts in root** | 5 | 🔴 HIGH |
| **Config files scattered** | 8 | 🟡 MEDIUM |
| **Markdown docs** | 7 | 🟡 MEDIUM |
| **Phase/Completion reports** | 2 | 🟡 MEDIUM |
| **Evidence files** | 1 | 🟡 MEDIUM |

---

## Cleanup Strategy

### Phase 1: Move Scripts (High Priority)

**Move to `scripts/`:**
```
discover_all_companies.py           → scripts/market-discovery/discover_all_companies.py
enrich_all_companies.py             → scripts/enrichment/enrich_all_companies.py
run_eneve_complete_flow.sh          → scripts/workflows/run_complete_flow.sh
start_api_server.sh                 → scripts/services/start_api_server.sh
start_celery_workers.sh             → scripts/services/start_celery_workers.sh
```

**Status**: These are utility/automation scripts that belong in scripts/ with proper subdirectories

---

### Phase 2: Consolidate Config Files (Medium Priority)

**Move to `config/` and consolidate:**

#### Database/ORM
- `alembic.ini` → `config/database/alembic.ini`
- `.env.example` → `config/secrets/env.example`

#### Development/Tooling
- `pyrightconfig.json` → `config/tools/pyrightconfig.json`
- `.yamllint` → `config/tools/yamllint.yaml`
- `.pre-commit-config.yaml` → `config/tools/pre-commit.yaml`

#### Documentation
- `mkdocs.yml` → `docs/mkdocs.yml` (keep in docs/)

#### Docker
- `.dockerignore` → `docker/.dockerignore` (move with Dockerfile)

#### Git
- `.gitignore` → KEEP in root (Git standard)
- `.env.example` → KEEP accessible (setup reference)

**Root Config After Cleanup:**
```
KEEP IN ROOT:
- .gitignore (Git standard)
- .env.example (Setup reference)
- pyproject.toml (Python standard)
- pyproject.toml (Python standard)
- requirements-lock.txt (Python standard)
- Makefile (Project standard)
```

---

### Phase 3: Archive Documentation (Medium Priority)

**Move to `.sisyphus/archive/completed-reports/`:**
```
IMPLEMENTATION_COMPLETE.md               → .sisyphus/archive/completed-reports/
PHASE_10_11_12_COMPLETION_REPORT.md     → .sisyphus/archive/completed-reports/
task-9-curl-verification.txt            → .sisyphus/evidence/  (keep with evidence)
```

**Keep in Root:**
```
README.md                   (Project overview)
CONTRIBUTING.md             (Contribution guide)
SECURITY.md                 (Security policy)
CHANGELOG.md                (Version history)
LICENSE                     (License)
```

---

### Phase 4: Data Files (Low Priority)

**Move non-essential data to `data/reference/`:**
```
envision_digital_profile.json   → data/reference/envision_digital_profile.json
discover_all_companies.py       → scripts/ first, then check if output data should be archived
enrich_all_companies.py         → scripts/ first, then check if output data should be archived
```

---

## Target Structure (After Cleanup)

```
solstein/
├── config/                          # ← NEW: All config files
│   ├── database/
│   │   └── alembic.ini
│   ├── tools/
│   │   ├── pyrightconfig.json
│   │   ├── yamllint.yaml
│   │   └── pre-commit.yaml
│   └── secrets/
│       └── env.example
├── scripts/                         # ← REORGANIZED: Better structure
│   ├── market-discovery/
│   │   └── discover_all_companies.py
│   ├── enrichment/
│   │   └── enrich_all_companies.py
│   ├── workflows/
│   │   └── run_complete_flow.sh
│   ├── services/
│   │   ├── start_api_server.sh
│   │   └── start_celery_workers.sh
│   └── ... (21 existing scripts)
├── docs/                            # ← Unchanged
│   ├── mkdocs.yml
│   └── ... (all documentation)
├── src/                             # ← Unchanged
├── tests/                           # ← Unchanged
├── data/                            # ← Moved reference data
│   ├── reference/
│   │   └── envision_digital_profile.json
│   └── ... (existing)
├── .sisyphus/
│   ├── archive/
│   │   └── completed-reports/       # ← NEW: Phase reports
│   │       ├── IMPLEMENTATION_COMPLETE.md
│   │       └── PHASE_10_11_12_COMPLETION_REPORT.md
│   ├── evidence/
│   │   └── ... (all evidence files)
│   ├── notepads/
│   └── plans/
├── ROOT (Clean, 8-10 files only)
│   ├── README.md                    # ← Keep
│   ├── CONTRIBUTING.md              # ← Keep
│   ├── SECURITY.md                  # ← Keep
│   ├── CHANGELOG.md                 # ← Keep
│   ├── LICENSE                      # ← Keep
│   ├── Makefile                     # ← Keep
│   ├── pyproject.toml               # ← Keep (Python standard)
│   ├── requirements-lock.txt        # ← Keep (Python standard)
│   ├── .env.example                 # ← Keep (setup reference)
│   ├── .gitignore                   # ← Keep (Git standard)
│   └── mkdocs.yml                   # ← OR move to docs/
├── docker/                          # ← Unchanged
├── alembic/                         # ← Unchanged (alembic init dir)
└── ... (other dirs)
```

---

## Benefits of This Cleanup

| Benefit | Impact |
|---------|--------|
| **Reduced root clutter** | From 33 → 8-10 files (70% reduction) |
| **Better discoverability** | Scripts in scripts/, configs in config/ |
| **Cleaner git history** | Phase reports archived, not in root |
| **Maintainability** | Logical grouping, easier to find things |
| **Onboarding** | New devs see clean root, know where things are |
| **CI/CD clarity** | Clear separation of tool config from app |

---

## Implementation Steps

### Step 1: Create directories
```bash
mkdir -p config/{database,tools,secrets}
mkdir -p scripts/{market-discovery,enrichment,workflows,services}
mkdir -p .sisyphus/archive/completed-reports
mkdir -p data/reference
```

### Step 2: Move config files
```bash
# Database config
mv alembic.ini config/database/

# Tool configs
mv pyrightconfig.json config/tools/
mv .yamllint config/tools/yamllint.yaml
mv .pre-commit-config.yaml config/tools/

# Secrets/env
mv .env.example config/secrets/
```

### Step 3: Move scripts
```bash
mv discover_all_companies.py scripts/market-discovery/
mv enrich_all_companies.py scripts/enrichment/
mv run_eneve_complete_flow.sh scripts/workflows/
mv start_api_server.sh scripts/services/
mv start_celery_workers.sh scripts/services/
```

### Step 4: Archive reports
```bash
mv IMPLEMENTATION_COMPLETE.md .sisyphus/archive/completed-reports/
mv PHASE_10_11_12_COMPLETION_REPORT.md .sisyphus/archive/completed-reports/
```

### Step 5: Move data
```bash
mv envision_digital_profile.json data/reference/
```

### Step 6: Update references
- Update .gitignore if necessary
- Update CI/CD config if they reference these paths
- Update README/scripts if they reference old paths

### Step 7: Commit
```bash
git add -A
git commit -m "chore: reorganize repository structure - move configs to config/, scripts to scripts/, archive completed reports"
```

---

## Risk Assessment

### Low Risk
✅ Moving config files (clearly utilities)  
✅ Moving scripts (clearly tools)  
✅ Archiving completed reports (reference only)

### Medium Risk  
⚠️ Updating references in CI/CD, Makefile, scripts  
⚠️ .env.example location (dev setup reference)

### Mitigation
- Update .gitignore to reflect new paths
- Update Makefile/scripts that reference old paths
- Test: `make`, `./scripts/services/start_api_server.sh`
- Update CI/CD configs (GitHub Actions, etc.)

---

## Quick Wins (Immediate)

**No-Risk improvements (can do right now):**
1. Move phase reports to archive/ (historical docs, not needed in root)
2. Create config/ directory structure (new, doesn't break anything)
3. Add config/ to .gitignore (if different settings needed)

**Then migrate files one batch at a time with updates.**

---

## Questions to Clarify

1. Is `.env.example` used during `make setup`? (If yes, might stay in root)
2. Are there CI/CD configs that hardcode paths to root files?
3. Should `alembic.ini` stay near `alembic/` or move to `config/`?
4. Is `envision_digital_profile.json` a real data file or test fixture?

---

## Estimated Cleanup Time
- **Planning**: ✅ Done
- **Creating directories**: 2 min
- **Moving files**: 5 min
- **Updating references**: 10-15 min
- **Testing**: 5 min
- **Commit & documentation**: 5 min

**Total: ~30-45 minutes**

---

**Status**: Ready to execute on your approval
