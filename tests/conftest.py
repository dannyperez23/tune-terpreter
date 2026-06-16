import pytest
from app import app, limiter

@pytest.fixture
def client():
    app.config['TESTING'] = True
    limiter.enabled = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def client_limiting_enabled():
    app.config['TESTING'] = True
    limiter.enabled = True
    with app.test_client() as client:
        yield client