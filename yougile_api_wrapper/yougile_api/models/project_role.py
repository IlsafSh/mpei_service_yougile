"""
Модель данных для роли проекта.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ProjectRole(BaseModel):
    """Модель данных для роли проекта."""
    
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any]
    
    class Config:
        allow_population_by_field_name = True
