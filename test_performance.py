import pytest
import time

def test_performance(duration):
    print(f"Running performance test for {duration} seconds")
    time.sleep(duration)
    assert True
