import os
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter(prefix="/api/weather", tags=["Weather"])

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")



@router.get("/search/by-city")
async def search_by_city(
    city: str,
    country: str,
    state: str | None = None
):

    #GEO ENCODING
    geo_query = f"{city},{state},{country}" if state else f"{city},{country}"

    geo_url = (
        "https://api.openweathermap.org/geo/1.0/direct"
        f"?q={geo_query}&limit=1&appid={OPENWEATHER_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        geo_response = await client.get(geo_url)

        if geo_response.status_code != 200:
            raise HTTPException(
                status_code=geo_response.status_code,
                detail="Geocoding API error"
            )

        geo_data = geo_response.json()

        if not geo_data:
            raise HTTPException(
                status_code=404,
                detail="City not found"
            )

        geo = geo_data[0]


        lat = geo["lat"]
        lon = geo["lon"]

        # get weatherr 
        weather_url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        weather_response = await client.get(weather_url)

        if weather_response.status_code != 200:
            raise HTTPException(
                status_code=weather_response.status_code,
                detail="Weather API error"
            )

        weather = weather_response.json()

    
    return {
        "location": {
            "city": geo["name"],
            "state": geo.get("state"),
            "country": geo["country"],
            "lat": lat,
            "lon": lon
        },
        "weather": {
            "temperature": weather["main"]["temp"],
            "feels_like": weather["main"]["feels_like"],
            "humidity": weather["main"]["humidity"],
            "description": weather["weather"][0]["description"],
            "wind_speed": weather["wind"]["speed"]
        }
    }



@router.get("/search/by-zip")
async def search_by_zip(zip_code: str, country: str):
  
    
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Weather API error")
        
        data = response.json()
        
        return {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }


@router.get("/search/by-coords")
async def search_by_coords(lat: float, lon: float):
    """
    Exemple: /api/weather/search/by-coords?lat=48.8566&lon=2.3522
    """
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Weather API error")
        
        data = response.json()
        
        return {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }






@router.get("/weather/by-city-range")
async def weather_by_city_range(
    city: str,
    country: str,
    state: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None
):


    start = end = None

    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else: start = datetime.now().date()

        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else: end = start + timedelta(days=5)

    except ValueError:
        raise HTTPException(400, "Invalid date format (YYYY-MM-DD)")

    if start and end:
        if start > end:
            raise HTTPException(400, "start_date must be <= end_date")
        if (end - start).days > 5:
            raise HTTPException(400, "Range limited to 5 days max")

    #GEO CODING
    geo_query = f"{city},{state},{country}" if state else f"{city},{country}"

    geo_url = (
        f"https://api.openweathermap.org/geo/1.0/direct"
        f"?q={geo_query}&limit=1&appid={OPENWEATHER_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        geo_resp = await client.get(geo_url)

        if geo_resp.status_code != 200 or not geo_resp.json():
            raise HTTPException(404, "City not found")

        geo = geo_resp.json()[0]
        lat = geo["lat"]
        lon = geo["lon"]

        #FORECAST 5 days
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        weather_resp = await client.get(weather_url)

        if weather_resp.status_code != 200:
            raise HTTPException(500, "Weather API error")

        forecast = weather_resp.json()["list"]

    #Filters based on date range
    results = []

    for item in forecast:
        item_date = datetime.fromtimestamp(item["dt"]).date()

        if start and end:
            if not (start <= item_date <= end):
                continue

        results.append({
            "datetime": item["dt_txt"],
            "temp": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "humidity": item["main"]["humidity"],
            "description": item["weather"][0]["description"],
            "wind_speed": item["wind"]["speed"]
        })

    return {
        "city": geo["name"],
        "state": geo.get("state"),
        "country": geo["country"],
        "lat": lat,
        "lon": lon,
        "count": len(results),
        "data": results
    }