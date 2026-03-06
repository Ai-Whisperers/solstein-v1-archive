# EPIC-020 Learnings

> Conventions, patterns, and insights discovered during god function refactoring

---

## Discovered Patterns

### Pattern 1: Pipeline Stage Pattern
Used for `run_market_intelligence` - Extract into stage classes with common interface.

### Pattern 2: Field Mapper Pattern
Used for `_convert_to_domain_company` - Map raw data to domain objects via mapper classes.

### Pattern 3: Strategy Pattern
Used for `_catalog_for_market` - Pluggable discovery strategies.

---

## Code Conventions

### Function Size Targets
- **Ideal:** <50 lines
- **Acceptable:** <100 lines
- **Maximum:** 100 lines (hard limit)

### Refactoring Safety Rules
1. Always maintain backward compatibility
2. Add tests BEFORE refactoring
3. Use feature flags for risky changes
4. Benchmark performance before/after

---

## Gotchas

### Gotcha 1: Deep Nesting
Many god functions have 20+ levels of nesting. Extract early returns and guard clauses.

### Gotcha 2: Shared State
Functions often mutate shared state. Document all side effects.

### Gotcha 3: Exception Handling
293 bare except clauses found. Replace with specific exception handling.

---

## Performance Notes

- [ ] Add benchmarks here as we discover performance characteristics

---

## Tooling

### Code Smell Detection
```bash
# Check function sizes
python scripts/ci/check_function_sizes.py src/solstein/research/pipeline.py

# Check class sizes
python scripts/ci/check_class_sizes.py src/solstein/data/loaders.py

# Full code smell detection
python scripts/ci/code_smell_detector.py src/solstein/
```

---

*Last updated: 2026-03-06*
