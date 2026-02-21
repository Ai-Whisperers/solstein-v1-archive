# Example test file with common issues

# Testing Rule Violations
import os
import sys

# Test function with no docstring


def test_example():
    assert 1 + 1 == 2


# Test file with no tests
class ExampleClass:
    """This class has a docstring"""

    def method(self):
        return True


# Test with poor naming


def t():
    return 42


# Test with no assertions


def test_no_assert():
    x = 5


# Test with hardcoded values


def test_hardcoded():
    assert os.path.exists("/path/to/file") == True


# Test with no isolation


def test_shared_state():
    global_counter = 0
    global_counter += 1
    assert global_counter == 1


# Test with no error handling


def test_no_error_handling():
    risky_operation()


# Test with no cleanup


def test_no_cleanup():
    temp_file = open("temp.txt", "w")
    temp_file.write("test")


# Test with no parameterization


def test_single_case():
    assert add(2, 2) == 4


def add(a, b):
    return a + b
