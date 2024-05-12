# Системные тесты
import pytest
import requests

@pytest.fixture
def api_url():
    return "http://localhost:5000"

def test_parking_list(api_url):
    response = requests.get(f"{api_url}/parkings")
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']

def test_parking_status(api_url):
    response = requests.get(f"{api_url}/parkings/1")
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
