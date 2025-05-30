"""
Ресурс для работы с колонками.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class ColumnsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с колонками."""
    
    _base_url = '/columns'
    
    def list(self, board_id: Optional[str] = None, include_deleted: Optional[bool] = None,
             limit: int = 50, offset: int = 0, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список колонок.
        
        Args:
            board_id: ID доски
            include_deleted: Включать удаленные колонки
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            title: Имя колонки
            
        Returns:
            list: Список колонок
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if board_id:
            params['boardId'] = board_id
            
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if title:
            params['title'] = title
            
        return super().list(**params)
    
    def create(self, title: str, board_id: str, color: Optional[int] = None) -> Dict[str, Any]:
        """
        Создать колонку.
        
        Args:
            title: Название колонки
            board_id: Id доски, в которой находится колонка
            color: Цвет колонки
            
        Returns:
            dict: Созданная колонка
        """
        data = {
            'title': title,
            'boardId': board_id
        }
        
        if color is not None:
            data['color'] = color
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить колонку по ID.
        
        Args:
            id: ID колонки
            
        Returns:
            dict: Колонка
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, title: Optional[str] = None,
               color: Optional[int] = None, board_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Обновить колонку.
        
        Args:
            id: ID колонки
            deleted: Если true, значит объект удален
            title: Название колонки
            color: Цвет колонки
            board_id: Id доски, в которой находится колонка
            
        Returns:
            dict: Обновленная колонка
        """
        data = {}
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if title:
            data['title'] = title
            
        if color is not None:
            data['color'] = color
            
        if board_id:
            data['boardId'] = board_id
            
        return super().update(id, **data)
