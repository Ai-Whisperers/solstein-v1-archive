# Python Project Template

## Project Structure
```
project-name/
├── README.md
├── .gitignore
├── pyproject.toml
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       └── module.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
│   └── index.md
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
name = "project-name"
version = "0.1.0"
description = "Project description"
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
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "black",
    "isort",
    "flake8",
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
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
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
    "--cov=project_name",
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
source = ["project_name"]
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

## Main Module Example
```python
"""
Main module for the project.
"""

from typing import Optional


def add(a: float, b: float) -> float:
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


def greet(name: Optional[str] = None) -> str:
    """
    Greet someone.
    
    Args:
        name: Name of the person to greet (optional)
        
    Returns:
        Greeting message
    """
    if name:
        return f"Hello, {name}!"
    return "Hello, World!"


if __name__ == "__main__":
    print(greet())
```

## Test Example
```python
"""
Tests for the main module.
"""

import unittest
from project_name.main import add, greet


class TestMain(unittest.TestCase):
    def test_add(self):
        """Test the add function."""
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0, 0), 0)
    
    def test_greet_with_name(self):
        """Test greet with name."""
        self.assertEqual(greet("Alice"), "Hello, Alice!")
    
    def test_greet_without_name(self):
        """Test greet without name."""
        self.assertEqual(greet(), "Hello, World!")


if __name__ == "__main__":
    unittest.main()
```

## Development Commands
```bash
# Install dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Run tests
pytest

# Run tests with coverage
pytest --cov=project_name

# Build package
python -m build

# Install in development mode
pip install -e .
```