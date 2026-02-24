# Testing Rules

## General Testing Principles
- **Test Coverage**: Aim for meaningful coverage, not 100%. Focus on critical paths and business logic.
- **Test Organization**: Follow patterns: `test_*.py` or `*_test.py` for test files.
- **Test Isolation**: Each test should be independent and not rely on external state.
- **Test Naming**: Use descriptive names that clearly indicate what is being tested.
- **Test Data**: Use realistic test data that reflects production scenarios.

## Code Patterns
```python
def test_something():
    """Good test naming"""
    assert 1 + 1 == 2

def test_with_arrange_act_assert():
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = process_data(setup_data)
    
    # Assert
    assert result == expected_result
```

## Anti-Patterns to Avoid
- **Test Pollution**: Avoid tests that modify shared state without cleanup.
- **Brittle Tests**: Tests should be resilient to minor implementation changes.
- **Over-Mocking**: Don't mock everything; test real integrations where appropriate.
- **Slow Tests**: Keep tests fast; use parallelization for long-running tests.
- **Test Code Duplication**: Extract common test utilities and patterns.

```python
def t():
    return 42  # Bad test naming

def test_no_assert():
    x = 5  # No assertion

# Test with hardcoded values

def test_hardcoded():
    assert os.path.exists('/path/to/file') == True  # Hardcoded paths

# Test with no isolation

def test_shared_state():
    global_counter = 0
    global_counter += 1
    assert global_counter == 1  # Shared state

# Test with no error handling

def test_no_error_handling():
    risky_operation()  # No error handling

# Test with no cleanup

def test_no_cleanup():
    temp_file = open('temp.txt', 'w')
    temp_file.write('test')  # No cleanup

# Test with no parameterization

def test_single_case():
    assert add(2, 2) == 4  # Single case, no parameterization

def add(a, b):
    return a + b