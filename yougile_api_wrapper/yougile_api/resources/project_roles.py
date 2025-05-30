"""
Ресурс для работы с ролями проекта.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, NestedResourceMixin


class ProjectRolesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с ролями проекта."""
    
    _base_url = '/projects/{parent_id}/roles'
    
    def list(self, project_id: str, limit: int = 50, name: Optional[str] = None,
             offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получить список ролей.
        
        Args:
            project_id: ID проекта
            limit: Количество элементов (по умолчанию 50)
            name: Имя роли
            offset: Индекс первого элемента (по умолчанию 0)
            
        Returns:
            list: Список ролей
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if name:
            params['name'] = name
            
        return super().list(project_id, **params)
    
    def create(self, project_id: str, name: str, permissions: Dict[str, Any],
               description: Optional[str] = None) -> Dict[str, Any]:
        """
        Создать роль.
        
        Args:
            project_id: ID проекта
            name: Название роли
            permissions: Права в проекте
            description: Описание роли
            
        Returns:
            dict: Созданная роль
        """
        data = {
            'name': name,
            'permissions': permissions
        }
        
        if description:
            data['description'] = description
            
        return super().create(project_id, **data)
    
    def get(self, project_id: str, id: str) -> Dict[str, Any]:
        """
        Получить роль по ID.
        
        Args:
            project_id: ID проекта
            id: ID роли проекта
            
        Returns:
            dict: Роль
        """
        return super().get(project_id, id)
    
    def update(self, project_id: str, id: str, name: Optional[str] = None,
               description: Optional[str] = None, permissions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обновить роль.
        
        Args:
            project_id: ID проекта
            id: ID роли проекта
            name: Название роли
            description: Описание роли
            permissions: Права в проекте
            
        Returns:
            dict: Обновленная роль
        """
        data = {}
        
        if name:
            data['name'] = name
            
        if description:
            data['description'] = description
            
        if permissions:
            data['permissions'] = permissions
            
        return super().update(project_id, id, **data)
    
    def delete(self, project_id: str, id: str) -> Dict[str, Any]:
        """
        Удалить роль.
        
        Args:
            project_id: ID проекта
            id: ID роли проекта
            
        Returns:
            dict: Результат операции
        """
        return super().delete(project_id, id)
