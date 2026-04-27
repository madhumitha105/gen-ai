import os
import requests
from langchain.tools import tool

# this tool fetches current weather to help with travel advice
@tool
def get_weather(city: str):
    """
    Fetches the current weather for a city. 
    Use this to advise the user on packing or if the destination is currently suitable for travel.
    """
    api_key = os.getenv("OPEN_WEATHER_KEY")
    # using metric units for celsius
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            return f"current weather in {city}: {temp}°C, {desc}, humidity: {humidity}%"
        return "weather data not found for this city"
    except Exception as e:
        return f"weather service error: {str(e)}"