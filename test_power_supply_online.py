
import pytest
import os

# This is a setup function that runs before each test function in this module.
# While it doesn't directly pass parameters to the test function, it fulfills
# the request for a "setup function call".
# The parameters (read path and result) are defined using pytest.mark.parametrize
# directly on the test function.
def setup_function():
    """
    Setup function for the power supply online test.
    This function runs before each test function in this module.
    """
    print("\nSetting up test for ACAD power supply online status...")

@pytest.mark.parametrize("file_path, expected_value", [
    ("/sys/class/power_supply/ACAD/online", "1")
])
def test_acad_power_supply_online(file_path, expected_value):
    """
    Tests if the ACAD power supply is online by reading its status file.

    Args:
        file_path (str): The absolute path to the power supply status file.
        expected_value (str): The expected content of the status file for an online status.
    """
    if not os.path.exists(file_path):
        pytest.skip(f"Power supply status file not found: {file_path}. Skipping test.")

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        assert content == expected_value, \
            f"ACAD power supply status mismatch: Expected '{expected_value}', but got '{content}' from {file_path}"
    except Exception as e:
        pytest.fail(f"An error occurred while reading {file_path}: {e}")

