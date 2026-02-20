# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Consolidated output directory structure (`data/output/`).
- Professional documentation (`CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`).
- Strict linting and formatting configuration (`ruff`, `mypy`).

### Changed
- Refactored repository structure: separated Python core to `src/` and archived C# legacy code to `legacy/`.
- Updated `demo_solstein.py` and CLI tools to use new directory structure.

## [0.1.0] - 2024-03-XX

### Initial Release
- Basic competitive intelligence features.
- Financial metric extraction and scoring.
- Excel dashboard generation.
