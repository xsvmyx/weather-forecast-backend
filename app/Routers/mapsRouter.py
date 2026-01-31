import os
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(prefix="/api/map", tags=["Map"])

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")



@router.get("/search/coords/by-city")
async def get_coords_by_city(
    city: str,
    country: str,
    state: str | None = None
):

    if state:
        query = f"{city},{state},{country}"
    else:
        query = f"{city},{country}"

    url = (
        "https://api.openweathermap.org/geo/1.0/direct"
        f"?q={query}&limit=1&appid={OPENWEATHER_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Geocoding API error"
            )

        data = response.json()

        if not data:
            raise HTTPException(status_code=404, detail="City not found")
        

        return {
            "city": data[0]["name"],
            "state": data[0].get("state"),
            "country": data[0]["country"],
            "lat": data[0]["lat"],
            "lon": data[0]["lon"],
        }
