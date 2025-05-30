"""
Модель данных для колонки.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Column(BaseModel):
    """Модель данных для колонки."""
    
    id: Optional[str] = None
    title: str
    board_id: str = Field(alias="boardId")
    color: Optional[int] = None
    deleted: Optional[bool] = None
    
    class Config:
        allow_population_by_field_name = True
