import unittest
from unittest.mock import patch, MagicMock, Mock
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from yougile_api.YouGileRestAPI import YouGileRestAPI


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
    8. Обработка ошибок API
    9. Кэширование результатов запросов
    """

    def setUp(self):
        """
        Подготовка окружения для тестов.
        Создаем экземпляр API-клиента и настраиваем базовые моки.
        """
        # Создаем экземпляр API-клиента с тестовым URL
        self.api = YouGileRestAPI(base_url="https://test.yougile.com/api-v2")

        # Тестовые данные для авторизации
        self.test_login = "test@example.com"
        self.test_password = "password123"
        self.test_company_id = 12345

        # Тестовый API-ключ
        self.test_token = "test_api_token_12345"

        # Тестовые данные для компаний
        self.test_companies = [
            {"id": 12345, "name": "Test Company 1"},
            {"id": 67890, "name": "Test Company 2"}
        ]

        # Тестовые данные для API-ключей
        self.test_keys = [
            {"id": 1, "key": "key1", "created": "2025-01-01"},
            {"id": 2, "key": "key2", "created": "2025-01-02"}
        ]

        # Тестовые данные для пользователей
        self.test_users = [
            {"id": 101, "email": "user1@example.com", "name": "User 1", "isAdmin": True},
            {"id": 102, "email": "user2@example.com", "name": "User 2", "isAdmin": False}
        ]

        # Тестовые данные для проектов
        self.test_projects = [
            {"id": 201, "title": "Project 1", "users": [101, 102]},
            {"id": 202, "title": "Project 2", "users": [101]}
        ]

        # Тестовые данные для досок
        self.test_boards = [
            {"id": 301, "title": "Board 1", "projectId": 201},
            {"id": 302, "title": "Board 2", "projectId": 202}
        ]

        # Тестовые данные для колонок
        self.test_columns = [
            {"id": 401, "title": "Column 1", "boardId": 301, "color": "#FF0000"},
            {"id": 402, "title": "Column 2", "boardId": 301, "color": "#00FF00"}
        ]

        # Тестовые данные для задач
        self.test_tasks = [
            {
                "id": 501,
                "title": "Task 1",
                "columnId": 401,
                "assigned": [101],
                "description": "Description 1"
            },
            {
                "id": 502,
                "title": "Task 2",
                "columnId": 402,
                "assigned": [102],
                "description": "Description 2"
            }
        ]

        # Тестовые данные для подписчиков чата
        self.test_chat_subscribers = [101, 102]

    def test_init(self):
        """
        Тест инициализации API-клиента.
        """
        # Проверяем, что URL установлен правильно
        self.assertEqual(self.api.url, "https://test.yougile.com/api-v2")

        # Проверяем, что кэши инициализированы пустыми списками
        self.assertEqual(self.api.companies, [])
        self.assertEqual(self.api.keys, [])
        self.assertEqual(self.api.users, [])
        self.assertEqual(self.api.projects, [])
        self.assertEqual(self.api.boards, [])
        self.assertEqual(self.api.columns, [])
        self.assertEqual(self.api.tasks, [])
        self.assertEqual(self.api.chat_subscribers, [])

        # Проверяем инициализацию с другим URL
        api2 = YouGileRestAPI(base_url="https://custom.yougile.com/api-v2/")
        self.assertEqual(api2.url, "https://custom.yougile.com/api-v2")  # Проверяем удаление trailing slash

    @patch('requests.request')
    def test_request_method(self, mock_request):
        """
        Тест внутреннего метода _request для выполнения запросов к API.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"key": "value"}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод _request
        result = self.api._request(
            "GET",
            "/test/path",
            token=self.test_token,
            params={"param": "value"},
            json={"data": "value"}
        )

        # Проверяем результат
        self.assertEqual(result, {"key": "value"})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/test/path",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params={"param": "value"},
            json={"data": "value"},
            timeout=30
        )

        # Проверяем обработку ответа без content
        mock_response.json.return_value = {"key": "value"}
        result = self.api._request("GET", "/test/path")
        self.assertEqual(result, {"key": "value"})

        # Проверяем обработку списка в ответе
        mock_response.json.return_value = [1, 2, 3]
        result = self.api._request("GET", "/test/path")
        self.assertEqual(result, [1, 2, 3])

    @patch('requests.request')
    def test_request_error_handling(self, mock_request):
        """
        Тест обработки ошибок в методе _request.
        """
        # Настраиваем мок для имитации HTTP-ошибки
        mock_request.side_effect = HTTPError("404 Client Error")

        # Проверяем, что исключение пробрасывается дальше
        with self.assertRaises(HTTPError):
            self.api._request("GET", "/test/path")

        # Настраиваем мок для имитации таймаута
        mock_request.side_effect = Timeout("Request timed out")

        # Проверяем, что исключение пробрасывается дальше
        with self.assertRaises(Timeout):
            self.api._request("GET", "/test/path")

        # Настраиваем мок для имитации общей ошибки запроса
        mock_request.side_effect = RequestException("General request error")

        # Проверяем, что исключение пробрасывается дальше
        with self.assertRaises(RequestException):
            self.api._request("GET", "/test/path")

    @patch('requests.request')
    def test_get_companies(self, mock_request):
        """
        Тест метода get_companies для получения списка компаний.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_companies}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_companies
        result = self.api.get_companies(self.test_login, self.test_password)

        # Проверяем результат
        self.assertEqual(result, self.test_companies)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.companies, self.test_companies)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/auth/companies",
            headers={"Content-Type": "application/json"},
            params=None,
            json={"login": self.test_login, "password": self.test_password, "name": ""},
            timeout=30
        )

    @patch('requests.request')
    def test_get_keys(self, mock_request):
        """
        Тест метода get_keys для получения списка API-ключей.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_keys}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_keys
        result = self.api.get_keys(self.test_login, self.test_password, self.test_company_id)

        # Проверяем результат
        self.assertEqual(result, self.test_keys)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.keys, self.test_keys)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/auth/keys/get",
            headers={"Content-Type": "application/json"},
            params=None,
            json={"login": self.test_login, "password": self.test_password, "companyId": self.test_company_id},
            timeout=30
        )

    @patch('requests.request')
    def test_create_key(self, mock_request):
        """
        Тест метода create_key для создания нового API-ключа.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"key": self.test_token}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_key
        result = self.api.create_key(self.test_login, self.test_password, self.test_company_id)

        # Проверяем результат
        self.assertEqual(result, {"key": self.test_token})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/auth/keys",
            headers={"Content-Type": "application/json"},
            params=None,
            json={"login": self.test_login, "password": self.test_password, "companyId": self.test_company_id},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_key(self, mock_request):
        """
        Тест метода delete_key для удаления API-ключа.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"success": True}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_key
        result = self.api.delete_key(self.test_token)

        # Проверяем результат
        self.assertEqual(result, {"success": True})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            f"https://test.yougile.com/api-v2/auth/keys/{self.test_token}",
            headers={"Content-Type": "application/json"},
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_users(self, mock_request):
        """
        Тест метода get_users для получения списка пользователей.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_users}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_users
        result = self.api.get_users(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_users)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.users, self.test_users)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_create_user(self, mock_request):
        """
        Тест метода create_user для создания нового пользователя.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 103, "email": "new@example.com"}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_user
        result = self.api.create_user(self.test_token, "new@example.com", isAdmin=True)

        # Проверяем результат
        self.assertEqual(result, {"id": 103, "email": "new@example.com"})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"email": "new@example.com", "isAdmin": True},
            timeout=30
        )

    @patch('requests.request')
    def test_get_user(self, mock_request):
        """
        Тест метода get_user для получения данных конкретного пользователя.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_users[0]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_user
        result = self.api.get_user(self.test_token, 101)

        # Проверяем результат
        self.assertEqual(result, self.test_users[0])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/users/101",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_user(self, mock_request):
        """
        Тест метода change_user для изменения данных пользователя.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 101, "isAdmin": False}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_user
        result = self.api.change_user(self.test_token, 101, isAdmin=False)

        # Проверяем результат
        self.assertEqual(result, {"id": 101, "isAdmin": False})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/users/101",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"isAdmin": False},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_user(self, mock_request):
        """
        Тест метода delete_user для удаления пользователя.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_user
        self.api.delete_user(self.test_token, 101)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            "https://test.yougile.com/api-v2/users/101",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_projects(self, mock_request):
        """
        Тест метода get_projects для получения списка проектов.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_projects}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_projects
        result = self.api.get_projects(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_projects)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.projects, self.test_projects)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/projects",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_create_project(self, mock_request):
        """
        Тест метода create_project для создания нового проекта.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 203, "title": "New Project", "users": [101, 102]}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_project
        result = self.api.create_project(self.test_token, "New Project", [101, 102])

        # Проверяем результат
        self.assertEqual(result, {"id": 203, "title": "New Project", "users": [101, 102]})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/projects",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"title": "New Project", "users": [101, 102]},
            timeout=30
        )

    @patch('requests.request')
    def test_get_project(self, mock_request):
        """
        Тест метода get_project для получения данных конкретного проекта.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_projects[0]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_project
        result = self.api.get_project(self.test_token, 201)

        # Проверяем результат
        self.assertEqual(result, self.test_projects[0])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/projects/201",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_project(self, mock_request):
        """
        Тест метода change_project для изменения данных проекта.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 201, "title": "Updated Project", "users": [101]}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_project
        result = self.api.change_project(
            self.test_token,
            201,
            title="Updated Project",
            users=[101],
            delete=False
        )

        # Проверяем результат
        self.assertEqual(result, {"id": 201, "title": "Updated Project", "users": [101]})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/projects/201",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"deleted": False, "title": "Updated Project", "users": [101]},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_project(self, mock_request):
        """
        Тест метода delete_project для удаления проекта.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_project
        self.api.delete_project(self.test_token, 201)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            "https://test.yougile.com/api-v2/projects/201",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_boards(self, mock_request):
        """
        Тест метода get_boards для получения списка досок.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_boards}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_boards
        result = self.api.get_boards(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_boards)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.boards, self.test_boards)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/boards",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_create_board(self, mock_request):
        """
        Тест метода create_board для создания новой доски.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 303, "title": "New Board", "projectId": 201}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_board
        result = self.api.create_board(self.test_token, "New Board", 201)

        # Проверяем результат
        self.assertEqual(result, {"id": 303, "title": "New Board", "projectId": 201})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/boards",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"title": "New Board", "projectId": 201, "stickers": {}},
            timeout=30
        )

    @patch('requests.request')
    def test_get_board(self, mock_request):
        """
        Тест метода get_board для получения данных конкретной доски.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_boards[0]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_board
        result = self.api.get_board(self.test_token, 301)

        # Проверяем результат
        self.assertEqual(result, self.test_boards[0])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/boards/301",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_board(self, mock_request):
        """
        Тест метода change_board для изменения данных доски.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 301, "title": "Updated Board", "projectId": 202}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_board
        result = self.api.change_board(
            self.test_token,
            301,
            title="Updated Board",
            projectId=202
        )

        # Проверяем результат
        self.assertEqual(result, {"id": 301, "title": "Updated Board", "projectId": 202})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/boards/301",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"deleted": False, "title": "Updated Board", "projectId": 202},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_board(self, mock_request):
        """
        Тест метода delete_board для удаления доски.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_board
        self.api.delete_board(self.test_token, 301)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            "https://test.yougile.com/api-v2/boards/301",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_columns(self, mock_request):
        """
        Тест метода get_columns для получения списка колонок.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_columns}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_columns
        result = self.api.get_columns(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_columns)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.columns, self.test_columns)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/columns",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_create_column(self, mock_request):
        """
        Тест метода create_column для создания новой колонки.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": {"id": 403, "title": "New Column", "boardId": 301, "color": "#0000FF"}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_column
        result = self.api.create_column(self.test_token, "New Column", "#0000FF", 301)

        # Проверяем результат
        self.assertEqual(result, {"id": 403, "title": "New Column", "boardId": 301, "color": "#0000FF"})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "POST",
            "https://test.yougile.com/api-v2/columns",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"title": "New Column", "color": "#0000FF", "boardId": 301},
            timeout=30
        )

    @patch('requests.request')
    def test_get_column(self, mock_request):
        """
        Тест метода get_column для получения данных конкретной колонки.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_columns[0]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_column
        result = self.api.get_column(self.test_token, 401)

        # Проверяем результат
        self.assertEqual(result, self.test_columns[0])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/columns/401",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_column(self, mock_request):
        """
        Тест метода change_column для изменения данных колонки.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 401, "title": "Updated Column", "color": "#00FFFF"}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_column
        result = self.api.change_column(
            self.test_token,
            401,
            title="Updated Column",
            color="#00FFFF"
        )

        # Проверяем результат
        self.assertEqual(result, {"id": 401, "title": "Updated Column", "color": "#00FFFF"})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/columns/401",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"deleted": False, "title": "Updated Column", "color": "#00FFFF"},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_column(self, mock_request):
        """
        Тест метода delete_column для удаления колонки.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_column
        self.api.delete_column(self.test_token, 401)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            "https://test.yougile.com/api-v2/columns/401",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_tasks(self, mock_request):
        """
        Тест метода get_tasks для получения списка задач.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_tasks}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_tasks
        result = self.api.get_tasks(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_tasks)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.tasks, self.test_tasks)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/task-list",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_tasks_reverse(self, mock_request):
        """
        Тест метода get_tasks_reverse для получения списка задач в обратном порядке.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_tasks[::-1]}  # Обратный порядок
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_tasks_reverse
        result = self.api.get_tasks_reverse(self.test_token)

        # Проверяем результат
        self.assertEqual(result, self.test_tasks[::-1])

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.tasks, self.test_tasks[::-1])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/tasks",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_create_task(self, mock_request):
        """
        Тест метода create_task для создания новой задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 503, "title": "New Task", "columnId": 401}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод create_task
        result = self.api.create_task(
            self.test_token,
            title="New Task",
            columnId=401,
            assigned=[101],
            description="Test description"
        )

        # Проверяем результат
        self.assertEqual(result, {"id": 503, "title": "New Task", "columnId": 401})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://test.yougile.com/api-v2/tasks")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.test_token}")
        self.assertEqual(kwargs["json"]["title"], "New Task")
        self.assertEqual(kwargs["json"]["columnId"], 401)
        self.assertEqual(kwargs["json"]["assigned"], [101])
        self.assertEqual(kwargs["json"]["description"], "Test description")

    @patch('requests.request')
    def test_get_task(self, mock_request):
        """
        Тест метода get_task для получения данных конкретной задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_tasks[0]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_task
        result = self.api.get_task(self.test_token, 501)

        # Проверяем результат
        self.assertEqual(result, self.test_tasks[0])

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/tasks/501",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_task(self, mock_request):
        """
        Тест метода change_task для изменения данных задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"id": 501, "title": "Updated Task", "completed": True}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_task
        result = self.api.change_task(
            self.test_token,
            501,
            title="Updated Task",
            completed=True
        )

        # Проверяем результат
        self.assertEqual(result, {"id": 501, "title": "Updated Task", "completed": True})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/tasks/501",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"title": "Updated Task", "completed": True},
            timeout=30
        )

    @patch('requests.request')
    def test_delete_task(self, mock_request):
        """
        Тест метода delete_task для удаления задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод delete_task
        self.api.delete_task(self.test_token, 501)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "DELETE",
            "https://test.yougile.com/api-v2/tasks/501",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_get_chat_subscribers(self, mock_request):
        """
        Тест метода get_chat_subscribers для получения списка подписчиков чата задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": self.test_chat_subscribers}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод get_chat_subscribers
        result = self.api.get_chat_subscribers(self.test_token, 501)

        # Проверяем результат
        self.assertEqual(result, self.test_chat_subscribers)

        # Проверяем, что результат кэшируется
        self.assertEqual(self.api.chat_subscribers, self.test_chat_subscribers)

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "GET",
            "https://test.yougile.com/api-v2/tasks/501/chat-subscribers",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json=None,
            timeout=30
        )

    @patch('requests.request')
    def test_change_chat_subscribers(self, mock_request):
        """
        Тест метода change_chat_subscribers для изменения списка подписчиков чата задачи.
        """
        # Настраиваем мок для requests.request
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": {"success": True}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Вызываем метод change_chat_subscribers
        result = self.api.change_chat_subscribers(self.test_token, 501, [101])

        # Проверяем результат
        self.assertEqual(result, {"success": True})

        # Проверяем, что requests.request был вызван с правильными параметрами
        mock_request.assert_called_once_with(
            "PUT",
            "https://test.yougile.com/api-v2/tasks/501/chat-subscribers",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            },
            params=None,
            json={"content": [101]},
            timeout=30
        )


if __name__ == '__main__':
    unittest.main()
