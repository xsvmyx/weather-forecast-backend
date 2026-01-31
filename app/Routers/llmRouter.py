import os
from click import prompt
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import httpx

router = APIRouter(prefix="/api/llm", tags=["LLM"])
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@router.post("/desc_climate")
async def desc_climate(
    city: str, 
    country: str,
    state: str | None = None
    ):
    
    
    if not GROQ_API_KEY:
        raise HTTPException(500, "Groq API key not configured")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a climate expert. Provide short, factual descriptions."
            },
            {
                "role": "user",
                "content": f"Describe the climate of {city}, {country} ,{state if state else ''} in under 3 sentences."
            }
        ],
        "model": "llama-3.3-70b-versatile", 
        "temperature": 0.7,
        "max_tokens": 150
    }

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Groq error: {response.text}"
            )

        data = response.json()
        description = data["choices"][0]["message"]["content"].strip()

        return {
            "city": city,
            "country": country,
            "climate_description": description,
            "provider": "groq"
        }
    





@router.post("/desc_locations")
async def desc_locations(
    city: str, 
    country: str,
    state: str | None = None
    ):
    
    
    if not GROQ_API_KEY:
        raise HTTPException(500, "Groq API key not configured")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a places expert. Provide short, factual descriptions."
            },
            {
                "role": "user",
                "content": f"Describe the places of interest in {city}, {country} ,{state if state else ''} in under 3 sentences."
            }
        ],
        "model": "llama-3.3-70b-versatile", 
        "temperature": 0.7,
        "max_tokens": 150
    }

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Groq error: {response.text}"
            )

        data = response.json()
        description = data["choices"][0]["message"]["content"].strip()

        return {
            "city": city,
            "country": country,
            "climate_description": description,
            "provider": "groq"
        }