# Tag-Based Versioning Guide

## Overview
Solstein uses git tags to drive automated versioning. Tags trigger version detection in CI/CD pipelines.

## Tag Formats

### Release Tags
```bash
# Standard release: v1.2.3
git tag -a release-1.2.3 -m "Release version 1.2.3"

# Pre-release: v1.2.3-rc1
git tag -a release-1.2.3-rc1 -m "Release candidate 1"
```

### Test Tags
```bash
# Test release: test-1.2.3-rc1
git tag -a test-1.2.3-rc1 -m "Test version for QA"
```

### Coverage Tags
```bash
# Coverage report: coverage-1.2.3
git tag -a coverage-1.2.3 -m "Coverage report version 1.2.3"
```

### Security Tags
```bash
# Security patch: security-20260224
git tag -a security-20260224 -m "Security patch"
```

## CI/CD Behavior

| Tag Pattern | Version | Action |
|-------------|---------|--------|
| `release-X.Y.Z` | X.Y.Z | Full release, update changelog |
| `release-X.Y.Z-rcN` | X.Y.Z-rcN | Release candidate, skip release |
| `test-X.Y.Z-rcN` | X.Y.Z-test | Test deployment |
| `coverage-X.Y.Z` | X.Y.Z | Coverage report only |
| `security-YYYYMMDD` | 0.0.1-security | Security patch |

## Creating Tags

### Local
```bash
# Create annotated tag
git tag -a release-1.2.3 -m "Release 1.2.3"

# Push to remote
git push origin release-1.2.3
```

### Via Makefile
```bash
# Create release tag
make tag-release VERSION=1.2.3

# Create test tag
make tag-test VERSION=1.2.3

# Create coverage tag
make tag-coverage VERSION=1.2.3
```

## Viewing Tags
```bash
# List all tags
git tag -l

# List with details
git tag -l -n

# Filter tags
git tag -l "release-*"
```

## Deleting Tags
```bash
# Delete local
git tag -d release-1.2.3

# Delete remote
git push origin --delete release-1.2.3
```

## Best Practices
1. Always use annotated tags (`-a`) with messages
2. Follow semantic versioning (MAJOR.MINOR.PATCH)
3. Test tags should never be merged to main
4. Security tags should include date in YYYYMMDD format
