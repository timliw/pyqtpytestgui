
import pytest
import os

# This is a setup function that can be used to prepare the test environment.
# For this specific test, we don't have much to set up, but it's here as requested.
def setup_function(function):
    """Setup for the power supply test."""
    # You could add setup code here if needed, e.g., checking if the path exists.
    # For now, we'll just print a message.
    print("Setting up power supply test.")

# This is a teardown function that can be used to clean up after the test.
def teardown_function(function):
    """Teardown for the power supply test."""
    # You could add cleanup code here if needed.
    print("Tearing down power supply test.")

@pytest.mark.parametrize("path, expected_result", [
    ("/sys/class/power_supply/ACAD/online", "1")
])
def test_power_supply_status(path, expected_result):
    """
    Tests if the power supply is online.
    It reads the file specified by the 'path' parameter and checks if its content
    matches the 'expected_result'.
    """
    assert os.path.exists(path), f"Path not found: {path}"
    with open(path, 'r') as f:
        content = f.read().strip()
    assert content == expected_result, f"Expected {expected_result} but got {content}"
