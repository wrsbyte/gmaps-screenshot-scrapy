from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class TargetLocationModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    folder: str
    address: Optional[str] = None
    link: Optional[str] = None
    latitude: float
    longitude: float

    gmaps_zoom: int
    gmaps_extra_params: Optional[Dict[str, Any]] = None

    active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
