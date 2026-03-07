# OpenCode Rules Index

## Quick Reference

### Before You Start
1. Read [epic-management.md](epic-management.md) - How to work on epics
2. Check [code-quality.md](code-quality.md) - File/class/function size limits
3. Review [error-handling.md](error-handling.md) - Error handling requirements

### While Coding
1. Follow [refactoring.md](refactoring.md) - Patterns for clean code
2. Obey [testing.md](testing.md) - Testing best practices
3. Check [api-design.md](api-design.md) - API conventions

### Before Committing
1. Run quality checks (see below)
2. Verify no regressions
3. Update documentation

## Rule Categories

### 🎯 Epic Management
**File**: [epic-management.md](epic-management.md)

- Epic lifecycle and states
- Story writing template
- Epic execution workflow
- Completion checklist
- Handoff procedures

**When to use**: Starting or working on any epic

### 📏 Code Quality
**File**: [code-quality.md](code-quality.md)

- File size limits (500 lines max)
- Function size limits (100 lines max)
- Class size limits (300 lines max)
- Import organization
- Circular import prevention
- Code duplication rules

**When to use**: Writing or reviewing code

### 🔧 Refactoring
**File**: [refactoring.md](refactoring.md)

- When to refactor triggers
- Extraction patterns (method, class, module)
- Design patterns (Strategy, Builder, Pipeline)
- Backward compatibility
- Refactoring checklist

**When to use**: Refactoring code, splitting large files/classes

### ⚠️ Error Handling
**File**: [error-handling.md](error-handling.md)

- Core philosophy: Never silently swallow errors
- Exception type guidelines
- Error context requirements
- Structured error results
- Async error handling
- Error recovery patterns

**When to use**: Writing any error handling code

### 🧪 Testing
**File**: [testing.md](testing.md)

- Testing principles
- Test organization
- Test naming conventions
- Anti-patterns to avoid

**When to use**: Writing or reviewing tests

### 🔌 API Design
**File**: [api-design.md](api-design.md)

- API conventions
- Endpoint design
- Request/response patterns
- Error responses

**When to use**: Designing or modifying APIs

### 🗄️ Database
**File**: [database.md](database.md)

- SQL best practices
- Migration guidelines
- Query optimization
- Index usage

**When to use**: Working with database code

### 🚀 Performance
**File**: [performance.md](performance.md)

- Performance optimization
- Caching strategies
- Query optimization
- Profiling

**When to use**: Optimizing performance

### 🔒 Security
**File**: [security.md](security.md)

- Security best practices
- Input validation
- Authentication/authorization
- Data protection

**When to use**: Handling sensitive data or security features

### 📚 Documentation
**File**: [documentation.md](documentation.md)

- Documentation standards
- Docstring formats
- README requirements
- Code comments

**When to use**: Writing documentation

### 🚀 Deployment
**File**: [deployment.md](deployment.md)

- Deployment procedures
- Environment management
- Rollback strategies
- Monitoring

**When to use**: Deploying code

### 📊 Project Management
**File**: [project-management.md](project-management.md)

- Project organization
- Task tracking
- Communication
- Meeting notes

**When to use**: Managing project tasks

## Quality Check Commands

### Before Committing
```bash
# File size checks
python scripts/ci/check_file_sizes.py --max-lines 500
python scripts/ci/check_class_sizes.py --max-lines 300
python scripts/ci/check_function_sizes.py --max-lines 100

# Code quality
python scripts/ci/code_smell_detector.py
python scripts/ci/detect_import_cycles.py
python scripts/ci/detect_code_duplication.py

# Testing
python -m pytest tests/ -xvs
```

### Epic Completion
```bash
# Full quality suite
python scripts/ci/run_quality_checks.py
```

## Common Patterns

### Starting a New Epic
1. Read [epic-management.md](epic-management.md)
2. Verify dependencies are complete
3. Run baseline metrics
4. Create todo list
5. Start with Story 0

### Refactoring Code
1. Read [refactoring.md](refactoring.md)
2. Ensure tests exist
3. Run tests (should pass)
4. Make small changes
5. Run tests (should still pass)
6. Commit
7. Repeat

### Handling Errors
1. Read [error-handling.md](error-handling.md)
2. Never use bare except
3. Always include context
4. Log appropriately
5. Test error paths

### Writing Tests
1. Read [testing.md](testing.md)
2. Follow arrange-act-assert
3. Use descriptive names
4. Test error paths
5. Keep tests isolated

## Rule Updates

### When to Update Rules
- New recurring issue identified
- Pattern established in epics
- Tool/process changes
- Team feedback

### How to Update
1. Edit the relevant rule file
2. Update this index if needed
3. Announce changes to team
4. Update AGENTS.md if applicable

## Questions?

If you're unsure which rule applies:
1. Check this index for the category
2. Read the relevant rule file
3. When in doubt, ask

Remember: **These rules exist to help, not hinder.** Use judgment, but defaults matter.
