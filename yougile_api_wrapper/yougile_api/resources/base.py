"""
Базовый класс для всех ресурсов API.
"""
from typing import Dict, Any, Optional, List, Union


class BaseResource:
    """Базовый класс для всех ресурсов API."""
    
    def __init__(self, client):
        """
        Инициализация ресурса.
        
        Args:
            client: Экземпляр клиента API
        """
        self._client = client


class CRUDResourceMixin:
    """Миксин для ресурсов с CRUD операциями."""
    
    def list(self, **params) -> List[Dict[str, Any]]:
        """
        Получить список объектов.
        
        Args:
            **params: Параметры запроса
            
        Returns:
            list: Список объектов
        """
        return self._client.request('GET', self._base_url, params=params)
        
    def create(self, **data) -> Dict[str, Any]:
        """
        Создать новый объект.
        
        Args:
            **data: Данные для создания объекта
            
        Returns:
            dict: Созданный объект
        """
        return self._client.request('POST', self._base_url, json=data)
        
    def get(self, id: str, **params) -> Dict[str, Any]:
        """
        Получить объект по ID.
        
        Args:
            id: Идентификатор объекта
            **params: Дополнительные параметры запроса
            
        Returns:
            dict: Объект
        """
        url = f"{self._base_url}/{id}"
        return self._client.request('GET', url, params=params)
        
    def update(self, id: str, **data) -> Dict[str, Any]:
        """
        Обновить объект.
        
        Args:
            id: Идентификатор объекта
            **data: Данные для обновления
            
        Returns:
            dict: Обновленный объект
        """
        url = f"{self._base_url}/{id}"
        return self._client.request('PUT', url, json=data)
        
    def delete(self, id: str) -> Dict[str, Any]:
        """
        Удалить объект.
        
        Args:
            id: Идентификатор объекта
            
        Returns:
            dict: Результат операции
        """
        url = f"{self._base_url}/{id}"
        return self._client.request('DELETE', url)


class NestedResourceMixin:
    """Миксин для вложенных ресурсов."""
    
    def list(self, parent_id: str, **params) -> List[Dict[str, Any]]:
        """
        Получить список вложенных объектов.
        
        Args:
            parent_id: Идентификатор родительского объекта
            **params: Параметры запроса
            
        Returns:
            list: Список объектов
        """
        url = self._get_url(parent_id)
        return self._client.request('GET', url, params=params)
        
    def create(self, parent_id: str, **data) -> Dict[str, Any]:
        """
        Создать новый вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            **data: Данные для создания объекта
            
        Returns:
            dict: Созданный объект
        """
        url = self._get_url(parent_id)
        return self._client.request('POST', url, json=data)
        
    def get(self, parent_id: str, id: str, **params) -> Dict[str, Any]:
        """
        Получить вложенный объект по ID.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            **params: Дополнительные параметры запроса
            
        Returns:
            dict: Объект
        """
        url = f"{self._get_url(parent_id)}/{id}"
        return self._client.request('GET', url, params=params)
        
    def update(self, parent_id: str, id: str, **data) -> Dict[str, Any]:
        """
        Обновить вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            **data: Данные для обновления
            
        Returns:
            dict: Обновленный объект
        """
        url = f"{self._get_url(parent_id)}/{id}"
        return self._client.request('PUT', url, json=data)
        
    def delete(self, parent_id: str, id: str) -> Dict[str, Any]:
        """
        Удалить вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            
        Returns:
            dict: Результат операции
        """
        url = f"{self._get_url(parent_id)}/{id}"
        return self._client.request('DELETE', url)
    
    def _get_url(self, parent_id: str) -> str:
        """
        Получить URL для вложенного ресурса.
        
        Args:
            parent_id: Идентификатор родительского объекта
            
        Returns:
            str: URL
        """
        return self._base_url.format(parent_id=parent_id)
