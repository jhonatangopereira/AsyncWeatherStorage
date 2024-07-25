import asyncio
import os
from datetime import datetime
from typing import Dict

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient

from app.cities_reader import read_cities

app = FastAPI()


load_dotenv()

# OpenWeather API Key
API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")
if not API_KEY:
    raise ValueError("API key not found")

# Configuração do MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo")
client = MongoClient(MONGO_URL)
db = client.weather_db

weather_collection = db.weather_collection
cities_collection = db.cities_collection

# Ler as cidades do arquivo cities.txt e salvar no MongoDB
cities = read_cities()
cities_collection.delete_many({})
cities_collection.insert_one({"cities": cities})


# Rotas
@app.get("/weather-data")
def get_weather_data():
    # Recuperar os dados de temperatura e umidade do MongoDB
    data = weather_collection.find()
    data = [[item["id"], item["datetime"], item["weather_data"]] for item in data]
    if not data:
        return {"message": "Weather data not found"}
    # Transformar os dados em uma lista
    return {"data": data, "message": "Weather data retrieved successfully"}


@app.get("/cities")
def get_cities():
    # Recuperar as cidades do MongoDB
    data = cities_collection.find()
    data = [item["cities"] for item in data]
    if not data:
        return {"message": "Cities not found"}
    # Transformar os dados em uma lista
    return {"data": data, "message": "Cities retrieved successfully"}


async def fetch_weather(city_id: int):
    try:
        request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}")
        data = request.json()
    except Exception as e:
        return {"message": f"Error while fetching weather data: {str(e)}"}
    return data

@app.post("/collect-weather/{request_id}")
async def collect_weather(request_id: int):
    # Coletar os dados de temperatura e umidade para cada cidade
    try:
        # Primeiro, verificar se os dados já foram coletados
        if weather_collection.find_one({"id": request_id}):
            return {"message": "Weather data already collected for this request_id"}
        # Extrair a hora atual
        now = datetime.now()
        for idx, city_id in enumerate(cities):
            if idx % 60 == 0:
                # Calcule o tempo restante até o próximo minuto
                current_second = now.second
                remaining_seconds = 60 - current_second
                await asyncio.sleep(remaining_seconds)
            data = await fetch_weather(city_id)
            # Extrair os dados necessários
            city_id, temperature, humidity = data["id"], data["main"]["temp"], data["main"]["humidity"]
            # Salvar os dados no MongoDB
            weather_collection.insert_one({
                "id": request_id,
                "datetime": datetime.now(),
                "weather_data": {
                    "city_id": city_id,
                    "temperature": temperature,
                    "humidity": humidity
                }
            })
    except Exception as e:
        return {"message": f"Error while collecting weather data: {str(e)}"}
    return {"message": "Weather data collected successfully", "data": data}


@app.get("/get-collection-progress/{request_id}")
def get_collection_progress(request_id: int) -> Dict[str, str]:
    # Retornar o progresso da coleta de dados
    data = weather_collection.find({"id": request_id})
    data = [item for item in data]
    if not data:
        return {"message": "Request ID not found"}
    # Calcular o progresso da coleta
    percentage_progress = (len(data) / len(cities)) * 100
    return {"percentage_progress": f"{percentage_progress:.1f}%", "message": "Collection progress retrieved successfully"}
