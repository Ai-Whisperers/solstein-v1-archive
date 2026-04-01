# OpenCode Framework Documentation

## Overview

OpenCode is a comprehensive framework for coding standards, validation, and compliance checking. It provides:

- **Rule System**: 8 categories of coding standards and best practices
- **Command System**: Extensible command framework for automation
- **Pattern Templates**: Production-ready project templates
- **Validation Engine**: Automated compliance checking
- **Documentation**: Comprehensive guides and examples

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ai-whisperers/solstein.git
cd solstein/.claude

# Install dependencies
pip install -e ".[dev]"
```

### Usage

```bash
# Validate a file
python -m validation.checker path/to/file.py

# Validate a directory
python -m validation.checker path/to/directory/

# Generate compliance report
python -m validation.checker path/to/directory/ --report

# List available commands
python -m commands.list

# Get help for a command
python -m commands.help hello
```

## Rule Categories

### 1. Testing
**File**: `.claude/rules/testing.md`

**Focus**: Unit tests, integration tests, test coverage, testing best practices

**Key Rules**:
- Test files must follow naming conventions (`test_*.py`, `*_test.py`)
- Test functions must start with `test_`
- Test classes must inherit from `unittest.TestCase`
- Minimum 80% code coverage required
- Integration tests must be marked with `@pytest.mark.integration`

### 2. API Design
**File**: `.claude/rules/api-design.md`

**Focus**: REST API design, endpoint structure, request/response formats

**Key Rules**:
- Use RESTful conventions for endpoints
- Proper HTTP status codes for responses
- Consistent error response format
- API documentation with OpenAPI/Swagger
- Rate limiting and pagination support

### 3. Database
**File**: `.claude/rules/database.md`

**Focus**: Database schema design, migrations, query optimization

**Key Rules**:
- Use migrations for schema changes
- Proper indexing strategies
- Query optimization and performance
- Database connection pooling
- Backup and recovery procedures

### 4. Deployment
**File**: `.claude/rules/deployment.md`

**Focus**: CI/CD, infrastructure, containerization, monitoring

**Key Rules**:
- Automated testing in CI/CD pipeline
- Infrastructure as code (Terraform)
- Container orchestration (Docker/Kubernetes)
- Health checks and monitoring
- Zero-downtime deployments

### 5. Security
**File**: `.claude/rules/security.md`

**Focus**: Authentication, authorization, data protection, vulnerability prevention

**Key Rules**:
- Input validation and sanitization
- Authentication and authorization
- Data encryption at rest and in transit
- Security headers and CORS configuration
- Regular security audits and penetration testing

### 6. Performance
**File**: `.claude/rules/performance.md`

**Focus**: Application performance, optimization, scalability

**Key Rules**:
- Code optimization and profiling
- Caching strategies
- Database query optimization
- Memory and CPU usage monitoring
- Load testing and capacity planning

### 7. Documentation
**File**: `.claude/rules/documentation.md`

**Focus**: Code documentation, API docs, user guides, maintenance docs

**Key Rules**:
- Function and class documentation
- API documentation with examples
- README files for all projects
- Architecture decision records (ADRs)
- Change logs and version history

### 8. Project Management
**File**: `.claude/rules/project-management.md`

**Focus**: Development workflows, code review, team collaboration

**Key Rules**:
- Git workflow and branching strategy
- Code review requirements
- Issue tracking and project management
- Team communication and documentation
- Release management and versioning

## Command System

### Available Commands

```bash
# List all commands
python -m commands.list

# Say hello
python -m commands.hello [name]

# Add two numbers
python -m commands.add a b

# Show version
python -m commands.version

# Get help
python -m commands.help [command]
```

### Creating Custom Commands

```python
from .commands import register_command

@register_command("custom", "Custom command description", "[args]")
def custom_command(args):
    """Custom command implementation."""
    print("Custom command executed")
    return 0
```

## Pattern Templates

### Python Project Template
**File**: `.claude/templars/python-project.md`

**Features**:
- Modern Python project structure
- pyproject.toml configuration
- Testing setup with pytest
- Code formatting with black/isort
- Linting with flake8
- Type checking with mypy

### FastAPI REST API Template
**File**: `.claude/templars/fastapi-rest-api-1.md`

**Features**:
- FastAPI application structure
- API routers and dependencies
- Database integration with SQLAlchemy
- Authentication and security
- Configuration management
- Database migrations with Alembic

## Validation Engine

### Validation Results

```python
from .validation.checker import ValidationResult

result = ValidationResult(
    rule="test_rule",
    file="test_file.py",
    line=1,
    column=None,
    message="Test message",
    severity="warning",
    passed=False
)
```

### Custom Validators

```python
def custom_validator(file_path: str, content: str, lines: List[str]) -> Tuple[bool, str]:
    """Custom validation logic."""
    # Your validation logic here
    return True, "Validation passed"
```

### Compliance Report

```bash
# Generate detailed report
python -m validation.checker path/to/directory/ --report

# JSON output
python -m validation.checker path/to/directory/ --json
```

## Development Workflow

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest
pytest --cov=project_name
```

### Validation

```bash
# Validate before commit
python -m validation.checker .

# Validate specific file
python -m validation.checker src/main.py

# Generate compliance report
python -m validation.checker . --report
```

## Contributing

### Adding New Rules

1. Create new rule file in `.claude/rules/`
2. Follow existing rule format
3. Add validation patterns and requirements
4. Test with validation engine

### Adding New Commands

1. Create command function in `.claude/commands/examples.py`
2. Use `@register_command` decorator
3. Add argument parsing with argparse
4. Test command functionality

### Adding New Templates

1. Create template file in `.claude/templars/`
2. Include project structure and examples
3. Add configuration files
4. Document usage and setup

## Configuration

### Rule Configuration

Rules can be configured in `.claude/rules/` directory. Each rule file should include:

- Category and severity
- Validation patterns
- Requirements and anti-patterns
- Custom validators
- File patterns and exclusions

### Command Configuration

Commands are registered in `.claude/commands/__init__.py` and can be configured with:

- Command name and description
- Argument parser configuration
- Usage examples
- Error handling

## Troubleshooting

### Common Issues

**Validation Errors**:
- Check file paths and permissions
- Verify rule patterns are correct
- Test custom validators separately

**Command Issues**:
- Verify command registration
- Check argument parsing
- Review error handling

**Template Issues**:
- Validate project structure
- Check configuration files
- Test build and installation

### Support

For issues and questions:
- Check documentation in `.claude/docs/`
- Review existing issues in repository
- Test with sample projects

## License

OpenCode Framework is proprietary software. See LICENSE file for details.

---

**Built by AI Whisperers**
*Finding the diamonds nobody knew were there.*