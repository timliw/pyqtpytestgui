
import time
import pytest

def test_success():
    """A test that always passes."""
    time.sleep(1)
    assert True

def test_failure():
    """A test that always fails."""
    time.sleep(1)
    assert False

@pytest.mark.parametrize("i", range(5))
def test_parametrized(i):
    """A parametrized test."""
    time.sleep(0.5)
    assert i % 2 == 0
