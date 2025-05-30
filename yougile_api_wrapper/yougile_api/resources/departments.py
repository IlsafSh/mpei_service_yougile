"""
Ресурс для работы с отделами.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class DepartmentsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с отделами."""
    
    _base_url = '/departments'
    
    def list(self, include_deleted: Optional[bool] = None, limit: int = 50, 
             offset: int = 0, parent_id: Optional[str] = None, 
             title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список отделов.
        
        Args:
            include_deleted: Включать удаленные отделы
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            parent_id: ID родительского отдела
            title: Имя отдела
            
        Returns:
            list: Список отделов
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if parent_id:
            params['parentId'] = parent_id
            
        if title:
            params['title'] = title
            
        return super().list(**params)
    
    def create(self, title: Optional[str] = None, parent_id: Optional[str] = None, 
               users: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Создать отдел.
        
        Args:
            title: Название отдела
            parent_id: Id родительского отдела
            users: Сотрудники на отделе и их роль
            
        Returns:
            dict: Созданный отдел
        """
        data = {}
        
        if title:
            data['title'] = title
            
        if parent_id:
            data['parentId'] = parent_id
            
        if users:
            data['users'] = users
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить отдел по ID.
        
        Args:
            id: ID отдела
            
        Returns:
            dict: Отдел
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, title: Optional[str] = None,
               parent_id: Optional[str] = None, users: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обновить отдел.
        
        Args:
            id: ID отдела
            deleted: Если true, значит объект удален
            title: Название отдела
            parent_id: Id родительского отдела
            users: Сотрудники на отделе и их роль
            
        Returns:
            dict: Обновленный отдел
        """
        data = {}
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if title:
            data['title'] = title
            
        if parent_id:
            data['parentId'] = parent_id
            
        if users:
            data['users'] = users
            
        return super().update(id, **data)
