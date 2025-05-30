"""
Модель данных для сообщения чата.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Модель данных для сообщения чата."""
    
    id: Optional[str] = None
    text: str
    text_html: str = Field(alias="textHtml")
    label: str
    deleted: Optional[bool] = None
    react: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
