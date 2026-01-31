import os
from fastapi import APIRouter, HTTPException , Query
from app.supabase import supabase
from datetime import datetime
router = APIRouter(prefix="/api/weather/crud", tags=["Weather Crud"])





@router.get("/history")
async def get_all_history():

    try:
        
        searches_response = supabase.table("weather_searches").select("*").execute()
        
        if not searches_response.data:
            return {
                "total": 0,
                "searches": []
            }
        
        
        result = []
        for search in searches_response.data:
            
            results_response = supabase.table("weather_results").select("*").eq("search_id", search["id"]).execute()
            
            result.append({
                "id": search["id"],
                "city": search["city"],
                "state": search["state"],
                "country": search["country"],
                "coordinates": {
                    "lat": search["lat"],
                    "lon": search["lon"]
                },
                "start_date": search["start_date"],
                "end_date": search["end_date"],
                "created_at": search["created_at"],
                "weather_data": results_response.data
            })
        
        return {
            "total": len(result),
            "searches": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")




@router.get("/history/{search_id}")
async def get_history_by_id(search_id: int):

    try:
       
        search_response = supabase.table("weather_searches").select("*").eq("id", search_id).execute()
        
        if not search_response.data:
            raise HTTPException(status_code=404, detail=f"Search with id {search_id} not found")
        
        search = search_response.data[0]
        
        
        results_response = supabase.table("weather_results").select("*").eq("search_id", search_id).execute()
        
        return {
            "id": search["id"],
            "city": search["city"],
            "state": search["state"],
            "country": search["country"],
            "coordinates": {
                "lat": search["lat"],
                "lon": search["lon"]
            },
            "start_date": search["start_date"],
            "end_date": search["end_date"],
            "created_at": search["created_at"],
            "weather_data": results_response.data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")




@router.delete("/history/{search_id}")
async def delete_history(search_id: int):

    try:
       
        search_response = supabase.table("weather_searches").select("*").eq("id", search_id).execute()
        
        if not search_response.data:
            raise HTTPException(status_code=404, detail=f"Search with id {search_id} not found")
        
        search = search_response.data[0]
        
       
        supabase.table("weather_results").delete().eq("search_id", search_id).execute()
        
        
        supabase.table("weather_searches").delete().eq("id", search_id).execute()
        
        return {
            "message": "Search deleted successfully",
            "deleted_search": {
                "id": search["id"],
                "city": search["city"],
                "country": search["country"],
                "created_at": search["created_at"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@router.delete("/history/all")
async def delete_all_history():

    try:
        
        supabase.table("weather_results").delete().neq("search_id", -1).execute()
        
        supabase.table("weather_searches").delete().neq("id", -1).execute()

        return {
            "message": "All searches and results deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history/search/country")
async def search_history_by_country(
    country: str = Query(..., min_length=1, description="Country name to search for")
):
    """Search weather history by country"""
    
    print(f"Searching history by country: {country}")
    
    try:
        searches_response = (
            supabase
            .table("weather_searches")
            .select("*")
            .ilike("country", f"%{country}%")
            .execute()
        )

        if not searches_response.data:
            return {
                "total": 0,
                "filter": {"country": country},
                "searches": []
            }

        result = []
        for search in searches_response.data:
            results_response = (
                supabase
                .table("weather_results")
                .select("*")
                .eq("search_id", search["id"])
                .execute()
            )

            result.append({
                "id": search["id"],
                "city": search["city"],
                "state": search["state"],
                "country": search["country"],
                "coordinates": {
                    "lat": search["lat"],
                    "lon": search["lon"]
                },
                "start_date": search["start_date"],
                "end_date": search["end_date"],
                "created_at": search["created_at"],
                "weather_data": results_response.data
            })

        return {
            "total": len(result),
            "filter": {"country": country},
            "searches": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history/search/city")
async def search_history_by_city(
    city: str = Query(..., min_length=1, description="City name to search for")
):
    """Search weather history by city"""
    
    print(f"Searching history by city: {city}")
    
    try:
        searches_response = (
            supabase
            .table("weather_searches")
            .select("*")
            .ilike("city", f"%{city}%")
            .execute()
        )

        if not searches_response.data:
            return {
                "total": 0,
                "filter": {"city": city},
                "searches": []
            }

        result = []
        for search in searches_response.data:
            results_response = (
                supabase
                .table("weather_results")
                .select("*")
                .eq("search_id", search["id"])
                .execute()
            )

            result.append({
                "id": search["id"],
                "city": search["city"],
                "state": search["state"],
                "country": search["country"],
                "coordinates": {
                    "lat": search["lat"],
                    "lon": search["lon"]
                },
                "start_date": search["start_date"],
                "end_date": search["end_date"],
                "created_at": search["created_at"],
                "weather_data": results_response.data
            })

        return {
            "total": len(result),
            "filter": {"city": city},
            "searches": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history/search/state")
async def search_history_by_state(
    state: str = Query(..., min_length=1, description="State name to search for")
):
    """Search weather history by state"""
    
    print(f"Searching history by state: {state}")
    
    try:
        # Handle null/none case
        if state.lower() in ("null", "none"):
            searches_response = (
                supabase
                .table("weather_searches")
                .select("*")
                .is_("state", None)
                .execute()
            )
        else:
            searches_response = (
                supabase
                .table("weather_searches")
                .select("*")
                .ilike("state", f"%{state}%")
                .execute()
            )

        if not searches_response.data:
            return {
                "total": 0,
                "filter": {"state": state},
                "searches": []
            }

        result = []
        for search in searches_response.data:
            results_response = (
                supabase
                .table("weather_results")
                .select("*")
                .eq("search_id", search["id"])
                .execute()
            )

            result.append({
                "id": search["id"],
                "city": search["city"],
                "state": search["state"],
                "country": search["country"],
                "coordinates": {
                    "lat": search["lat"],
                    "lon": search["lon"]
                },
                "start_date": search["start_date"],
                "end_date": search["end_date"],
                "created_at": search["created_at"],
                "weather_data": results_response.data
            })

        return {
            "total": len(result),
            "filter": {"state": state},
            "searches": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history/search/zipcode")
async def search_history_by_zipcode(
    zipcode: str = Query(..., min_length=1, description="Zipcode to search for")
):
    """Search weather history by zipcode"""
    
    print(f"Searching history by zipcode: {zipcode}")
    
    try:
        searches_response = (
            supabase
            .table("weather_searches")
            .select("*")
            .ilike("zip_code", f"%{zipcode}%")
            .execute()
        )

        if not searches_response.data:
            return {
                "total": 0,
                "filter": {"zip_code": zipcode},
                "searches": []
            }

        result = []
        for search in searches_response.data:
            results_response = (
                supabase
                .table("weather_results")
                .select("*")
                .eq("search_id", search["id"])
                .execute()
            )

            result.append({
                "id": search["id"],
                "city": search["city"],
                "state": search["state"],
                "country": search["country"],
                "zip_code": search.get("zip_code"),
                "coordinates": {
                    "lat": search["lat"],
                    "lon": search["lon"]
                },
                "start_date": search["start_date"],
                "end_date": search["end_date"],
                "created_at": search["created_at"],
                "weather_data": results_response.data
            })

        return {
            "total": len(result),
            "filter": {"zipcode": zipcode},
            "searches": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    











# ==================== UPDATE ENDPOINT ====================
from app.Schemas.WeatherSchemas import WeatherSearchUpdate
@router.put("/history/{search_id}")
async def update_history(search_id: int, updates: WeatherSearchUpdate):
    try:
        
        search_response = supabase.table("weather_searches").select("*").eq("id", search_id).execute()
        if not search_response.data:
            raise HTTPException(status_code=404, detail=f"Search with id {search_id} not found")

        
        update_data = {}

        if updates.city is not None:
            update_data["city"] = updates.city
        if updates.state is not None:
            update_data["state"] = updates.state
        if updates.country is not None:
            update_data["country"] = updates.country
        if updates.zip_code is not None:
            update_data["zip_code"] = updates.zip_code
        if updates.lat is not None:
            update_data["lat"] = updates.lat
        if updates.lon is not None:
            update_data["lon"] = updates.lon

        
        if updates.start_date is not None:
            try:
                dt = datetime.fromisoformat(updates.start_date)
                update_data["start_date"] = dt.date().isoformat()
            except ValueError:
                try:
                    dt = datetime.strptime(updates.start_date, "%Y-%m-%d")
                    update_data["start_date"] = dt.date().isoformat()
                except ValueError:
                    raise HTTPException(400, "start_date must be YYYY-MM-DD or ISO datetime")

        if updates.end_date is not None:
            try:
                dt = datetime.fromisoformat(updates.end_date)
                update_data["end_date"] = dt.date().isoformat()
            except ValueError:
                try:
                    dt = datetime.strptime(updates.end_date, "%Y-%m-%d")
                    update_data["end_date"] = dt.date().isoformat()
                except ValueError:
                    raise HTTPException(400, "end_date must be YYYY-MM-DD or ISO datetime")

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        
        updated_response = supabase.table("weather_searches").update(update_data).eq("id", search_id).execute()
        if not updated_response.data:
            raise HTTPException(status_code=500, detail="Update failed")

        return {
            "message": "Search updated successfully",
            "updated_fields": list(update_data.keys()),
            "search": updated_response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")