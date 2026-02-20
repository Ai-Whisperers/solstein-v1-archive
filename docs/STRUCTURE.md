# Repository Structure Guide

This repository has been restructured to separate the modern Python application from legacy C# code.

## Directory Layout

*   **`src/solstein/`**: The core Python application (FastAPI, Pydantic).
*   **`legacy/`**: Archived C# solution and older project files. **Do not develop here.**
*   **`scripts/`**: Utility scripts for setup, data migration, and ad-hoc tasks.
*   **`docs/`**: Documentation.
    *   `archive/`: Old analysis documents.
    *   `architecture/`: Current architectural decisions.
*   **`tests/`**: Pytest suite.

## workflow

1.  **Install**: `pip install -e .[dev]`
2.  **Run API**: `uvicorn solstein.api.main:app --reload` (or similar)
3.  **Test**: `pytest`
