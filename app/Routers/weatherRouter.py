import os
from tracemalloc import start
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from app.supabase import supabase

load_dotenv()

router = APIRouter(prefix="/api/weather", tags=["Weather"])

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@router.get("/search/by-city")
async def search_by_city(
    city: str,
    country: str,
    state: str | None = None
):
    geo_query = f"{city},{state},{country}" if state else f"{city},{country}"

    geo_url = (
        "https://api.openweathermap.org/geo/1.0/direct"
        f"?q={geo_query}&limit=1&appid={OPENWEATHER_API_KEY}"
    )

    search_id = None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            #GEO 
            geo_response = await client.get(geo_url)
            if geo_response.status_code != 200:
                raise HTTPException(
                    status_code=geo_response.status_code,
                    detail="Geocoding API error"
                )

            geo_data = geo_response.json()
            if not geo_data:
                raise HTTPException(status_code=404, detail="City not found")

            geo = geo_data[0]
            lat = geo["lat"]
            lon = geo["lon"]

            #WEATHER
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

        searched_at = datetime.now(timezone.utc).isoformat()

        # -------- INSERT SEARCH --------
        search_insert = supabase.table("weather_searches").insert({
            "city": geo["name"],
            "state": geo.get("state"),
            "country": geo["country"],
            "lat": lat,
            "lon": lon,
            "created_at": searched_at,
            "start_date": searched_at,
            "end_date": searched_at
        }).execute()

        search_id = search_insert.data[0]["id"]

        # -------- INSERT RESULT --------
        supabase.table("weather_results").insert({
            "search_id": search_id,
            "forecast_datetime": searched_at,
            "temp": weather["main"]["temp"],
            "feels_like": weather["main"]["feels_like"],
            "humidity": weather["main"]["humidity"],
            "description": weather["weather"][0]["description"],
            "wind_speed": weather["wind"]["speed"]
        }).execute()

    #HTTP ERRORS 
    except HTTPException:
        
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()
        raise

    #UNEXPECTED ERRORS 
    except Exception as e:
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()

        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed, rolled back: {str(e)}"
        )

    
    return {
        "search_id": search_id,
        "location": {
            "city": geo["name"],
            "state": geo.get("state"),
            "country": geo["country"],
            "lat": lat,
            "lon": lon
        },
        "weather": {
            "temp": weather["main"]["temp"],
            "feels_like": weather["main"]["feels_like"],
            "humidity": weather["main"]["humidity"],
            "description": weather["weather"][0]["description"],
            "wind_speed": weather["wind"]["speed"]
        }
    }



#===============================================================================================================================================================






@router.get("/search/by-zip")
async def search_by_zip(zip_code: str, country: str):
    """
    Exemple:
    /api/weather/search/by-zip?zip_code=75001&country=FR
    """

    search_id = None

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?zip={zip_code},{country}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    try:
        # WEATHER API
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Weather API error"
                )

            data = response.json()

        searched_at = datetime.now(timezone.utc).isoformat()

        
        search_insert = supabase.table("weather_searches").insert({
            "city": data.get("name"),
            "state": data.get("state") if "state" in data else None,
            "country": data["sys"]["country"],
            "zip_code": zip_code,
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "created_at": searched_at,
            "start_date": searched_at,
            "end_date": searched_at
        }).execute()

        search_id = search_insert.data[0]["id"]

       
        supabase.table("weather_results").insert({
            "search_id": search_id,
            "forecast_datetime": searched_at,
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }).execute()

    
    except HTTPException:
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()
        raise

    
    except Exception as e:
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()

        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed, rolled back: {str(e)}"
        )

   
    return {
        "search_id": search_id,
        "location": {
            "city": data.get("name"),
            "country": data["sys"]["country"],
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"]
        },
        "weather": {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
    }


#===============================================================================================================================================================


@router.get("/search/by-coords")
async def search_by_coords(lat: float, lon: float):
    """
    Exemple:
    /api/weather/search/by-coords?lat=48.8566&lon=2.3522
    """

    search_id = None

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    try:
        #WEATHER
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Weather API error"
                )

            data = response.json()

        searched_at = datetime.now(timezone.utc).isoformat()

        
        search_insert = supabase.table("weather_searches").insert({
            "city": data.get("name"),
            "state": data.get("state") if "state" in data else None,
            "country": data["sys"]["country"],
            "lat": lat,
            "lon": lon,
            "created_at": searched_at,
            "start_date": searched_at,
            "end_date": searched_at
        }).execute()

        search_id = search_insert.data[0]["id"]

        
        supabase.table("weather_results").insert({
            "search_id": search_id,
            "forecast_datetime": searched_at,
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }).execute()

    #HTTP ERRORS
    except HTTPException:
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()
        raise

    #UNEXPECTED ERRORS
    except Exception as e:
        if search_id:
            supabase.table("weather_searches") \
                .delete() \
                .eq("id", search_id) \
                .execute()

        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed, rolled back: {str(e)}"
        )

    
    return {
        "search_id": search_id,
        "location": {
            "city": data.get("name"),
            "country": data["sys"]["country"],
            "lat": lat,
            "lon": lon
        },
        "weather": {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
    }







#===============================================================================================================================================================


@router.get("/weather/by-city-range")
async def weather_by_city_range(
    city: str,
    country: str,
    state: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None
):
    search_id = None 

    try:
       
        #date 
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.utcnow().date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else start + timedelta(days=5)
        except ValueError:
            raise HTTPException(400, "Invalid date format (YYYY-MM-DD)")

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

            
            #WEATHER FORECAST
            
            weather_url = (
                f"https://api.openweathermap.org/data/2.5/forecast"
                f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            )

            weather_resp = await client.get(weather_url)

            if weather_resp.status_code != 200:
                raise HTTPException(500, "Weather API error")

            forecast = weather_resp.json()["list"]

        
        #INSERT search in history
       
        search_insert = supabase.table("weather_searches").insert({
            "city": geo["name"],
            "state": geo.get("state"),
            "country": geo["country"],
            "lat": lat,
            "lon": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat() ,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        search_id = search_insert.data[0]["id"]

        
        #FILTER + INSERT RESULTS
        
        results = []
        weather_rows = []

        for item in forecast:
            item_date = datetime.fromtimestamp(item["dt"]).date()

            if not (start <= item_date <= end):
                continue
            
            row = {
                "search_id": search_id,
                "forecast_datetime": item["dt_txt"],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"]
            }

            weather_rows.append(row)

            results.append({
                "datetime": item["dt_txt"],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"]
            })

    
        if weather_rows:
            supabase.table("weather_results").insert(weather_rows).execute()

        return {
            "city": geo["name"],
            "state": geo.get("state"),
            "country": geo["country"],
            "lat": lat,
            "lon": lon,
            "count": len(results),
            "data": results
        }

    except Exception as e:
        
        #    rollback
        
        if search_id:
            supabase.table("weather_results").delete().eq("search_id", search_id).execute()
            supabase.table("weather_searches").delete().eq("id", search_id).execute()

        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed, rolled back: {str(e)}"
        )