"""
Ресурс для работы с состояниями строковых стикеров.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, NestedResourceMixin


class StringStickerStatesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с состояниями строковых стикеров."""
    
    _base_url = '/string-stickers/{parent_id}/states'
    
    def get(self, sticker_id: str, state_id: str, include_deleted: Optional[bool] = None) -> Dict[str, Any]:
        """
        Получить состояние по ID.
        
        Args:
            sticker_id: ID стикера
            state_id: ID состояния стикера
            include_deleted: Включать удаленные состояния
            
        Returns:
            dict: Состояние стикера
        """
        params = {}
        
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        return super().get(sticker_id, state_id)
    
    def update(self, sticker_id: str, state_id: str, deleted: Optional[bool] = None,
               name: Optional[str] = None, color: Optional[int] = None) -> Dict[str, Any]:
        """
        Обновить состояние.
        
        Args:
            sticker_id: ID стикера
            state_id: ID состояния стикера
            deleted: Если true, значит объект удален
            name: Имя состояния стикера
            color: Цвет состояния
            
        Returns:
            dict: Обновленное состояние
        """
        data = {}
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if name:
            data['name'] = name
            
        if color is not None:
            data['color'] = color
            
        url = f"{self._get_url(sticker_id)}/{state_id}"
        return self._client.request('PUT', url, json=data)
    
    def create(self, sticker_id: str, name: str, color: Optional[int] = None) -> Dict[str, Any]:
        """
        Создать состояние.
        
        Args:
            sticker_id: ID стикера
            name: Имя состояния стикера
            color: Цвет состояния
            
        Returns:
            dict: Созданное состояние
        """
        data = {
            'name': name
        }
        
        if color is not None:
            data['color'] = color
            
        return super().create(sticker_id, **data)
