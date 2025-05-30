"""
Модель данных для стикера спринта.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SprintSticker(BaseModel):
    """Модель данных для стикера спринта."""
    
    id: Optional[str] = None
    name: str
    states: List[Dict[str, Any]]
    deleted: Optional[bool] = None
    
    class Config:
        allow_population_by_field_name = True
