# Contributing to SolStein

Thank you for your interest in contributing to SolStein! We are building the future of competitive intelligence for VC/PE.

## Development Workflow

1.  **Fork and Clone**: Fork the repo and clone it locally.
2.  **Environment Setup**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .[dev]
    ```
3.  **Branching**: Create a feature branch (`git checkout -b feature/amazing-feature`).
4.  **Coding Standards**:
    *   We use `ruff` for linting and formatting. Run `ruff check .` and `ruff format .`.
    *   We use `mypy` for static type checking. Run `mypy .`.
    *   All new features must include tests.
5.  **Testing**: Run `pytest` to ensure all tests pass.
6.  **Commit**: Use conventional commits (e.g., `feat: add new scraper`, `fix: resolve sizing issue`).
7.  **Push and PR**: Push to your fork and submit a Pull Request.

## Project Structure

*   `src/solstein/`: Core application code.
*   `tests/`: Unit and integration tests.
*   `scripts/`: Utility scripts (migrations, demos).
*   `data/`: Local data storage (gitignored).
*   `docs/`: Documentation.

## Reporting Issues

Please search existing issues before creating a new one. When reporting a bug, please include:
*   Steps to reproduce.
*   Expected vs actual behavior.
*   Environment details.

## License

By contributing, you agree that your contributions will be licensed under the project's license.
