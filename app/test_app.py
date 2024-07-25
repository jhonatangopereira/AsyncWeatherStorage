import time

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app

client = TestClient(app)

# Configuração do MongoDB
MONGO_URL = "mongodb://mongo"
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.weather_db

weather_collection = db.weather_collection
cities_collection = db.cities_collection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup antes dos testes
    weather_collection.delete_many({})
    cities_collection.delete_many({})
    # Inserir cidades de teste
    cities = [1, 2, 3]  # Exemplo de IDs de cidades
    cities_collection.insert_one({"cities": cities})
    yield
    # Teardown depois dos testes
    weather_collection.delete_many({})
    cities_collection.delete_many({})

def test_get_weather_data():
    response = client.get("/weather-data")
    assert response.status_code == 200
    assert response.json() == {"message": "Weather data not found"}

def test_get_cities():
    response = client.get("/cities")
    assert response.status_code == 200
    data = response.json().get("data")
    assert isinstance(data, list)
    assert len(data) > 0
    assert "message" in response.json()
    assert response.json()["message"] == "Cities retrieved successfully"

def test_collect_weather(monkeypatch):
    request_id = 1

    # Mock da função fetch_weather para retornar dados falsos
    async def mock_fetch_weather(city_id: int):
        return {
            "id": city_id,
            "main": {
                "temp": 25,
                "humidity": 80
            }
        }

    monkeypatch.setattr("app.main.fetch_weather", mock_fetch_weather)

    response = client.post(f"/collect-weather/{request_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Weather data collected successfully"

    # Verifique se os dados foram realmente inseridos no MongoDB
    data = weather_collection.find({"id": request_id})
    assert len(list(data)) > 0

def test_get_collection_progress():
    request_id = 1

    # Primeira coleta para o request_id
    client.post(f"/collect-weather/{request_id}")

    # Aguarde um pouco para garantir que a coleta foi feita
    time.sleep(2)

    response = client.get(f"/get-collection-progress/{request_id}")
    assert response.status_code == 200
    assert "percentage_progress" in response.json()
    assert response.json()["message"] == "Collection progress retrieved successfully"
