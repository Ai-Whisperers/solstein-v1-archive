# Automated Docs And AST Expansion Plan

## Purpose

Solstein is too large and too irregular to rely on repeated full-file reading as the default way to understand pipeline behavior. The goal of this plan is to widen the tokenless and semi-tokenless surfaces of the repo so future work can query contracts, structures, and invariants directly instead of re-reading large volumes of source and drift-prone prose.

This is not a generic docs plan. It is a codebase-reading efficiency plan.

## What We Already Have

- `basedpyright` in strict mode with a checked-in baseline
- `ast-grep` with tested structural rules
- `mkdocstrings` + `Griffe` strict docs slice
- custom CI scripts in `scripts/ci/`
- TypeScript contracts package in `tooling/contracts-ts/`

## Current Limitation

The current generated-doc system is still too narrow:

- generated Python reference only covers package-addressable modules that Griffe can resolve cleanly
- several high-value folders are still not package-addressable enough for the same workflow
- most docs are still hand-written, not derived from AST, type metadata, or schema contracts
- many existing docs are broad and historical, which makes them expensive to re-read and poor as operational references

## What Will Save Tokens

The biggest token savings will not come from “more markdown”. They will come from machine-derived, queryable artifacts that compress the codebase into stable indexes.

The most useful artifacts are:

1. module manifests
2. schema inventories
3. pipeline node maps
4. external integration contract indexes
5. AST rule catalogs
6. typed boundary registries
7. import/dependency summaries

These are the documents and indexes that let an agent answer:

- what enters this boundary?
- what leaves it?
- what failures are explicit vs implicit?
- what schema owns this payload?
- what modules are safe to trust as canonical?
- what invariants are already enforced by CI?

without having to open ten files first.

## Expansion Principles

1. Generate what is structural.
2. Curate what is architectural or business-rationale-heavy.
3. Never let generated docs pretend to cover areas with unresolved package/layout debt.
4. Every new generated artifact must come with a blocking or semi-blocking freshness check.
5. Prefer indexes over narratives when the goal is codebase navigation.

## Where To Expand First

### Tier 1: Immediate High-Value Expansion

These are the fastest wins because they map directly to current pipeline risk and current strict gates.

#### 1. Pipeline Boundary Registry

Create a generated registry for critical nodes:

- `worker`
- `data/unified`
- `infrastructure/connectors`
- `api/routers`
- `api/schemas`

For each node, capture:

- input type or payload boundary
- output type or payload boundary
- exception model
- cache usage
- persistence side effects
- current tests covering it
- current AST rules touching it

This should be generated from AST and type inspection plus a small layer of curated metadata.

#### 2. Schema Ownership Map

Generate a repo-wide index of:

- Pydantic models
- dataclasses used as contracts
- SQLAlchemy ORM models
- TypeScript `zod` schemas

For each schema, capture:

- module path
- schema name
- primary responsibility
- inbound/outbound boundary
- related tests
- related audit files

This becomes the shortest path to understanding “what schema should own this payload”.

#### 3. AST Rule Catalog

Generate docs from `tooling/ast-grep/rules/` and `scripts/ci/` into a single reference page:

- rule id
- why it exists
- related issue/audit id
- whether it is blocking
- examples of accepted and rejected patterns

This prevents rule drift and gives future agents a compact explanation of what structural debt is already guarded.

#### 4. External Integration Index

Keep the hand-written provider docs, but add a generated top-level index that summarizes:

- provider name
- authoritative docs URL
- `llms.txt` availability
- repo availability
- MCP availability
- connector modules in Solstein
- wrapper risk level
- contract status: live, drifted, heuristic, dormant

This should be a compact machine-readable table that agents can read first before opening long provider docs.

### Tier 2: Structural Expansion After Small Package Cleanup

These give strong value but first require packaging and layout cleanup.

#### 5. Generated API Reference For `analytics`, `data`, and `domain`

Current blockers:

- `src/solstein/analytics`
- `src/solstein/data`
- `src/solstein/domain`

are not uniformly package-addressable for the current `Griffe` flow.

The fix is not “write more docs”. The fix is:

- add the missing package markers where appropriate
- avoid ambiguous or duplicate model/module naming
- make importable subtrees explicit and stable

Once that is done, expand `PYTHON_API_REFERENCE.md` to include:

- scoring
- classification
- unified enrichment
- domain models
- evidence models
- export boundaries

#### 6. Import And Dependency Maps

Generate compact indexes for:

- module import graph
- cycle hotspots
- top-level dependency clusters
- critical-path modules by fan-in/fan-out

This is much cheaper than repeatedly re-reading import trees during audits.

#### 7. Connector Contract Surface Maps

Generate per-connector summaries from AST and type metadata:

- connector class
- async/sync entrypoints
- env vars used
- output fact types
- shared payload schema if any
- fallback paths
- known caveats

This is the shortest route to “what does this integration actually do in our code”.

