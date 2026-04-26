from langchain.tools import tool
import requests
import os

@tool
def get_flights(source: str, destination: str):
    """Fetch flight options between source and destination with airline, price, and duration."""

    url = "https://skyscanner44.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
        "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com"
    }

    params = {
        "origin": source,
        "destination": destination,
        "departureDate": "2026-06-01",
        "adults": "1",
        "currency": "INR"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return "No flight data available"

    data = response.json()

    try:
        flights = data["itineraries"]["buckets"][0]["items"][:3]

        result = []
        for f in flights:
            price = f["price"]["formatted"]
            airline = f["legs"][0]["carriers"]["marketing"][0]["name"]
            duration = f["legs"][0]["durationInMinutes"]

            result.append(f"{airline} | {price} | {duration} mins")

        return "\n".join(result)

    except:
        return "No flights found"