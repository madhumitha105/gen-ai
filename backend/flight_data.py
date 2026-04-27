from langchain.tools import tool
import requests
import os

@tool
def get_flights(source: str, destination: str, departure_date: str, adults: int = 1, children: int = 0, currency: str = "INR"):
    """
    Fetch flight options between source and destination.
    Args:
        source: The starting city/airport code.
        destination: The destination city/airport code.
        departure_date: Date in YYYY-MM-DD format.
        adults: Number of adult passengers.
        children: Number of child passengers.
        currency: The currency code (e.g., INR, USD).
    """

    url = "https://skyscanner44.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
        "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com"
    }

    #dynamic params based on user input
    params = {
        "origin": source,
        "destination": destination,
        "departureDate": departure_date,
        "adults": str(adults),
        "children": str(children),
        "currency": currency
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            return f"Error fetching flights: Status {response.status_code}"

        data = response.json()
        
        #getting top 3 suggestions
        buckets = data.get("itineraries", {}).get("buckets", [])
        if not buckets:
            return "No flights found for these criteria."

        items = buckets[0].get("items", [])[:3]
        
        result = []
        for f in items:
            price = f["price"]["formatted"]
            airline = f["legs"][0]["carriers"]["marketing"][0]["name"]
            duration_mins = f["legs"][0]["durationInMinutes"]
            
            #converting minutes to hours/mins for better readability
            hours = duration_mins // 60
            mins = duration_mins % 60
            duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

            result.append(f"- {airline} | {price} | {duration_str}")

        return "\n".join(result) if result else "No flights found."

    except Exception as e:
        return f"An error occurred while searching for flights: {str(e)}"