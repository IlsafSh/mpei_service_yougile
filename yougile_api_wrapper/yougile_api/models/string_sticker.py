"""
Модель данных для строкового стикера.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StringSticker(BaseModel):
    """Модель данных для строкового стикера."""
    
    id: Optional[str] = None
    name: str
    states: Optional[List[Dict[str, Any]]] = None
    icon: Optional[str] = None
    deleted: Optional[bool] = None
    
    class Config:
        allow_population_by_field_name = True
