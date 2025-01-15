from agent.tool.tool_registry import tool
import urllib.request
import json
import requests
from typing import Dict

@tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts currency using latest exchange rates.
    
    Args:
        - amount: Amount to convert
        - from_currency: Source currency code (e.g., USD)
        - to_currency: Target currency code (e.g., EUR)

    Returns:
        - String containing the converted amount in target currency
    """
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            
        if "rates" not in data:
            return "Error: Could not fetch exchange rates"
            
        rate = data["rates"].get(to_currency.upper())
        if not rate:
            return f"Error: No rate found for {to_currency}"
            
        converted = amount * rate
        # return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
        return f"{converted:.2f} {to_currency.upper()}"
        
    except Exception as e:
        return f"Error converting currency: {str(e)}"

@tool()    
def current_weather(city_name: str, country_name: str) -> Dict:
    """Get the current weather for a given city.
    
    Args:
        - city_name: Name of the city to get weather for.    
        - country_name: Name of the Country where the city is.  

    Returns:
       - A dictionary containing the city name, country name and temperature in °C.
    """
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city_name + "," + country_name,
            "appid": "3fcdbdc8c0ceaffec031aebe6bdad062",
            "units": "metric"  # Use 'imperial' for Fahrenheit
        }

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        weather_data = response.json()
        return str({
            "City": weather_data.get("name"),
            "Temperature (°C)": weather_data["main"]["temp"],
            "Weather": weather_data["weather"][0]["description"],
            "Humidity (%)": weather_data["main"]["humidity"],
            "Wind Speed (m/s)": weather_data["wind"]["speed"]
        })
    except requests.exceptions.RequestException as e:
        return {"Error": str(e)}
    except KeyError:
        return {"Error": "Unexpected response format"}
    
@tool()    
def country_for_city(city_name: str) -> str:
    """Get the country name for the given city name.
    
    Args:
        - city_name: Name of the city to get weather for.    

    Returns:
       - Name of the Country where the city is
    """
    try:
        # print(city_name)
        return "US"
        
    except Exception as e:
        return f"Error get country for city: {str(e)}"
    
@tool()    
def get_current_location() -> str:
    """Get the city and country name of the current location.
    
    Returns:
       - Name of the City and Country for current location
    """
    try:
        return "Cary, US"
        
    except Exception as e:
        return f"Error getting location: {str(e)}"    