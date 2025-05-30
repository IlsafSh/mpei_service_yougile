"""
Модель данных для вебхука.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Webhook(BaseModel):
    """Модель данных для вебхука."""
    
    id: str
    url: str
    event: str
    deleted: bool
    disabled: bool
    
    class Config:
        allow_population_by_field_name = True
