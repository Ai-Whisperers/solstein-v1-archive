# FastAPI REST API Template

## Project Structure
```
fastapi-project/
├── README.md
├── .gitignore
├── pyproject.toml
├── src/
│   └── fastapi_project/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   ├── items.py
│       │   │   └── users.py
│       │   └── dependencies.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── security.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── item.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── .claude/
    ├── rules/
    └── commands/
```

## pyproject.toml
```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastapi-project"
version = "0.1.0"
description = "FastAPI REST API project"
authors = [{name = "Author Name", email = "author@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]
dependencies = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "sqlalchemy",
    "alembic",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "black",
    "isort",
    "flake8",
    "mypy",
]
test = [
    "pytest",
    "pytest-cov",
]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(\n  # directories\n  \.eggs\n  | \.git\n  | \.hg\n  | \.mypy_cache\n  | \.tox\n  | \.venv\n  | build\n  | dist\n)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=fastapi_project",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--strict-markers",
    "--strict-config",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["fastapi_project"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

## Main Application
```python
"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routers import items, users
from .core.config import settings
from .core.security import get_current_user


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(items.router, prefix=settings.API_V1_STR, tags=["items"])
    app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
    
    # Add event handlers
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        print(f"Starting {settings.PROJECT_NAME}...")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event handler."""
        print(f"Shutting down {settings.PROJECT_NAME}...")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": settings.PROJECT_NAME}
    
    return app


app = create_application()
```