import os
import requests
from langchain.tools import tool

#to get the live exchange rates to make budget planning accurate
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str):
    """
    Converts an amount from one currency to another using live exchange rates.
    Use this to give accurate budget estimates in both source and destination currencies.
    """
    api_key = os.getenv("EXCHANGE_RATE_KEY")
    # using the pair conversion endpoint for speed
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if data["result"] == "success":
            converted = data['conversion_result']
            rate = data['conversion_rate']
            return f"{amount} {from_currency} is {converted:.2f} {to_currency} (Rate: 1 {from_currency} = {rate:.4f} {to_currency})"
        return "could not fetch live exchange rates"
    except Exception as e:
        return f"currency service error: {str(e)}"