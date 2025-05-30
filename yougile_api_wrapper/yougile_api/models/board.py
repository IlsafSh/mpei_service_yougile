"""
Модель данных для доски.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Board(BaseModel):
    """Модель данных для доски."""
    
    id: Optional[str] = None
    title: str
    project_id: str = Field(alias="projectId")
    stickers: Optional[Dict[str, Any]] = None
    deleted: Optional[bool] = None
    
    class Config:
        allow_population_by_field_name = True
