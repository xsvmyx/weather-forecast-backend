import os
import httpx
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@router.get("/search_locations")
async def search_locations(query: str, max_results: int = 5):

    query = f"{query} travel tourism places to visit" #to show only travel related videos

    youtube_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(youtube_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="YouTube API error"
            )

        data = response.json()



        videos = []

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            videos.append({
                "title": snippet["title"],
                "description": snippet["description"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })
        
        return {
            "total_results": len(videos),
            "videos": videos
        }
    



@router.get("/search_weather")
async def search_weather(query: str, max_results: int = 5):

    query = f"{query} weather forecast" #to show only weather related videos

    youtube_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(youtube_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="YouTube API error"
            )

        data = response.json()



        videos = []

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            videos.append({
                "title": snippet["title"],
                "description": snippet["description"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })
        
        return {
            "total_results": len(videos),
            "videos": videos
        }