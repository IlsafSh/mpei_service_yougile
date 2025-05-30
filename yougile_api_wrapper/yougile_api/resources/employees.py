"""
Ресурс для работы с сотрудниками.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class EmployeesResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с сотрудниками."""
    
    _base_url = '/users'
    
    def list(self, email: Optional[str] = None, limit: int = 50, 
             offset: int = 0, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список сотрудников.
        
        Args:
            email: Почта сотрудника
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            project_id: ID проекта
            
        Returns:
            list: Список сотрудников
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if email:
            params['email'] = email
            
        if project_id:
            params['projectId'] = project_id
            
        return super().list(**params)
    
    def create(self, email: str, is_admin: Optional[bool] = None) -> Dict[str, Any]:
        """
        Пригласить сотрудника в компанию.
        
        Args:
            email: Почтовый ящик сотрудника
            is_admin: Имеет ли пользователь права администратора
            
        Returns:
            dict: Результат операции
        """
        data = {
            'email': email
        }
        
        if is_admin is not None:
            data['isAdmin'] = is_admin
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить сотрудника по ID.
        
        Args:
            id: ID сотрудника
            
        Returns:
            dict: Сотрудник
        """
        return super().get(id)
    
    def update(self, id: str, is_admin: Optional[bool] = None) -> Dict[str, Any]:
        """
        Обновить сотрудника.
        
        Args:
            id: ID сотрудника
            is_admin: Имеет ли пользователь права администратора
            
        Returns:
            dict: Обновленный сотрудник
        """
        data = {}
        
        if is_admin is not None:
            data['isAdmin'] = is_admin
            
        return super().update(id, **data)
    
    def delete(self, id: str) -> Dict[str, Any]:
        """
        Удалить сотрудника из компании.
        
        Args:
            id: ID сотрудника
            
        Returns:
            dict: Результат операции
        """
        return super().delete(id)
