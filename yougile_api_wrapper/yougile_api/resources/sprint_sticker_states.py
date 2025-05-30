"""
Ресурс для работы с состояниями стикеров спринта.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, NestedResourceMixin


class SprintStickerStatesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с состояниями стикеров спринта."""
    
    _base_url = '/sprint-stickers/{parent_id}/states'
    
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
            
        url = f"{self._get_url(sticker_id)}/{state_id}"
        return self._client.request('GET', url, params=params)
    
    def update(self, sticker_id: str, state_id: str, deleted: Optional[bool] = None,
               name: Optional[str] = None, begin: Optional[int] = None,
               end: Optional[int] = None) -> Dict[str, Any]:
        """
        Обновить состояние.
        
        Args:
            sticker_id: ID стикера
            state_id: ID состояния стикера
            deleted: Если true, значит объект удален
            name: Имя состояния стикера
            begin: Дата начала спринта в секундах от 01.01.1970
            end: Дата окончания спринта в секундах от 01.01.1970
            
        Returns:
            dict: Обновленное состояние
        """
        data = {}
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if name:
            data['name'] = name
            
        if begin is not None:
            data['begin'] = begin
            
        if end is not None:
            data['end'] = end
            
        url = f"{self._get_url(sticker_id)}/{state_id}"
        return self._client.request('PUT', url, json=data)
    
    def create(self, sticker_id: str, name: str, begin: Optional[int] = None,
               end: Optional[int] = None) -> Dict[str, Any]:
        """
        Создать состояние.
        
        Args:
            sticker_id: ID стикера
            name: Имя состояния стикера
            begin: Дата начала спринта в секундах от 01.01.1970
            end: Дата окончания спринта в секундах от 01.01.1970
            
        Returns:
            dict: Созданное состояние
        """
        data = {
            'name': name
        }
        
        if begin is not None:
            data['begin'] = begin
            
        if end is not None:
            data['end'] = end
            
        return super().create(sticker_id, **data)
