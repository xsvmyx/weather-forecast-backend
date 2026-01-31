from pydantic import BaseModel
from typing import Optional


class WeatherSearchUpdate(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    start_date: Optional[str] = None  # ou date
    end_date: Optional[str] = None    # ou date