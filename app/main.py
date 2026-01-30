from fastapi import FastAPI
from app.Routers.weatherRouter import router as weather_router
from app.Routers.mapsRouter import router as maps_router
from app.Routers.llmRouter import router as llm_router
from app.Routers.youtubeRouter import router as youtube_router

app = FastAPI(title="Weather API")

@app.get("/")
def read_root():
    return {"message": "Weather API is running!"}




app.include_router(weather_router)
app.include_router(maps_router)
app.include_router(llm_router)
app.include_router(youtube_router)