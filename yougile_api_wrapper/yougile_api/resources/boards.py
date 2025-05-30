"""
Ресурс для работы с досками.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class BoardsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с досками."""
    
    _base_url = '/boards'
    
    def list(self, include_deleted: Optional[bool] = None, limit: int = 50, 
             offset: int = 0, project_id: Optional[str] = None, 
             title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список досок.
        
        Args:
            include_deleted: Включать удаленные доски
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            project_id: ID проекта
            title: Имя доски
            
        Returns:
            list: Список досок
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if project_id:
            params['projectId'] = project_id
            
        if title:
            params['title'] = title
            
        return super().list(**params)
    
    def create(self, title: str, project_id: str, stickers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Создать доску.
        
        Args:
            title: Название доски
            project_id: Id проекта, в котором находится доска
            stickers: Стикеры доски
            
        Returns:
            dict: Созданная доска
        """
        data = {
            'title': title,
            'projectId': project_id
        }
        
        if stickers:
            data['stickers'] = stickers
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить доску по ID.
        
        Args:
            id: ID доски
            
        Returns:
            dict: Доска
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, title: Optional[str] = None,
               project_id: Optional[str] = None, stickers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обновить доску.
        
        Args:
            id: ID доски
            deleted: Если true, значит объект удален
            title: Название доски
            project_id: Id проекта, в котором находится доска
            stickers: Стикеры доски
            
        Returns:
            dict: Обновленная доска
        """
        data = {}

        if deleted:
            data['deleted'] = deleted

        if title:
            data['title'] = title

        if project_id:
            data['projectId'] = project_id

        if stickers:
            data['stickers'] = stickers
        
        return super().update(id, **data)
