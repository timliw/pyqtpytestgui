import pytest

@pytest.fixture
def user():
    return "admin"

@pytest.fixture
def password():
    return "password123"

@pytest.fixture
def duration():
    return 5
