import pytest

@pytest.mark.parametrize("data_type", ["user", "product"])
def test_data_validation(data_type):
    print(f"Validating {data_type} data")
    assert data_type in ["user", "product"]
