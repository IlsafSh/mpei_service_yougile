"""
Ресурс для работы с вебхуками.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class WebhooksResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с вебхуками."""
    
    _base_url = '/webhooks'
    
    def list(self, event: Optional[str] = None, limit: int = 50, 
             offset: int = 0, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список подписок.
        
        Args:
            event: Событие
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            url: URL
            
        Returns:
            list: Список подписок
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if event:
            params['event'] = event
            
        if url:
            params['url'] = url
            
        return super().list(**params)
    
    def create(self, url: str, event: str) -> Dict[str, Any]:
        """
        Создать подписку.
        
        Args:
            url: URL
            event: Событие
            
        Returns:
            dict: Созданная подписка
        """
        data = {
            'url': url,
            'event': event
        }
        
        return super().create(**data)
    
    def update(self, id: str, deleted: Optional[bool] = None, url: Optional[str] = None, 
               event: Optional[str] = None, disabled: Optional[bool] = None) -> Dict[str, Any]:
        """
        Обновить подписку.
        
        Args:
            id: ID подписки
            url: URL
            event: Событие
            
        Returns:
            dict: Обновленная подписка
        """
        data = {}
        
        if url:
            data['url'] = url
            
        if event:
            data['event'] = event

        if deleted:
            data['deleted'] = deleted

        if disabled:
            data['disabled'] = disabled
            
        return super().update(id, **data)
