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

API_KEY = os.environ.get("OPEN_WEATHER_API_KEY", "28b2485cf1de8a48458937d968cc3ec9")

# MongoDB Configuration
# MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27018")
MONGO_URL = "mongodb://mongo"
client = MongoClient(MONGO_URL)
db = client.weather_db

# Get weather collection in MongoDB
weather_collection = db.weather_collection

# Get cities collection in MongoDB
cities_collection = db.cities_collection
cities = read_cities()
# Delete all the existing cities
cities_collection.delete_many({})
# Insert the cities
cities_collection.insert_one({"cities": cities})


# Routes
@app.get("/weather-data")
def get_weather_data():
    # Get the weather data from MongoDB
    data = weather_collection.find()
    data = [[item["id"], item["datetime"], item["weather_data"]] for item in data]
    if not data:
        return {"message": "Weather data not found"}
    # Transform the data to a list
    return {"data": data, "message": "Weather data retrieved successfully"}


@app.get("/cities")
def get_cities():
    # Get the cities from MongoDB
    data = cities_collection.find()
    data = [item["cities"] for item in data]
    if not data:
        return {"message": "Cities not found"}
    # Transform the data to a list
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
    # Collect weather data from Open Weather API and store it in MongoDB
    try:
        # First, verify if the request_id is already in the database
        if weather_collection.find_one({"id": request_id}):
            return {"message": "Weather data already collected for this request_id"}
        for idx, city_id in enumerate(cities):
            data = await fetch_weather(city_id)
            # Get the temperature and humidity from the data
            city_id, temperature, humidity = data["id"], data["main"]["temp"], data["main"]["humidity"]
            # Store the data in MongoDB
            weather_collection.insert_one({
                "id": request_id,
                "datetime": datetime.now(),
                "weather_data": {
                    "city_id": city_id,
                    "temperature": temperature,
                    "humidity": humidity
                }
            })
            await asyncio.sleep(1)
    except Exception as e:
        return {"message": f"Error while collecting weather data: {str(e)}"}
    return {"message": "Weather data collected successfully", "data": data}


@app.get("/get-collection-progress/{request_id}")
def get_collection_progress(request_id: int) -> Dict[str, str]:
    # Get the collection progress of the user from MongoDB
    data = weather_collection.find({"id": request_id})
    if not data:
        return {"message": "Request ID not found"}
    data = [item for item in data]
    percentage_progress = (len(data) / len(cities)) * 100
    return {"percentage_progress": f"{percentage_progress:.1f}%", "message": "Collection progress retrieved successfully"}
