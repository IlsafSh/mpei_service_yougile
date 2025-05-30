"""
Модель данных для отдела.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Department(BaseModel):
    """Модель данных для отдела."""
    
    id: Optional[str] = None
    title: Optional[str] = None
    parent_id: Optional[str] = Field(None, alias="parentId")
    users: Optional[Dict[str, Any]] = None
    deleted: Optional[bool] = None
    
    class Config:
        allow_population_by_field_name = True
