import unittest
from unittest.mock import patch, MagicMock
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
import logging
import sys

# Добавляем путь к родительской директории, чтобы импортировать yougile_api
# Это может потребоваться, если тесты запускаются из директории tests
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем из локальной директории
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from yougile_api.YouGileRestAPI import YouGileRestAPI

# Настройка логирования для тестов (можно отключить, установив уровень выше DEBUG)
logging.basicConfig(level=logging.CRITICAL)  # Отключаем логирование во время тестов
logger = logging.getLogger('test_yougile_api')


class TestYouGileRestAPI(unittest.TestCase):
    """
    Комплексные тесты для класса YouGileRestAPI из модуля yougile_api.

    Тесты покрывают следующие сценарии:
    1. Инициализация API-клиента
    2. Авторизация и работа с API-ключами
    3. Работа с пользователями
    4. Работа с проектами
    5. Работа с досками
    6. Работа с колонками
    7. Работа с задачами
    8. Работа с отделами
    9. Работа с сотрудниками
    10. Работа с групповыми чатами
    11. Работа с сообщениями чатов
    12. Работа с ролями проекта
    13. Работа с вебхуками
    14. Работа со стикерами спринта
    15. Работа с текстовыми стикерами
    16. Работа с файлами
    17. Обработка ошибок API
    18. Кэширование результатов запросов
    """

    def setUp(self):
        """
        Подготовка окружения для тестов.
        Создаем экземпляр API-клиента и настраиваем базовые моки.
        """
        self.api = YouGileRestAPI(base_url="https://test.yougile.com/api-v2", logger=logger)

        # Тестовые данные
        self.test_login = "test@example.com"
        self.test_password = "password123"
        self.test_company_id = "company-id-123"
        self.test_token = "test-api-token-12345"
        self.test_user_id = "user-id-101"
        self.test_user_id_2 = "user-id-102"
        self.test_project_id = "project-id-201"
        self.test_project_id_2 = "project-id-202"
        self.test_board_id = "board-id-301"
        self.test_board_id_2 = "board-id-302"
        self.test_column_id = "column-id-401"
        self.test_column_id_2 = "column-id-402"
        self.test_task_id = "task-id-501"
        self.test_task_id_2 = "task-id-502"
        self.test_department_id = "dept-id-601"
        self.test_employee_id = "emp-id-701"
        self.test_chat_id = "chat-id-801"
        self.test_message_id = "msg-id-901"
        self.test_role_id = "role-id-1001"
        self.test_webhook_id = "hook-id-1101"
        self.test_sprint_sticker_id = "sprint-sticker-id-1201"
        self.test_string_sticker_id = "string-sticker-id-1301"
        self.test_file_id = "file-id-1401"

        # Тестовые данные для ответов API (с использованием строковых ID)
        self.test_companies = [
            {"id": self.test_company_id, "name": "Test Company 1"},
            {"id": "company-id-678", "name": "Test Company 2"}
        ]
        self.test_keys = [
            {"id": "key-id-1", "key": self.test_token, "created": "2025-01-01"},
            {"id": "key-id-2", "key": "key2", "created": "2025-01-02"}
        ]
        self.test_users = [
            {"id": self.test_user_id, "email": "user1@example.com", "name": "User 1", "isAdmin": True},
            {"id": self.test_user_id_2, "email": "user2@example.com", "name": "User 2", "isAdmin": False}
        ]
        self.test_projects = [
            {"id": self.test_project_id, "title": "Project 1",
             "users": {self.test_user_id: "admin", self.test_user_id_2: "user"}},
            {"id": self.test_project_id_2, "title": "Project 2", "users": {self.test_user_id: "admin"}}
        ]
        self.test_boards = [
            {"id": self.test_board_id, "title": "Board 1", "projectId": self.test_project_id},
            {"id": self.test_board_id_2, "title": "Board 2", "projectId": self.test_project_id_2}
        ]
        self.test_columns = [
            {"id": self.test_column_id, "title": "Column 1", "boardId": self.test_board_id, "color": 1},
            {"id": self.test_column_id_2, "title": "Column 2", "boardId": self.test_board_id, "color": 2}
        ]
        self.test_tasks = [
            {
                "id": self.test_task_id,
                "title": "Task 1",
                "columnId": self.test_column_id,
                "assigned": [self.test_user_id],
                "description": "Description 1"
            },
            {
                "id": self.test_task_id_2,
                "title": "Task 2",
                "columnId": self.test_column_id_2,
                "assigned": [self.test_user_id_2],
                "description": "Description 2"
            }
        ]
        self.test_departments = [
            {"id": self.test_department_id, "title": "Department 1"},
            {"id": "dept-id-602", "title": "Department 2"}
        ]
        self.test_employees = [
            {"id": self.test_employee_id, "userId": self.test_user_id, "departmentId": self.test_department_id,
             "position": "Manager"},
            {"id": "emp-id-702", "userId": self.test_user_id_2, "departmentId": self.test_department_id,
             "position": "Developer"}
        ]
        self.test_group_chats = [
            {"id": self.test_chat_id, "title": "Chat 1", "users": [self.test_user_id, self.test_user_id_2]},
            {"id": "chat-id-802", "title": "Chat 2", "users": [self.test_user_id]}
        ]
        self.test_chat_messages = [
            {"id": self.test_message_id, "chatId": self.test_chat_id, "text": "Hello", "userId": self.test_user_id},
            {"id": "msg-id-902", "chatId": self.test_chat_id, "text": "Hi", "userId": self.test_user_id_2}
        ]
        self.test_project_roles = [
            {"id": self.test_role_id, "title": "Admin", "projectId": self.test_project_id,
             "permissions": {"canEdit": True}},
            {"id": "role-id-1002", "title": "User", "projectId": self.test_project_id,
             "permissions": {"canEdit": False}}
        ]
        self.test_webhooks = [
            {"id": self.test_webhook_id, "url": "https://example.com/hook1", "events": ["task.created"]},
            {"id": "hook-id-1102", "url": "https://example.com/hook2", "events": ["task.updated"]}
        ]
        self.test_sprint_stickers = [
            {"id": self.test_sprint_sticker_id, "title": "Sprint Sticker 1", "boardId": self.test_board_id,
             "states": []},
            {"id": "sprint-sticker-id-1202", "title": "Sprint Sticker 2", "boardId": self.test_board_id, "states": []}
        ]
        self.test_string_stickers = [
            {"id": self.test_string_sticker_id, "title": "String Sticker 1", "boardId": self.test_board_id,
             "states": []},
            {"id": "string-sticker-id-1302", "title": "String Sticker 2", "boardId": self.test_board_id, "states": []}
        ]
        self.test_files = [
            {"id": self.test_file_id, "name": "file1.txt", "taskId": self.test_task_id},
            {"id": "file-id-1402", "name": "file2.jpg", "taskId": self.test_task_id}
        ]

    def _mock_response(self, json_data=None, status_code=200, is_content=True, raise_for_status=None):
        """Вспомогательный метод для создания мок-ответа requests."""
        mock_resp = MagicMock()
        mock_resp.status_code = status_code

        # Устанавливаем не-пустой контент для всех ответов, кроме 204 No Content
        if status_code != 204 and json_data is not None:
            if isinstance(json_data, dict):
                mock_resp.content = b'{"data": "non-empty"}'
            elif isinstance(json_data, list):
                mock_resp.content = b'["non-empty"]'
            else:
                mock_resp.content = b'non-empty'

            if is_content:
                mock_resp.json.return_value = {"content": json_data}
            else:
                mock_resp.json.return_value = json_data
        else:
            # Для 204 No Content или None json_data
            mock_resp.content = b''
            mock_resp.json.side_effect = ValueError  # Имитация отсутствия JSON

        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        else:
            if status_code >= 400:
                mock_resp.raise_for_status.side_effect = HTTPError(f"{status_code} Error", response=mock_resp)
            else:
                mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_init(self):
        """Тест инициализации API-клиента."""
        self.assertEqual(self.api.url, "https://test.yougile.com/api-v2")
        self.assertIsInstance(self.api.logger, logging.Logger)
        # Проверяем инициализацию кэшей
        self.assertEqual(self.api.companies, [])
        self.assertEqual(self.api.keys, [])
        # ... и так далее для всех кэшируемых списков
        self.assertEqual(self.api.webhooks, [])

    @patch('requests.request')
    def test_request_success(self, mock_request):
        """Тест успешного выполнения _request."""
        mock_request.return_value = self._mock_response(json_data={"key": "value"})
        result = self.api._request("GET", "/test", token=self.test_token)
        self.assertEqual(result, {"key": "value"})
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/test",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_request_success_no_content_wrapper(self, mock_request):
        """Тест успешного _request, когда ответ не обернут в 'content'."""
        mock_request.return_value = self._mock_response(json_data=[{"id": 1}], is_content=False)
        result = self.api._request("GET", "/test_list")
        self.assertEqual(result, [{"id": 1}])

    @patch('requests.request')
    def test_request_http_error(self, mock_request):
        """Тест обработки HTTPError в _request."""
        mock_request.return_value = self._mock_response(status_code=404, json_data={"error": "Not Found"},
                                                        is_content=False)
        with self.assertRaises(HTTPError):
            self.api._request("GET", "/not_found")

    @patch('requests.request')
    def test_request_timeout_error(self, mock_request):
        """Тест обработки Timeout в _request."""
        mock_request.side_effect = Timeout("Request timed out")
        with self.assertRaises(Timeout):
            self.api._request("GET", "/timeout")

    @patch('requests.request')
    def test_request_request_exception(self, mock_request):
        """Тест обработки RequestException в _request."""
        mock_request.side_effect = RequestException("General request error")
        with self.assertRaises(RequestException):
            self.api._request("GET", "/error")

    # --- Тесты методов API --- #

    @patch('requests.request')
    def test_get_companies(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_companies)
        result = self.api.get_companies(self.test_login, self.test_password)
        self.assertEqual(result, self.test_companies)
        self.assertEqual(self.api.companies, self.test_companies)  # Проверка кэша
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/auth/companies",
            headers={"Content-Type": "application/json"}, params=None,
            json={"login": self.test_login, "password": self.test_password, "name": ""}, timeout=30
        )

    @patch('requests.request')
    def test_get_keys(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_keys)
        result = self.api.get_keys(self.test_login, self.test_password, self.test_company_id)
        self.assertEqual(result, self.test_keys)
        self.assertEqual(self.api.keys, self.test_keys)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/auth/keys/get",
            headers={"Content-Type": "application/json"}, params=None,
            json={"login": self.test_login, "password": self.test_password, "companyId": self.test_company_id},
            timeout=30
        )

    @patch('requests.request')
    def test_create_key(self, mock_request):
        mock_response_data = {"key": self.test_token, "id": "new-key-id"}
        mock_request.return_value = self._mock_response(mock_response_data)
        result = self.api.create_key(self.test_login, self.test_password, self.test_company_id)
        self.assertEqual(result, mock_response_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/auth/keys",
            headers={"Content-Type": "application/json"}, params=None,
            json={"login": self.test_login, "password": self.test_password, "companyId": self.test_company_id},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_key(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)  # 204 No Content
        # Ожидаем, что метод вернет None или пустой dict при успешном удалении без контента
        result = self.api.delete_key(self.test_token)
        self.assertIsNone(result)  # Или self.assertEqual(result, {}) в зависимости от реализации _request
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/auth/keys/{self.test_token}",
            headers={"Content-Type": "application/json"}, params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_users(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_users)
        result = self.api.get_users(self.test_token)
        self.assertEqual(result, self.test_users)
        self.assertEqual(self.api.users, self.test_users)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/users",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_user(self, mock_request):
        new_user_email = "new@example.com"
        new_user_data = {"id": "user-id-103", "email": new_user_email, "isAdmin": False}
        mock_request.return_value = self._mock_response(new_user_data)
        result = self.api.create_user(self.test_token, new_user_email, isAdmin=False)
        self.assertEqual(result, new_user_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/users",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"email": new_user_email, "isAdmin": False}, timeout=30
        )

    @patch('requests.request')
    def test_get_user(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_users[0])
        result = self.api.get_user(self.test_token, self.test_user_id)
        self.assertEqual(result, self.test_users[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/users/{self.test_user_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_user(self, mock_request):
        updated_user_data = self.test_users[0].copy()
        updated_user_data["isAdmin"] = False
        mock_request.return_value = self._mock_response(updated_user_data)
        result = self.api.change_user(self.test_token, self.test_user_id, isAdmin=False)
        self.assertEqual(result, updated_user_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/users/{self.test_user_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"isAdmin": False}, timeout=30
        )

    @patch('requests.request')
    def test_delete_user(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_user(self.test_token, self.test_user_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/users/{self.test_user_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_projects(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_projects)
        result = self.api.get_projects(self.test_token)
        self.assertEqual(result, self.test_projects)
        self.assertEqual(self.api.projects, self.test_projects)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/projects",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_project(self, mock_request):
        new_project_title = "New Project"
        new_project_users = {self.test_user_id: "admin"}
        new_project_data = {"id": "project-id-203", "title": new_project_title, "users": new_project_users}
        mock_request.return_value = self._mock_response(new_project_data)
        result = self.api.create_project(self.test_token, new_project_title, new_project_users)
        self.assertEqual(result, new_project_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/projects",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"title": new_project_title, "users": new_project_users}, timeout=30
        )

    @patch('requests.request')
    def test_get_project(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_projects[0])
        result = self.api.get_project(self.test_token, self.test_project_id)
        self.assertEqual(result, self.test_projects[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/projects/{self.test_project_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_project(self, mock_request):
        updated_project_data = self.test_projects[0].copy()
        updated_project_data["title"] = "Updated Project Title"
        updated_project_data["users"] = {self.test_user_id: "admin"}
        mock_request.return_value = self._mock_response(updated_project_data)
        result = self.api.change_project(self.test_token, self.test_project_id, title="Updated Project Title",
                                         users={self.test_user_id: "admin"})
        self.assertEqual(result, updated_project_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/projects/{self.test_project_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"deleted": False, "title": "Updated Project Title", "users": {self.test_user_id: "admin"}}, timeout=30
        )

    @patch('requests.request')
    def test_delete_project(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_project(self.test_token, self.test_project_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/projects/{self.test_project_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_boards(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_boards)
        result = self.api.get_boards(self.test_token)
        self.assertEqual(result, self.test_boards)
        self.assertEqual(self.api.boards, self.test_boards)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/boards",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_board(self, mock_request):
        new_board_title = "New Board"
        new_board_stickers = {"deadline": True}
        new_board_data = {"id": "board-id-303", "title": new_board_title, "projectId": self.test_project_id}
        mock_request.return_value = self._mock_response(new_board_data)
        result = self.api.create_board(self.test_token, new_board_title, self.test_project_id,
                                       stickers=new_board_stickers)
        self.assertEqual(result, new_board_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/boards",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"title": new_board_title, "projectId": self.test_project_id, "stickers": new_board_stickers},
            timeout=30
        )

    @patch('requests.request')
    def test_get_board(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_boards[0])
        result = self.api.get_board(self.test_token, self.test_board_id)
        self.assertEqual(result, self.test_boards[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/boards/{self.test_board_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_board(self, mock_request):
        updated_board_data = self.test_boards[0].copy()
        updated_board_data["title"] = "Updated Board Title"
        updated_board_data["stickers"] = {"assignee": False}
        mock_request.return_value = self._mock_response(updated_board_data)
        result = self.api.change_board(self.test_token, self.test_board_id, title="Updated Board Title",
                                       stickers={"assignee": False})
        self.assertEqual(result, updated_board_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/boards/{self.test_board_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated Board Title", "stickers": {"assignee": False}},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_board(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_board(self.test_token, self.test_board_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/boards/{self.test_board_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_columns(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_columns)
        result = self.api.get_columns(self.test_token, boardId=self.test_board_id)
        self.assertEqual(result, self.test_columns)
        self.assertEqual(self.api.columns, self.test_columns)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/columns",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"boardId": self.test_board_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_column(self, mock_request):
        new_column_title = "New Column"
        new_column_color = 3
        new_column_data = {"id": "column-id-403", "title": new_column_title, "boardId": self.test_board_id,
                           "color": new_column_color}
        mock_request.return_value = self._mock_response(new_column_data)
        result = self.api.create_column(self.test_token, new_column_title, new_column_color, self.test_board_id,
                                        position=1)
        self.assertEqual(result, new_column_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/columns",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"title": new_column_title, "color": new_column_color, "boardId": self.test_board_id, "position": 1},
            timeout=30
        )

    @patch('requests.request')
    def test_get_column(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_columns[0])
        result = self.api.get_column(self.test_token, self.test_column_id)
        self.assertEqual(result, self.test_columns[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/columns/{self.test_column_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_column(self, mock_request):
        updated_column_data = self.test_columns[0].copy()
        updated_column_data["title"] = "Updated Column Title"
        updated_column_data["color"] = 5
        updated_column_data["position"] = 0
        mock_request.return_value = self._mock_response(updated_column_data)
        result = self.api.change_column(self.test_token, self.test_column_id, title="Updated Column Title", color=5,
                                        position=0)
        self.assertEqual(result, updated_column_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/columns/{self.test_column_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated Column Title", "color": 5, "position": 0}, timeout=30
        )

    @patch('requests.request')
    def test_delete_column(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_column(self.test_token, self.test_column_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/columns/{self.test_column_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_tasks(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_tasks)
        result = self.api.get_tasks(self.test_token, columnId=self.test_column_id)
        self.assertEqual(result, self.test_tasks)
        self.assertEqual(self.api.tasks, self.test_tasks)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/tasks",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"columnId": self.test_column_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_task(self, mock_request):
        new_task_title = "New Task"
        new_task_assigned = [self.test_user_id, self.test_user_id_2]
        new_task_data = {"id": "task-id-503", "title": new_task_title, "columnId": self.test_column_id}
        mock_request.return_value = self._mock_response(new_task_data)
        result = self.api.create_task(
            self.test_token,
            title=new_task_title,
            columnId=self.test_column_id,
            description="New desc",
            assigned=new_task_assigned
        )
        self.assertEqual(result, new_task_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/tasks",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={
                "title": new_task_title,
                "columnId": self.test_column_id,
                "description": "New desc",
                "assigned": new_task_assigned
            },
            timeout=30
        )

    @patch('requests.request')
    def test_get_task(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_tasks[0])
        result = self.api.get_task(self.test_token, self.test_task_id)
        self.assertEqual(result, self.test_tasks[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/tasks/{self.test_task_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_task(self, mock_request):
        updated_task_data = self.test_tasks[0].copy()
        updated_task_data["title"] = "Updated Task Title"
        updated_task_data["completed"] = True
        updated_task_data["assigned"] = [self.test_user_id_2]
        mock_request.return_value = self._mock_response(updated_task_data)
        result = self.api.change_task(
            self.test_token,
            self.test_task_id,
            title="Updated Task Title",
            completed=True,
            assigned=[self.test_user_id_2]
        )
        self.assertEqual(result, updated_task_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/tasks/{self.test_task_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={
                "deleted": False,
                "title": "Updated Task Title",
                "completed": True,
                "assigned": [self.test_user_id_2]
            },
            timeout=30
        )

    @patch('requests.request')
    def test_delete_task(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_task(self.test_token, self.test_task_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/tasks/{self.test_task_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    # --- Тесты для новых методов --- #

    @patch('requests.request')
    def test_get_departments(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_departments)
        result = self.api.get_departments(self.test_token)
        self.assertEqual(result, self.test_departments)
        self.assertEqual(self.api.departments, self.test_departments)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/departments",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_department(self, mock_request):
        new_dept_title = "New Department"
        new_dept_data = {"id": "dept-id-603", "title": new_dept_title}
        mock_request.return_value = self._mock_response(new_dept_data)
        result = self.api.create_department(self.test_token, new_dept_title)
        self.assertEqual(result, new_dept_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/departments",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"title": new_dept_title}, timeout=30
        )

    @patch('requests.request')
    def test_get_department(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_departments[0])
        result = self.api.get_department(self.test_token, self.test_department_id)
        self.assertEqual(result, self.test_departments[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/departments/{self.test_department_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_department(self, mock_request):
        updated_dept_data = self.test_departments[0].copy()
        updated_dept_data["title"] = "Updated Department"
        mock_request.return_value = self._mock_response(updated_dept_data)
        result = self.api.change_department(self.test_token, self.test_department_id, title="Updated Department")
        self.assertEqual(result, updated_dept_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/departments/{self.test_department_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated Department"}, timeout=30
        )

    @patch('requests.request')
    def test_delete_department(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_department(self.test_token, self.test_department_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/departments/{self.test_department_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_employees(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_employees)
        result = self.api.get_employees(self.test_token, departmentId=self.test_department_id)
        self.assertEqual(result, self.test_employees)
        self.assertEqual(self.api.employees, self.test_employees)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/employees",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"departmentId": self.test_department_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_employee(self, mock_request):
        new_emp_pos = "Tester"
        new_emp_data = {"id": "emp-id-703", "userId": self.test_user_id, "departmentId": self.test_department_id,
                        "position": new_emp_pos}
        mock_request.return_value = self._mock_response(new_emp_data)
        result = self.api.create_employee(self.test_token, self.test_user_id, self.test_department_id,
                                          position=new_emp_pos)
        self.assertEqual(result, new_emp_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/employees",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"userId": self.test_user_id, "departmentId": self.test_department_id, "position": new_emp_pos},
            timeout=30
        )

    @patch('requests.request')
    def test_get_employee(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_employees[0])
        result = self.api.get_employee(self.test_token, self.test_employee_id)
        self.assertEqual(result, self.test_employees[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/employees/{self.test_employee_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_employee(self, mock_request):
        updated_emp_data = self.test_employees[0].copy()
        updated_emp_data["position"] = "Senior Manager"
        mock_request.return_value = self._mock_response(updated_emp_data)
        result = self.api.change_employee(self.test_token, self.test_employee_id, position="Senior Manager")
        self.assertEqual(result, updated_emp_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/employees/{self.test_employee_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "position": "Senior Manager"}, timeout=30
        )

    @patch('requests.request')
    def test_delete_employee(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_employee(self.test_token, self.test_employee_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/employees/{self.test_employee_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_group_chats(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_group_chats)
        result = self.api.get_group_chats(self.test_token)
        self.assertEqual(result, self.test_group_chats)
        self.assertEqual(self.api.group_chats, self.test_group_chats)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/groupchats",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_group_chat(self, mock_request):
        new_chat_title = "New Chat"
        new_chat_users = [self.test_user_id]
        new_chat_data = {"id": "chat-id-803", "title": new_chat_title, "users": new_chat_users}
        mock_request.return_value = self._mock_response(new_chat_data)
        result = self.api.create_group_chat(self.test_token, new_chat_title, new_chat_users)
        self.assertEqual(result, new_chat_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/groupchats",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"title": new_chat_title, "users": new_chat_users}, timeout=30
        )

    @patch('requests.request')
    def test_get_group_chat(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_group_chats[0])
        result = self.api.get_group_chat(self.test_token, self.test_chat_id)
        self.assertEqual(result, self.test_group_chats[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/groupchats/{self.test_chat_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_group_chat(self, mock_request):
        updated_chat_data = self.test_group_chats[0].copy()
        updated_chat_data["title"] = "Updated Chat"
        updated_chat_data["users"] = [self.test_user_id_2]
        mock_request.return_value = self._mock_response(updated_chat_data)
        result = self.api.change_group_chat(self.test_token, self.test_chat_id, title="Updated Chat",
                                            users=[self.test_user_id_2])
        self.assertEqual(result, updated_chat_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/groupchats/{self.test_chat_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated Chat", "users": [self.test_user_id_2]}, timeout=30
        )

    @patch('requests.request')
    def test_delete_group_chat(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_group_chat(self.test_token, self.test_chat_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/groupchats/{self.test_chat_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_chat_messages(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_chat_messages)
        result = self.api.get_chat_messages(self.test_token, self.test_chat_id, limit=10, offset=0)
        self.assertEqual(result, self.test_chat_messages)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/chatmessages",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"chatId": self.test_chat_id, "limit": 10, "offset": 0}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_chat_message(self, mock_request):
        new_msg_text = "Hello there!"
        new_msg_data = {"id": "msg-id-903", "chatId": self.test_chat_id, "text": new_msg_text,
                        "userId": self.test_user_id}
        mock_request.return_value = self._mock_response(new_msg_data)
        result = self.api.create_chat_message(self.test_token, self.test_chat_id, new_msg_text)
        self.assertEqual(result, new_msg_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/chatmessages",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"chatId": self.test_chat_id, "text": new_msg_text}, timeout=30
        )

    @patch('requests.request')
    def test_get_chat_message(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_chat_messages[0])
        result = self.api.get_chat_message(self.test_token, self.test_message_id)
        self.assertEqual(result, self.test_chat_messages[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/chatmessages/{self.test_message_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_chat_message(self, mock_request):
        updated_msg_data = self.test_chat_messages[0].copy()
        updated_msg_data["text"] = "Updated message text"
        mock_request.return_value = self._mock_response(updated_msg_data)
        result = self.api.change_chat_message(self.test_token, self.test_message_id, text="Updated message text")
        self.assertEqual(result, updated_msg_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/chatmessages/{self.test_message_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"text": "Updated message text"}, timeout=30
        )

    @patch('requests.request')
    def test_delete_chat_message(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_chat_message(self.test_token, self.test_message_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/chatmessages/{self.test_message_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_project_roles(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_project_roles)
        result = self.api.get_project_roles(self.test_token, projectId=self.test_project_id)
        self.assertEqual(result, self.test_project_roles)
        self.assertEqual(self.api.project_roles, self.test_project_roles)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/projectroles",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"projectId": self.test_project_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_project_role(self, mock_request):
        new_role_title = "Tester Role"
        new_role_perms = {"canView": True, "canEdit": False}
        new_role_data = {"id": "role-id-1003", "title": new_role_title, "projectId": self.test_project_id,
                         "permissions": new_role_perms}
        mock_request.return_value = self._mock_response(new_role_data)
        result = self.api.create_project_role(self.test_token, new_role_title, self.test_project_id, new_role_perms)
        self.assertEqual(result, new_role_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/projectroles",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"title": new_role_title, "projectId": self.test_project_id, "permissions": new_role_perms}, timeout=30
        )

    @patch('requests.request')
    def test_get_project_role(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_project_roles[0])
        result = self.api.get_project_role(self.test_token, self.test_role_id)
        self.assertEqual(result, self.test_project_roles[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/projectroles/{self.test_role_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_project_role(self, mock_request):
        updated_role_data = self.test_project_roles[0].copy()
        updated_role_data["title"] = "Super Admin"
        updated_role_data["permissions"] = {"canDoEverything": True}
        mock_request.return_value = self._mock_response(updated_role_data)
        result = self.api.change_project_role(self.test_token, self.test_role_id, title="Super Admin",
                                              permissions={"canDoEverything": True})
        self.assertEqual(result, updated_role_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/projectroles/{self.test_role_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Super Admin", "permissions": {"canDoEverything": True}},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_project_role(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_project_role(self.test_token, self.test_role_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/projectroles/{self.test_role_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_webhooks(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_webhooks)
        result = self.api.get_webhooks(self.test_token)
        self.assertEqual(result, self.test_webhooks)
        self.assertEqual(self.api.webhooks, self.test_webhooks)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/webhooks",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_webhook(self, mock_request):
        new_hook_url = "https://new.example.com/hook"
        new_hook_events = ["task.created", "task.deleted"]
        new_hook_data = {"id": "hook-id-1103", "url": new_hook_url, "events": new_hook_events}
        mock_request.return_value = self._mock_response(new_hook_data)
        result = self.api.create_webhook(self.test_token, new_hook_url, new_hook_events)
        self.assertEqual(result, new_hook_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/webhooks",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"url": new_hook_url, "events": new_hook_events}, timeout=30
        )

    @patch('requests.request')
    def test_get_webhook(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_webhooks[0])
        result = self.api.get_webhook(self.test_token, self.test_webhook_id)
        self.assertEqual(result, self.test_webhooks[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/webhooks/{self.test_webhook_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_webhook(self, mock_request):
        updated_hook_data = self.test_webhooks[0].copy()
        updated_hook_data["url"] = "https://updated.example.com/hook"
        updated_hook_data["events"] = ["column.created"]
        mock_request.return_value = self._mock_response(updated_hook_data)
        result = self.api.change_webhook(self.test_token, self.test_webhook_id, url="https://updated.example.com/hook",
                                         events=["column.created"])
        self.assertEqual(result, updated_hook_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/webhooks/{self.test_webhook_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None,
            json={"deleted": False, "url": "https://updated.example.com/hook", "events": ["column.created"]}, timeout=30
        )

    @patch('requests.request')
    def test_delete_webhook(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_webhook(self.test_token, self.test_webhook_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/webhooks/{self.test_webhook_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_sprint_stickers(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_sprint_stickers)
        result = self.api.get_sprint_stickers(self.test_token, boardId=self.test_board_id)
        self.assertEqual(result, self.test_sprint_stickers)
        self.assertEqual(self.api.sprint_stickers, self.test_sprint_stickers)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/sprintstickers",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"boardId": self.test_board_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_sprint_sticker(self, mock_request):
        new_sticker_title = "New Sprint Sticker"
        new_sticker_states = [{"name": "State 1", "color": 1}]
        new_sticker_data = {"id": "sprint-sticker-id-1203", "title": new_sticker_title, "boardId": self.test_board_id,
                            "states": new_sticker_states}
        mock_request.return_value = self._mock_response(new_sticker_data)
        result = self.api.create_sprint_sticker(self.test_token, new_sticker_title, self.test_board_id,
                                                new_sticker_states)
        self.assertEqual(result, new_sticker_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/sprintstickers",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"title": new_sticker_title, "boardId": self.test_board_id, "states": new_sticker_states},
            timeout=30
        )

    @patch('requests.request')
    def test_get_sprint_sticker(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_sprint_stickers[0])
        result = self.api.get_sprint_sticker(self.test_token, self.test_sprint_sticker_id)
        self.assertEqual(result, self.test_sprint_stickers[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/sprintstickers/{self.test_sprint_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_sprint_sticker(self, mock_request):
        updated_sticker_data = self.test_sprint_stickers[0].copy()
        updated_sticker_data["title"] = "Updated Sprint Sticker"
        updated_sticker_data["states"] = [{"name": "Updated State", "color": 2}]
        mock_request.return_value = self._mock_response(updated_sticker_data)
        result = self.api.change_sprint_sticker(self.test_token, self.test_sprint_sticker_id,
                                                title="Updated Sprint Sticker",
                                                states=[{"name": "Updated State", "color": 2}])
        self.assertEqual(result, updated_sticker_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/sprintstickers/{self.test_sprint_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated Sprint Sticker",
                               "states": [{"name": "Updated State", "color": 2}]}, timeout=30
        )

    @patch('requests.request')
    def test_delete_sprint_sticker(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_sprint_sticker(self.test_token, self.test_sprint_sticker_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/sprintstickers/{self.test_sprint_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_string_stickers(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_string_stickers)
        result = self.api.get_string_stickers(self.test_token, boardId=self.test_board_id)
        self.assertEqual(result, self.test_string_stickers)
        self.assertEqual(self.api.string_stickers, self.test_string_stickers)
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/stringstickers",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"boardId": self.test_board_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_create_string_sticker(self, mock_request):
        new_sticker_title = "New String Sticker"
        new_sticker_states = [{"name": "State A", "color": 4}]
        new_sticker_data = {"id": "string-sticker-id-1303", "title": new_sticker_title, "boardId": self.test_board_id,
                            "states": new_sticker_states}
        mock_request.return_value = self._mock_response(new_sticker_data)
        result = self.api.create_string_sticker(self.test_token, new_sticker_title, self.test_board_id,
                                                new_sticker_states)
        self.assertEqual(result, new_sticker_data)
        mock_request.assert_called_once_with(
            "POST", f"{self.api.url}/stringstickers",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"title": new_sticker_title, "boardId": self.test_board_id, "states": new_sticker_states},
            timeout=30
        )

    @patch('requests.request')
    def test_get_string_sticker(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_string_stickers[0])
        result = self.api.get_string_sticker(self.test_token, self.test_string_sticker_id)
        self.assertEqual(result, self.test_string_stickers[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/stringstickers/{self.test_string_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_change_string_sticker(self, mock_request):
        updated_sticker_data = self.test_string_stickers[0].copy()
        updated_sticker_data["title"] = "Updated String Sticker"
        updated_sticker_data["states"] = [{"name": "Updated State B", "color": 5}]
        mock_request.return_value = self._mock_response(updated_sticker_data)
        result = self.api.change_string_sticker(self.test_token, self.test_string_sticker_id,
                                                title="Updated String Sticker",
                                                states=[{"name": "Updated State B", "color": 5}])
        self.assertEqual(result, updated_sticker_data)
        mock_request.assert_called_once_with(
            "PUT", f"{self.api.url}/stringstickers/{self.test_string_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json={"deleted": False, "title": "Updated String Sticker",
                               "states": [{"name": "Updated State B", "color": 5}]}, timeout=30
        )

    @patch('requests.request')
    def test_delete_string_sticker(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_string_sticker(self.test_token, self.test_string_sticker_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/stringstickers/{self.test_string_sticker_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_files(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_files)
        result = self.api.get_files(self.test_token, taskId=self.test_task_id)
        self.assertEqual(result, self.test_files)
        # Файлы не кэшируются
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/files",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params={"taskId": self.test_task_id}, json=None, timeout=30
        )

    @patch('requests.request')
    def test_get_file(self, mock_request):
        mock_request.return_value = self._mock_response(self.test_files[0])
        result = self.api.get_file(self.test_token, self.test_file_id)
        self.assertEqual(result, self.test_files[0])
        mock_request.assert_called_once_with(
            "GET", f"{self.api.url}/files/{self.test_file_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )

    @patch('requests.request')
    def test_delete_file(self, mock_request):
        mock_request.return_value = self._mock_response(status_code=204, json_data=None)
        result = self.api.delete_file(self.test_token, self.test_file_id)
        self.assertIsNone(result)
        mock_request.assert_called_once_with(
            "DELETE", f"{self.api.url}/files/{self.test_file_id}",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.test_token}"},
            params=None, json=None, timeout=30
        )


if __name__ == '__main__':
    unittest.main()