import pytest

def test_login(user, password):
    print(f"Logging in with user: {user} and password: {password}")
    assert user == "admin"
    assert password == "password123"
