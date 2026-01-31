import json
from datetime import datetime
from pathlib import Path
import re

import requests


class SettingsService:
    __FILE = Path("Setting.json")

    def __init__(self):
        self.com_port = None
        self.city = None
        self.api_key = None

    def change_settings(self, com_port : str, city : str, api_key : str):
        self.com_port = com_port
        self.city = city
        self.api_key = api_key

    def load(self) -> bool:
        if not self.__FILE.exists():
            data = {
                "com_port": "None",
                "weather": {
                    "api_key": "None",
                    "city": "None"
                }
            }

            with open(self.__FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            return False
        else:
            with open(self.__FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            com_port = data.get("com_port")
            weather = data.get("weather",{})
            self.city = weather.get("city")
            self.api_key = weather.get("api_key")

            if com_port is None or self.city is None or self.api_key is None or re.fullmatch(r"COM\d+", com_port) is None:
                return False

            self.com_port = data.get("com_port")
            self.city = weather.get("city")
            self.api_key = weather.get("api_key")

            return True

    def save(self):
        data = {
            "com_port": self.com_port,
            "weather": {
                "api_key": self.api_key,
                "city": self.city
            }
        }
        with open(self.__FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)



class WeatherService:
    """Class Service for retrieving and caching weather data from OpenWeatherMap API"""
    __URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key : str, city : str = "Samara"):
        """
        Initialize WeatherService.

        :param api_key: OpenWeatherMap API key.
        :param city: City name for weather requests.
        """
        self.__api_key = api_key
        self.__city = city
        self.__data = None
        self.__last_update = None

    def get_weather(self) -> dict:
        """Get current weather data. Weather data is cached and updated once per day.

        :return: Dictionary with weather information:
            {
                "city": str,
                "temperature": float,
                "feels_like": float,
                "humidity": int,
                "description": str,
                "wind_speed": float
            }
        :raises requests.RequestException: If the HTTP request fails.
        """
        if self.__data is not None or (self.__last_update is not None and self.__last_update != datetime.now().date()):
            return self.__data
        else:
            self.__last_update = datetime.now().date()

        params = {
            "q": self.__city,
            "appid": self.__api_key,
            "units": "metric",
            "lang": "ru"
        }

        response = requests.get(self.__URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        self.__data = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        return self.__data