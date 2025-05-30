"""
Ресурс для работы с сообщениями чата.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, NestedResourceMixin


class ChatMessagesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с сообщениями чата."""
    
    _base_url = '/chats/{parent_id}/messages'
    
    def list(self, chat_id: str, from_user_id: Optional[str] = None, 
             include_deleted: Optional[bool] = None, include_system: Optional[bool] = None,
             label: Optional[str] = None, limit: int = 50, offset: int = 0,
             since: Optional[int] = None, text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить историю сообщений.
        
        Args:
            chat_id: ID чата
            from_user_id: ID сотрудника от кого сообщение
            include_deleted: Включать удаленные сообщения
            include_system: Включать системные сообщения
            label: Поиск по быстрой ссылке сообщения
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            since: Искать среди сообщений, время создания которых позже указанного времени (timestamp)
            text: Строка, которую сообщение должно содержать
            
        Returns:
            list: История сообщений
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if from_user_id:
            params['fromUserId'] = from_user_id
            
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if include_system is not None:
            params['includeSystem'] = include_system
            
        if label:
            params['label'] = label
            
        if since:
            params['since'] = since
            
        if text:
            params['text'] = text
            
        return super().list(chat_id, **params)
    
    def create(self, chat_id: str, text: str, text_html: int, label: str) -> Dict[str, Any]:
        """
        Написать в чат.
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            text_html: Текст сообщения в формате HTML
            label: Быстрая ссылка
            
        Returns:
            dict: Созданное сообщение
        """
        data = {
            'text': text,
            'textHtml': text_html,
            'label': label
        }
        
        return super().create(chat_id, **data)
    
    def get(self, chat_id: str, id: str) -> Dict[str, Any]:
        """
        Получить сообщение по ID.
        
        Args:
            chat_id: ID чата
            id: ID сообщения
            
        Returns:
            dict: Сообщение
        """
        return super().get(chat_id, id)
    
    def update(self, chat_id: str, id: str, deleted: Optional[bool] = None,
               label: Optional[str] = None, react: str = '👍') -> Dict[str, Any]:
        """
        Изменить сообщение.
        
        Args:
            chat_id: ID чата
            id: ID сообщения
            deleted: Если true, значит объект удален
            label: Быстрая ссылка
            react: Список реакций админа
            
        Returns:
            dict: Обновленное сообщение
        """
        data = {
            'react': react
        }
        
        if deleted is not None:
            data['deleted'] = deleted
            
        if label:
            data['label'] = label
            
        return super().update(chat_id, id, **data)