### Tier 3: Deep Query Surfaces

These are the highest leverage long-term, but should only be built after Tier 1 and Tier 2 are stable.

#### 8. Symbol-Level Search Manifests

Generate machine-readable symbol manifests for:

- classes
- functions
- validators
- routers
- tasks
- schemas

This can support tokenless semantic lookup and future linting/retrieval layers without needing a vector step first.

#### 9. Codemod Opportunity Registry

Use AST scans plus CI findings to generate a registry of:

- duplicated anti-patterns
- repeated exception handling shapes
- weakly typed dict boundaries
- stale compatibility shims

This gives a map of where `LibCST` codemods should be applied instead of one-off hand fixes.

#### 10. Generated Release-Critical Surface

Create a compact generated view of the modules and schemas that can directly break:

- scoring
- enrichment
- refresh connectors
- API batch responses
- worker persistence
- evidence storage

This should become the first thing an agent reads before touching core pipeline logic.

## What Should Stay Curated

Do not try to auto-generate these fully:

- business rationale
- scoring methodology rationale
- provider caveat narratives
- architecture decisions
- migration reasoning

These should be short, curated overlays that link into generated indexes underneath.

## Package-Structure Work Needed First

The following directories currently weaken automated docs expansion because they are not consistently package-addressable:

- `src/solstein/analytics`
- `src/solstein/data`
- `src/solstein/domain`
- `src/solstein/application`
- `src/solstein/config`
- `src/solstein/intelligence`
- `src/solstein/monitoring`
- `src/solstein/security`
- `src/solstein/tenant`
- `src/solstein/utils`

This does not mean “add `__init__.py` everywhere blindly”.

It means:

1. decide which directories are canonical public package surfaces
2. add package markers only where the import model should be stable
3. avoid papering over duplicate or transitional module layouts

## Gates We Should Add

### Gate A: Generated Docs Freshness

Add a non-interactive generator script and fail CI if generated docs are stale.

Targets:

- schema inventory
- AST rule catalog
- pipeline boundary registry
- Python API reference subset

### Gate B: Package-Addressability Audit

Add a CI script that checks whether designated “reference-exported” packages remain importable and Griffe-resolvable.

### Gate C: Contract Drift Gate

Fail if a critical router or worker boundary changes without:

- Python schema update
- TS contract update
- regression or schema test update
- generated reference refresh

### Gate D: AST Rule Coverage Gate

For every new structural issue fixed in an audit:

- require a rule or an explicit justification for why no rule is possible

### Gate E: Boundary Manifest Gate

Fail if critical boundary registries are missing coverage for:

- workers
- refresh connectors
- batch enrichment
- scoring
- evidence persistence

## Concrete Tooling To Add

### 1. `scripts/docs/generate_schema_inventory.py`

Generate:

- `docs/reference/generated/SCHEMA_REGISTRY.md`
- machine-readable JSON alongside it

Sources:

- Python AST
- `pydantic` model inspection
- `zod` schema file scanning
- ORM class discovery

### 2. `scripts/docs/generate_pipeline_registry.py`

Generate:

- `docs/reference/generated/PIPELINE_BOUNDARY_REGISTRY.md`

Sources:

- routers
- Celery tasks
- enrichment functions
- refresh connectors
- repositories

### 3. `scripts/docs/generate_ast_rule_catalog.py`

Generate:

- `docs/reference/generated/AST_RULE_CATALOG.md`

Sources:

- `tooling/ast-grep/rules`
- `tooling/ast-grep/rule-tests`
- selected `scripts/ci` checks

### 4. `scripts/docs/generate_module_manifest.py`

Generate per-package manifests for the packages that become reference-approved.

### 5. `scripts/docs/check_generated_docs_fresh.py`

Blocking CI check that diffs generated outputs.

## Recommended Rollout Order

### Phase 1

- schema registry
- AST rule catalog
- generated docs freshness gate

### Phase 2

- pipeline boundary registry
- release-critical surface map
- contract drift gate

### Phase 3

- package-addressability cleanup for `analytics`, `data`, `domain`
- expand mkdocstrings coverage

### Phase 4

- import/dependency manifests
- codemod opportunity registry
- deeper symbol-level manifests

## How This Reduces Slop

This reduces slop in three ways:

1. fewer repeated broad reads of historical docs
2. less manual inference about what a module or boundary does
3. more enforcement that the code, schemas, AST rules, and docs move together

The result should be:

- fewer token-expensive exploration loops
- less context drift between agents
- faster identification of canonical modules
- stricter alignment between runtime behavior and documentation

## Immediate Next Step

The next concrete implementation should be:

1. add `scripts/docs/generate_ast_rule_catalog.py`
2. add `scripts/docs/generate_schema_inventory.py`
3. create `docs/reference/generated/`
4. wire a `docs-generated-check` target into `Makefile`

That is the smallest step that meaningfully widens tokenless reading without requiring a large refactor first.
