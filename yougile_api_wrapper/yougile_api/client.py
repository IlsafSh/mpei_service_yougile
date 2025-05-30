"""
Клиент для работы с YouGile API.
"""
import requests
from typing import Dict, Any, Optional, List, Union
from .exceptions import YouGileApiError, YouGileAuthError, YouGileNotFoundError

# Импорт ресурсов
from .resources.auth import AuthResource
from .resources.boards import BoardsResource
from .resources.chat_messages import ChatMessagesResource
from .resources.columns import ColumnsResource
from .resources.departments import DepartmentsResource
from .resources.employees import EmployeesResource
from .resources.group_chats import GroupChatsResource
from .resources.project_roles import ProjectRolesResource
from .resources.projects import ProjectsResource
from .resources.sprint_stickers import SprintStickersResource
from .resources.sprint_sticker_states import SprintStickerStatesResource
from .resources.string_stickers import StringStickersResource
from .resources.string_sticker_states import StringStickerStatesResource
from .resources.tasks import TasksResource
from .resources.webhooks import WebhooksResource


class YouGileClient:
    """Клиент для работы с YouGile API."""
    
    BASE_URL = "https://ru.yougile.com/api-v2"
    
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация клиента.
        
        Args:
            token: Токен для аутентификации
        """
        self.token = token
        self.session = requests.Session()
        
        # Инициализация ресурсов
        self.auth = AuthResource(self)
        self.boards = BoardsResource(self)
        self.chat_messages = ChatMessagesResource(self)
        self.columns = ColumnsResource(self)
        self.departments = DepartmentsResource(self)
        self.employees = EmployeesResource(self)
        self.group_chats = GroupChatsResource(self)
        self.project_roles = ProjectRolesResource(self)
        self.projects = ProjectsResource(self)
        self.sprint_stickers = SprintStickersResource(self)
        self.sprint_sticker_states = SprintStickerStatesResource(self)
        self.string_stickers = StringStickersResource(self)
        self.string_sticker_states = StringStickerStatesResource(self)
        self.tasks = TasksResource(self)
        self.webhooks = WebhooksResource(self)
    
    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                json: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Выполнить запрос к API.
        
        Args:
            method: HTTP метод
            endpoint: Эндпоинт API
            params: Параметры запроса
            json: Данные для отправки в формате JSON
            
        Returns:
            dict или list: Ответ от API
            
        Raises:
            YouGileApiError: При ошибке API
            YouGileAuthError: При ошибке аутентификации
            YouGileNotFoundError: Если ресурс не найден
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Подготовка заголовков
        headers = {
            "Content-Type": "application/json"
        }

        # Добавляем токен в заголовок Authorization, если он есть
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = self.session.request(method, url, params=params, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise YouGileAuthError("Ошибка аутентификации")
            elif response.status_code == 404:
                raise YouGileNotFoundError("Ресурс не найден")
            else:
                raise YouGileApiError(f"Ошибка API: {response.text}")
        except requests.exceptions.RequestException as e:
            raise YouGileApiError(f"Ошибка запроса: {str(e)}")
        except ValueError:
            raise YouGileApiError("Некорректный ответ от API")
            
    def set_token(self, token: str) -> None:
        """
        Установить токен для аутентификации.
        
        Args:
            token: Токен для аутентификации
        """
        self.token = token
