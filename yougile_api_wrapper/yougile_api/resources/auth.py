"""
Ресурс для работы с аутентификацией.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource


class AuthResource(BaseResource):
    """Ресурс для работы с аутентификацией."""
    
    def get_companies(self, login: str, password: str, name: Optional[str] = None, 
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получить список компаний.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            name: Название компании (опционально)
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            
        Returns:
            list: Список компаний
        """
        data = {
            'login': login,
            'password': password
        }
        
        if name:
            data['name'] = name
            
        params = {
            'limit': limit,
            'offset': offset
        }
        
        return self._client.request('POST', '/auth/companies', params=params, json=data)
    
    def get_keys(self, login: str, password: str, company_id: str) -> List[Dict[str, Any]]:
        """
        Получить список ключей.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            company_id: ID компании
            
        Returns:
            list: Список ключей
        """
        data = {
            'login': login,
            'password': password,
            'companyId': company_id
        }
        
        return self._client.request('POST', '/auth/keys/get', json=data)
    
    def create_key(self, login: str, password: str, company_id: str) -> Dict[str, Any]:
        """
        Создать ключ.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            company_id: ID компании
            
        Returns:
            dict: Созданный ключ
        """
        data = {
            'login': login,
            'password': password,
            'companyId': company_id
        }
        
        return self._client.request('POST', '/auth/keys', json=data)
    
    def delete_key(self, key: str) -> Dict[str, Any]:
        """
        Удалить ключ.
        
        Args:
            key: Ключ
            
        Returns:
            dict: Результат операции
        """
        return self._client.request('DELETE', f'/auth/keys/{key}')
