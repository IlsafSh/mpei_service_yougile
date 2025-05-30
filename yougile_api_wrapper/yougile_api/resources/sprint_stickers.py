"""
Ресурс для работы со стикерами спринта.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class SprintStickersResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы со стикерами спринта."""
    
    _base_url = '/sprint-stickers'
    
    def list(self, board_id: Optional[str] = None, include_deleted: Optional[bool] = None,
             limit: int = 50, name: Optional[str] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получить список стикеров.
        
        Args:
            board_id: ID доски
            include_deleted: Включать удаленные стикеры
            limit: Количество элементов (по умолчанию 50)
            name: Имя стикера
            offset: Индекс первого элемента (по умолчанию 0)
            
        Returns:
            list: Список стикеров
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if board_id:
            params['boardId'] = board_id
            
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if name:
            params['name'] = name
            
        return super().list(**params)
    
    def create(self, name: str, states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Создать стикер.
        
        Args:
            name: Имя стикера
            states: Состояния стикера
            
        Returns:
            dict: Созданный стикер
        """
        data = {
            'name': name,
            'states': states
        }
        
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить стикер по ID.
        
        Args:
            id: ID стикера спринта
            
        Returns:
            dict: Стикер
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Обновить стикер.
        
        Args:
            id: ID стикера спринта
            deleted: Если true, значит объект удален
            name: Имя стикера
            
        Returns:
            dict: Обновленный стикер
        """
        data = {}
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if name:
            data['name'] = name
            
        return super().update(id, **data)
