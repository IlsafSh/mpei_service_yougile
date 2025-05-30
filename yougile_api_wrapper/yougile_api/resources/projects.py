"""
Ресурс для работы с проектами.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class ProjectsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с проектами."""
    
    _base_url = '/projects'
    
    def list(self, include_deleted: Optional[bool] = None, limit: int = 50, 
             offset: int = 0, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список проектов.
        
        Args:
            include_deleted: Включать удаленные проекты
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            title: Имя проекта
            
        Returns:
            list: Список проектов
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if title:
            params['title'] = title
            
        return super().list(**params)
    
    def create(self, title: str, users: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Создать проект.
        
        Args:
            title: Название проекта
            users: Сотрудники на проекте и их роль
            
        Returns:
            dict: Созданный проект
        """
        data = {
            'title': title
        }
        
        if users:
            data['users'] = users
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить проект по ID.
        
        Args:
            id: ID проекта
            
        Returns:
            dict: Проект
        """
        return super().get(id)
    
    def update(self, id: str, title: str, deleted: Optional[bool] = None,
               users: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обновить проект.
        
        Args:
            id: ID проекта
            title: Название проекта
            deleted: Если true, значит объект удален
            users: Сотрудники на проекте и их роль
            
        Returns:
            dict: Обновленный проект
        """
        data = {
            'title': title
        }

        if deleted is not None:
            data['deleted'] = deleted
            
        if users:
            data['users'] = users
            
        return super().update(id, **data)
