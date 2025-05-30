"""
Ресурс для работы с групповыми чатами.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class GroupChatsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с групповыми чатами."""
    
    _base_url = '/group-chats'
    
    def list(self, include_deleted: Optional[bool] = None, limit: int = 50, 
             offset: int = 0, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список чатов.
        
        Args:
            include_deleted: Включать удаленные чаты
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            title: Имя чата
            
        Returns:
            list: Список чатов
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
    
    def create(self, title: str, users: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать чат.
        
        Args:
            title: Название чата
            users: Сотрудники в чате
            
        Returns:
            dict: Созданный чат
        """
        data = {
            'title': title,
            'users': users
        }
        
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить чат по ID.
        
        Args:
            id: ID чата
            
        Returns:
            dict: Чат
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, title: Optional[str] = None,
               users: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обновить чат.
        
        Args:
            id: ID чата
            deleted: Если true, значит объект удален
            title: Название чата
            users: Сотрудники в чате
            
        Returns:
            dict: Обновленный чат
        """
        data = {
            'users': users
        }

        if deleted is not None:
            data['deleted'] = deleted

        if title is not None:
            data['title'] = title

        if users is not None:
            data['users'] = users
        
        return super().update(id, **data)
