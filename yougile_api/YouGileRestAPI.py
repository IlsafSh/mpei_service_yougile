"""
------------------------------------------------------------
Обёртка над REST API YouGile v2.0
------------------------------------------------------------
Документация API: https://ru.yougile.com/api-v2#/
------------------------------------------------------------
"""

from typing import Any, Dict, List, Optional, Union
import requests
import logging
import os
import sys
from requests.exceptions import RequestException, HTTPError, Timeout


class YouGileRestAPI:
    """
    Класс-обёртка над REST v2 YouGile.

    ───────────────────────────────────────────────────────
    * Памятка по порядку работы:
        1.  Получаем список компаний    →  get_companies()
        2.  Создаём / берём API-ключ    →  create_key() / get_keys()
        3.  Передаём ключ в остальные методы как `token`.
    *   Все *get_* методы кешируют результат в одноимённые self.*
        (если нужно «живое» состояние — просто вызывайте их повторно).
    *   Любую ошибку API (статус ≠ 200) метод _request() поднимает как
        исключение → удобно оборачивать вызовы try/except в основном коде.
    """

    # --------------------------------------------------------------------- #
    #                          ️  ОСНОВЫ / НАСТРОЙКА                       #
    # --------------------------------------------------------------------- #

    def __init__(
        self,
        base_url: str = "https://ru.yougile.com/api-v2",
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Инициализация клиента.
        :param base_url: базовый URL API (может пригодиться на тестовом стенде)
        :param logger: логгер для записи информации о запросах и ошибках
        """
        self.url = base_url.rstrip("/")

        # Находим корень проекта и создаем директорию для диагностических файлов
        self.project_root = self._find_project_root()
        self.diagnostic_dir = os.path.join(self.project_root, "diagnostic_files")
        os.makedirs(self.diagnostic_dir, exist_ok=True)

        # Настраиваем логирование
        self.logger = logger or self._setup_logging()
        self.logger.info("Инициализация YouGile API клиента...")

        # «кеш» для списковых запросов – для повторного использования
        self.companies: List[Dict[str, Any]] = []
        self.keys: List[Dict[str, Any]] = []
        self.users: List[Dict[str, Any]] = []
        self.projects: List[Dict[str, Any]] = []
        self.boards: List[Dict[str, Any]] = []
        self.columns: List[Dict[str, Any]] = []
        self.tasks: List[Dict[str, Any]] = []
        self.project_roles: List[Dict[str, Any]] = []
        self.sprint_stickers: List[Dict[str, Any]] = []
        self.string_stickers: List[Dict[str, Any]] = []
        self.webhooks: List[Dict[str, Any]] = []

    def _find_project_root(self) -> str:
        """
        Находит корневую директорию проекта.
        Ищет вверх по дереву директорий, пока не найдет main.py или requirements.txt.

        :return: Абсолютный путь к корневой директории проекта
        """
        # Начинаем с текущей директории
        current_dir = os.path.abspath(os.getcwd())

        # Ищем вверх по дереву директорий
        while True:
            # Проверяем наличие маркеров корневой директории проекта
            if os.path.exists(os.path.join(current_dir, "main.py")) or \
               os.path.exists(os.path.join(current_dir, "requirements.txt")):
                return current_dir

            # Переходим на уровень выше
            parent_dir = os.path.dirname(current_dir)

            # Если достигли корня файловой системы, возвращаем текущую директорию
            if parent_dir == current_dir:
                return os.getcwd()

            current_dir = parent_dir

    def _setup_logging(self):
        """
        Настройка логирования в файл и консоль.
        Автоматически создает директорию diagnostic_files и настраивает вывод логов.
        """
        logger = logging.getLogger('yougile_api')
        logger.setLevel(logging.DEBUG)

        # Проверяем, не настроены ли уже обработчики для этого логгера
        if not logger.handlers:
            # Создаем обработчик для записи в файл
            log_file = os.path.join(self.diagnostic_dir, 'yougile_api.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # Создаем обработчик для вывода в консоль
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Создаем форматтер для логов
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Добавляем обработчики к логгеру
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

            logger.info(f"Логирование настроено. Файл логов: {log_file}")

        return logger

    # ------------------------- ВНУТРЕННЯЯ КУХНЯ --------------------------- #

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        error_msg: str = "Ошибка при выполнении запроса к API",
    ) -> Dict[str, Any]:
        """
        Универсальный запрос к API.
        Добавляет заголовок Content-Type, Bearer-токен (если указан),
        бросает исключение, если код ответа ≠ 200.
        Возвращает «content», если YouGile заворачивает данные в обёртку.

        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param path: путь к эндпоинту API
        :param token: Bearer токен для авторизации
        :param params: параметры запроса (query string)
        :param json: тело запроса в формате JSON
        :param timeout: таймаут запроса в секундах
        :param error_msg: сообщение об ошибке для логирования
        :return: данные ответа API
        """
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{self.url}{path}"
        self.logger.debug(f"Выполняется {method} запрос к {url}")
        self.logger.debug(f"Тело запроса: {json}")
        try:
            resp = requests.request(
                method, url,
                headers=headers,
                params=params,
                json=json,
                timeout=timeout
            )
            resp.raise_for_status()

            # Проверка на пустой ответ (например, для DELETE запросов)
            if not resp.content or len(resp.content) == 0:
                return None

            try:
                data = resp.json()
                if isinstance(data, dict) and "content" in data:
                    return data["content"]
                return data
            except ValueError:
                # Если ответ не может быть преобразован в JSON
                self.logger.debug(f"Ответ не содержит JSON: {resp.content}")
                return None

        except HTTPError as e:
            status_code = getattr(e.response, 'status_code', 'неизвестно')
            self.logger.error(f"{error_msg}: HTTP ошибка {status_code}")
            if hasattr(e, 'response') and e.response and hasattr(e.response, 'content'):
                try:
                    error_data = e.response.json()
                    self.logger.error(f"Детали ошибки: {error_data}")
                except (ValueError, AttributeError):
                    self.logger.error(f"Тело ответа: {e.response.content}")
            raise

        except Timeout:
            self.logger.error(f"{error_msg}: превышен таймаут {timeout} секунд")
            raise

        except RequestException as e:
            self.logger.error(f"{error_msg}: {str(e)}")
            raise

        except ValueError as e:
            self.logger.error(f"{error_msg}: ошибка при разборе JSON ответа: {str(e)}")
            raise

    # ===================================================================== #
    #                               1.  AUTH                                #
    # ===================================================================== #

    def get_companies(self, login: str, password: str, name: str = "") -> List[Dict[str, Any]]:
        """
        Авторизация → получить список компаний, к которым доступен пользователь.

        :param login: логин пользователя (email)
        :param password: пароль пользователя
        :param name: опциональное имя для фильтрации компаний
        :return: список компаний
        """
        self.logger.info(f"Получение списка компаний для пользователя {login}")
        self.companies = self._request(
            "POST",
            "/auth/companies",
            json={"login": login, "password": password, "name": name},
            error_msg=f"Ошибка при получении списка компаний для {login}"
        )
        return self.companies

    def get_keys(self, login: str, password: str, companyId: str) -> List[Dict[str, Any]]:
        """
        Авторизация → получить все сохранённые API-ключи для конкретной компании.

        :param login: логин пользователя (email)
        :param password: пароль пользователя
        :param companyId: ID компании
        :return: список API-ключей
        """
        self.logger.info(f"Получение списка API-ключей для компании {companyId}")
        self.keys = self._request(
            "POST",
            "/auth/keys/get",
            json={"login": login, "password": password, "companyId": companyId},
            error_msg=f"Ошибка при получении списка API-ключей для компании {companyId}"
        )
        return self.keys

    def create_key(self, login: str, password: str, companyId: str) -> Dict[str, Any]:
        """
        Авторизация → создать новый API-ключ (Bearer token).

        :param login: логин пользователя (email)
        :param password: пароль пользователя
        :param companyId: ID компании
        :return: информация о созданном API-ключе
        """
        self.logger.info(f"Создание нового API-ключа для компании {companyId}")
        return self._request(
            "POST",
            "/auth/keys",
            json={"login": login, "password": password, "companyId": companyId},
            error_msg=f"Ошибка при создании API-ключа для компании {companyId}"
        )

    def delete_key(self, key: str) -> Dict[str, Any]:
        """
        Авторизация → удалить (отозвать) ключ по его значению.

        :param key: значение API-ключа для удаления
        :return: результат операции
        """
        self.logger.info(f"Удаление API-ключа")
        return self._request(
            "DELETE",
            f"/auth/keys/{key}",
            error_msg=f"Ошибка при удалении API-ключа"
        )

    # ===================================================================== #
    #                               2.  USERS                               #
    # ===================================================================== #

    def get_users(self, token: str) -> List[Dict[str, Any]]:
        """
        Сотрудники → получить всех юзеров компании.

        :param token: API-ключ
        :return: список пользователей компании
        """
        self.logger.info("Получение списка пользователей компании")
        self.users = self._request(
            "GET",
            "/users",
            token=token,
            error_msg="Ошибка при получении списка пользователей"
        )
        return self.users

    def create_user(self, token: str, email: str, isAdmin: bool = False) -> Dict[str, Any]:
        """
        Сотрудники → пригласить нового пользователя по e-mail.

        :param token: API-ключ
        :param email: email нового пользователя
        :param isAdmin: флаг администратора
        :return: информация о созданном пользователе
        """
        self.logger.info(f"Создание нового пользователя с email {email}")
        return self._request(
            "POST",
            "/users",
            token=token,
            json={"email": email, "isAdmin": isAdmin},
            error_msg=f"Ошибка при создании пользователя с email {email}"
        )

    def get_user(self, token: str, userId: str) -> Dict[str, Any]:
        """
        Сотрудники → получить данные конкретного сотрудника по ID.

        :param token: API-ключ
        :param userId: ID пользователя
        :return: информация о пользователе
        """
        self.logger.info(f"Получение информации о пользователе {userId}")
        return self._request(
            "GET",
            f"/users/{userId}",
            token=token,
            error_msg=f"Ошибка при получении информации о пользователе {userId}"
        )

    def change_user(self, token: str, userId: str, isAdmin: bool = False) -> Dict[str, Any]:
        """
        Сотрудники → изменить флаг администратора у пользователя.

        :param token: API-ключ
        :param userId: ID пользователя
        :param isAdmin: новое значение флага администратора
        :return: обновленная информация о пользователе
        """
        self.logger.info(f"Изменение прав пользователя {userId}")
        return self._request(
            "PUT",
            f"/users/{userId}",
            token=token,
            json={"isAdmin": isAdmin},
            error_msg=f"Ошибка при изменении прав пользователя {userId}"
        )

    def delete_user(self, token: str, userId: str) -> None:
        """
        Сотрудники → удалить сотрудника (безвозвратно).

        :param token: API-ключ
        :param userId: ID пользователя для удаления
        """
        self.logger.info(f"Удаление пользователя {userId}")
        self._request(
            "DELETE",
            f"/users/{userId}",
            token=token,
            error_msg=f"Ошибка при удалении пользователя {userId}"
        )

    # ===================================================================== #
    #                              3.  PROJECTS                             #
    # ===================================================================== #

    def get_projects(self, token: str) -> List[Dict[str, Any]]:
        """
        Проекты → получить список проектов компании.

        :param token: API-ключ
        :return: список проектов компании
        """
        self.logger.info("Получение списка проектов компании")
        self.projects = self._request(
            "GET",
            "/projects",
            token=token,
            error_msg="Ошибка при получении списка проектов"
        )
        return self.projects

    def create_project(self, token: str, title: str, users: Dict[str, str]) -> Dict[str, Any]:
        """
        Проекты → создать новый проект с указанными участниками.

        :param token: API-ключ
        :param title: название проекта
        :param users: словарь с ID пользователей и их ролями, например {"user_id": "admin"}
        :return: информация о созданном проекте
        """
        self.logger.info(f"Создание нового проекта '{title}'")
        return self._request(
            "POST",
            "/projects",
            token=token,
            json={"title": title, "users": users},
            error_msg=f"Ошибка при создании проекта '{title}'"
        )

    def get_project(self, token: str, projectId: str) -> Dict[str, Any]:
        """
        Проекты → получить один проект по его ID.

        :param token: API-ключ
        :param projectId: ID проекта
        :return: информация о проекте
        """
        self.logger.info(f"Получение информации о проекте {projectId}")
        return self._request(
            "GET",
            f"/projects/{projectId}",
            token=token,
            error_msg=f"Ошибка при получении информации о проекте {projectId}"
        )

    def change_project(
        self,
        token: str,
        projectId: str,
        title: Optional[str] = None,
        users: Optional[Dict[str, str]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Проекты → переименовать, изменить состав участников или пометить на удаление.

        :param token: API-ключ
        :param projectId: ID проекта
        :param title: новое название проекта (опционально)
        :param users: новый словарь с ID пользователей и их ролями (опционально)
        :param delete: пометить проект на удаление
        :return: обновленная информация о проекте
        """
        self.logger.info(f"Изменение проекта {projectId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if users is not None:
            payload["users"] = users
        return self._request(
            "PUT",
            f"/projects/{projectId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении проекта {projectId}"
        )

    def delete_project(self, token: str, projectId: str) -> None:
        """
        Проекты → физически удалить проект.

        :param token: API-ключ
        :param projectId: ID проекта для удаления
        """
        self.logger.info(f"Удаление проекта {projectId}")
        self._request(
            "DELETE",
            f"/projects/{projectId}",
            token=token,
            error_msg=f"Ошибка при удалении проекта {projectId}"
        )

    # ===================================================================== #
    #                               4.  BOARDS                              #
    # ===================================================================== #

    def get_boards(self, token: str) -> List[Dict[str, Any]]:
        """
        Доски → получить список всех досок во всех проектах.

        :param token: API-ключ
        :return: список досок
        """
        self.logger.info("Получение списка досок")
        self.boards = self._request(
            "GET",
            "/boards",
            token=token,
            error_msg="Ошибка при получении списка досок"
        )
        return self.boards

    def create_board(
        self,
        token: str,
        title: str,
        projectId: str,
        stickers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Доски → создать новую доску внутри проекта.

        :param token: API-ключ
        :param title: название доски
        :param projectId: ID проекта
        :param stickers: настройки стикеров (опционально)
        :return: информация о созданной доске
        """
        self.logger.info(f"Создание новой доски '{title}' в проекте {projectId}")
        payload = {"title": title, "projectId": projectId}
        if stickers is not None:
            payload["stickers"] = stickers
        return self._request(
            "POST",
            "/boards",
            token=token,
            json=payload,
            error_msg=f"Ошибка при создании доски '{title}' в проекте {projectId}"
        )

    def get_board(self, token: str, boardId: str) -> Dict[str, Any]:
        """
        Доски → получить одну доску по её ID.

        :param token: API-ключ
        :param boardId: ID доски
        :return: информация о доске
        """
        self.logger.info(f"Получение информации о доске {boardId}")
        return self._request(
            "GET",
            f"/boards/{boardId}",
            token=token,
            error_msg=f"Ошибка при получении информации о доске {boardId}"
        )

    def change_board(
        self,
        token: str,
        boardId: str,
        title: Optional[str] = None,
        stickers: Optional[Dict[str, Any]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Доски → переименовать, изменить настройки стикеров или пометить на удаление.

        :param token: API-ключ
        :param boardId: ID доски
        :param title: новое название доски (опционально)
        :param stickers: новые настройки стикеров (опционально)
        :param delete: пометить доску на удаление
        :return: обновленная информация о доске
        """
        self.logger.info(f"Изменение доски {boardId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if stickers is not None:
            payload["stickers"] = stickers
        return self._request(
            "PUT",
            f"/boards/{boardId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении доски {boardId}"
        )

    def delete_board(self, token: str, boardId: str) -> None:
        """
        Доски → физически удалить доску.

        :param token: API-ключ
        :param boardId: ID доски для удаления
        """
        self.logger.info(f"Удаление доски {boardId}")
        self._request(
            "DELETE",
            f"/boards/{boardId}",
            token=token,
            error_msg=f"Ошибка при удалении доски {boardId}"
        )

    # ===================================================================== #
    #                              5.  COLUMNS                              #
    # ===================================================================== #

    def get_columns(self, token: str, boardId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Колонки → получить список колонок на доске.

        :param token: API-ключ
        :param boardId: ID доски (опционально)
        :return: список колонок
        """
        self.logger.info(f"Получение списка колонок{' для доски ' + boardId if boardId else ''}")
        params = {"boardId": boardId} if boardId else None
        self.columns = self._request(
            "GET",
            "/columns",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка колонок{' для доски ' + boardId if boardId else ''}"
        )
        return self.columns

    def create_column(
        self,
        token: str,
        title: str,
        color: int,
        boardId: str,
        position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Колонки → создать новую колонку на доске.

        :param token: API-ключ
        :param title: название колонки
        :param color: цвет колонки (число от 1 до 16, соответствующее цвету)
        :param boardId: ID доски
        :param position: позиция колонки (опционально)
        :return: информация о созданной колонке
        """
        self.logger.info(f"Создание новой колонки '{title}' на доске {boardId}")
        payload = {"title": title, "color": color, "boardId": boardId}
        if position is not None:
            payload["position"] = position
        return self._request(
            "POST",
            "/columns",
            token=token,
            json=payload,
            error_msg=f"Ошибка при создании колонки '{title}' на доске {boardId}"
        )

    def get_column(self, token: str, columnId: str) -> Dict[str, Any]:
        """
        Колонки → получить одну колонку по её ID.

        :param token: API-ключ
        :param columnId: ID колонки
        :return: информация о колонке
        """
        self.logger.info(f"Получение информации о колонке {columnId}")
        return self._request(
            "GET",
            f"/columns/{columnId}",
            token=token,
            error_msg=f"Ошибка при получении информации о колонке {columnId}"
        )

    def change_column(
        self,
        token: str,
        columnId: str,
        title: Optional[str] = None,
        color: Optional[str] = None,
        position: Optional[int] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Колонки → переименовать, изменить цвет, позицию или пометить на удаление.

        :param token: API-ключ
        :param columnId: ID колонки
        :param title: новое название колонки (опционально)
        :param color: новый цвет колонки (опционально)
        :param position: новая позиция колонки (опционально)
        :param delete: пометить колонку на удаление
        :return: обновленная информация о колонке
        """
        self.logger.info(f"Изменение колонки {columnId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if color is not None:
            payload["color"] = color
        if position is not None:
            payload["position"] = position
        return self._request(
            "PUT",
            f"/columns/{columnId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении колонки {columnId}"
        )

    def delete_column(self, token: str, columnId: str) -> None:
        """
        Колонки → физически удалить колонку.

        :param token: API-ключ
        :param columnId: ID колонки для удаления
        """
        self.logger.info(f"Удаление колонки {columnId}")
        self._request(
            "DELETE",
            f"/columns/{columnId}",
            token=token,
            error_msg=f"Ошибка при удалении колонки {columnId}"
        )

    # ===================================================================== #
    #                               6.  TASKS                               #
    # ===================================================================== #

    def get_tasks(self, token: str, columnId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Задачи → получить список задач в колонке.

        :param token: API-ключ
        :param columnId: ID колонки (опционально)
        :return: список задач
        """
        self.logger.info(f"Получение списка задач{' для колонки ' + columnId if columnId else ''}")
        params = {"columnId": columnId} if columnId else None
        self.tasks = self._request(
            "GET",
            "/tasks",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка задач{' для колонки ' + columnId if columnId else ''}"
        )
        return self.tasks

    def get_tasks_reverse(self, token: str, columnId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Задачи → получить список задач в колонке в обратном порядке.

        :param token: API-ключ
        :param columnId: ID колонки (опционально)
        :return: список задач в обратном порядке
        """
        tasks = self.get_tasks(token, columnId)
        return list(reversed(tasks))

    def create_task(
        self,
        token: str,
        title: str,
        columnId: str,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
        completed: Optional[bool] = None,
        subtasks: Optional[List[str]] = None,
        assigned: Optional[List[str]] = None,
        deadline: Optional[Dict[str, Any]] = None,
        timeTracking: Optional[Dict[str, Any]] = None,
        checklists: Optional[List[Dict[str, Any]]] = None,
        stickers: Optional[Dict[str, Any]] = None,
        stopwatch: Optional[Dict[str, Any]] = None,
        timer: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Задачи → создать новую задачу в колонке.

        :param token: API-ключ
        :param title: название задачи
        :param columnId: ID колонки
        :param description: описание задачи (опционально)
        :param archived: задача в архиве (опционально)
        :param completed: задача выполнена (опционально)
        :param subtasks: список ID подзадач (опционально)
        :param assigned: список ID пользователей, назначенных на задачу (опционально)
        :param deadline: дедлайн задачи (опционально)
        :param timeTracking: тайм-трекинг задачи (опционально)
        :param checklists: чек-листы задачи (опционально)
        :param stickers: стикеры задачи (опционально)
        :param stopwatch: секундомер задачи (опционально)
        :param timer: таймер задачи (опционально)
        :return: информация о созданной задаче
        """
        self.logger.info(f"Создание новой задачи '{title}' в колонке {columnId}")
        payload: Dict[str, Any] = {"title": title, "columnId": columnId}

        if description is not None:
            payload["description"] = description
        if archived is not None:
            payload["archived"] = archived
        if completed is not None:
            payload["completed"] = completed
        if subtasks is not None:
            payload["subtasks"] = subtasks
        if assigned is not None:
            payload["assigned"] = assigned
        if deadline is not None:
            payload["deadline"] = deadline
        if timeTracking is not None:
            payload["timeTracking"] = timeTracking
        if checklists is not None:
            payload["checklists"] = checklists
        if stickers is not None:
            payload["stickers"] = stickers
        if stopwatch is not None:
            payload["stopwatch"] = stopwatch
        if timer is not None:
            payload["timer"] = timer

        return self._request(
            "POST",
            "/tasks",
            token=token,
            json=payload,
            error_msg=f"Ошибка при создании задачи '{title}' в колонке {columnId}"
        )

    def get_task(self, token: str, taskId: str) -> Dict[str, Any]:
        """
        Задачи → получить одну задачу по её ID.

        :param token: API-ключ
        :param taskId: ID задачи
        :return: информация о задаче
        """
        self.logger.info(f"Получение информации о задаче {taskId}")
        return self._request(
            "GET",
            f"/tasks/{taskId}",
            token=token,
            error_msg=f"Ошибка при получении информации о задаче {taskId}"
        )

    def change_task(
        self,
        token: str,
        taskId: str,
        title: Optional[str] = None,
        columnId: Optional[str] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
        completed: Optional[bool] = None,
        subtasks: Optional[List[str]] = None,
        assigned: Optional[List[str]] = None,
        deadline: Optional[Dict[str, Any]] = None,
        timeTracking: Optional[Dict[str, Any]] = None,
        checklists: Optional[List[Dict[str, Any]]] = None,
        stickers: Optional[Dict[str, Any]] = None,
        stopwatch: Optional[Dict[str, Any]] = None,
        timer: Optional[Dict[str, Any]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Задачи → изменить задачу или пометить на удаление.

        :param token: API-ключ
        :param taskId: ID задачи
        :param title: новое название задачи (опционально)
        :param columnId: новый ID колонки (опционально)
        :param description: новое описание задачи (опционально)
        :param archived: задача в архиве (опционально)
        :param completed: задача выполнена (опционально)
        :param subtasks: новый список ID подзадач (опционально)
        :param assigned: новый список ID пользователей, назначенных на задачу (опционально)
        :param deadline: новый дедлайн задачи (опционально)
        :param timeTracking: новый тайм-трекинг задачи (опционально)
        :param checklists: новые чек-листы задачи (опционально)
        :param stickers: новые стикеры задачи (опционально)
        :param stopwatch: новый секундомер задачи (опционально)
        :param timer: новый таймер задачи (опционально)
        :param delete: пометить задачу на удаление
        :return: обновленная информация о задаче
        """
        self.logger.info(f"Изменение задачи {taskId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if columnId is not None:
            payload["columnId"] = columnId
        if description is not None:
            payload["description"] = description
        if archived is not None:
            payload["archived"] = archived
        if completed is not None:
            payload["completed"] = completed
        if subtasks is not None:
            payload["subtasks"] = subtasks
        if assigned is not None:
            payload["assigned"] = assigned
        if deadline is not None:
            payload["deadline"] = deadline
        if timeTracking is not None:
            payload["timeTracking"] = timeTracking
        if checklists is not None:
            payload["checklists"] = checklists
        if stickers is not None:
            payload["stickers"] = stickers
        if stopwatch is not None:
            payload["stopwatch"] = stopwatch
        if timer is not None:
            payload["timer"] = timer
        return self._request(
            "PUT",
            f"/tasks/{taskId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении задачи {taskId}"
        )

    def delete_task(self, token: str, taskId: str) -> None:
        """
        Задачи → физически удалить задачу.

        :param token: API-ключ
        :param taskId: ID задачи для удаления
        """
        self.logger.info(f"Удаление задачи {taskId}")
        self._request(
            "DELETE",
            f"/tasks/{taskId}",
            token=token,
            error_msg=f"Ошибка при удалении задачи {taskId}"
        )

    # ===================================================================== #
    #                            7.  DEPARTMENTS                            #
    # ===================================================================== #

    def get_departments(self, token: str) -> List[Dict[str, Any]]:
        """
        Отделы → получить список отделов компании.

        :param token: API-ключ
        :return: список отделов
        """
        self.logger.info("Получение списка отделов компании")
        self.departments = self._request(
            "GET",
            "/departments",
            token=token,
            error_msg="Ошибка при получении списка отделов"
        )
        return self.departments

    def create_department(self, token: str, title: str) -> Dict[str, Any]:
        """
        Отделы → создать новый отдел.

        :param token: API-ключ
        :param title: название отдела
        :return: информация о созданном отделе
        """
        self.logger.info(f"Создание нового отдела '{title}'")
        return self._request(
            "POST",
            "/departments",
            token=token,
            json={"title": title},
            error_msg=f"Ошибка при создании отдела '{title}'"
        )

    def get_department(self, token: str, departmentId: str) -> Dict[str, Any]:
        """
        Отделы → получить один отдел по его ID.

        :param token: API-ключ
        :param departmentId: ID отдела
        :return: информация об отделе
        """
        self.logger.info(f"Получение информации об отделе {departmentId}")
        return self._request(
            "GET",
            f"/departments/{departmentId}",
            token=token,
            error_msg=f"Ошибка при получении информации об отделе {departmentId}"
        )

    def change_department(
        self,
        token: str,
        departmentId: str,
        title: Optional[str] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Отделы → переименовать или пометить на удаление.

        :param token: API-ключ
        :param departmentId: ID отдела
        :param title: новое название отдела (опционально)
        :param delete: пометить отдел на удаление
        :return: обновленная информация об отделе
        """
        self.logger.info(f"Изменение отдела {departmentId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        return self._request(
            "PUT",
            f"/departments/{departmentId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении отдела {departmentId}"
        )

    def delete_department(self, token: str, departmentId: str) -> None:
        """
        Отделы → физически удалить отдел.

        :param token: API-ключ
        :param departmentId: ID отдела для удаления
        """
        self.logger.info(f"Удаление отдела {departmentId}")
        self._request(
            "DELETE",
            f"/departments/{departmentId}",
            token=token,
            error_msg=f"Ошибка при удалении отдела {departmentId}"
        )

    # ===================================================================== #
    #                             8.  EMPLOYEES                             #
    # ===================================================================== #

    def get_employees(self, token: str, departmentId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Сотрудники → получить список сотрудников отдела.

        :param token: API-ключ
        :param departmentId: ID отдела (опционально)
        :return: список сотрудников
        """
        self.logger.info(f"Получение списка сотрудников{' отдела ' + departmentId if departmentId else ''}")
        params = {"departmentId": departmentId} if departmentId else None
        self.employees = self._request(
            "GET",
            "/employees",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка сотрудников{' отдела ' + departmentId if departmentId else ''}"
        )
        return self.employees

    def create_employee(
        self,
        token: str,
        userId: str,
        departmentId: str,
        position: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Сотрудники → добавить пользователя в отдел.

        :param token: API-ключ
        :param userId: ID пользователя
        :param departmentId: ID отдела
        :param position: должность (опционально)
        :return: информация о созданном сотруднике
        """
        self.logger.info(f"Добавление пользователя {userId} в отдел {departmentId}")
        payload = {"userId": userId, "departmentId": departmentId}
        if position is not None:
            payload["position"] = position
        return self._request(
            "POST",
            "/employees",
            token=token,
            json=payload,
            error_msg=f"Ошибка при добавлении пользователя {userId} в отдел {departmentId}"
        )

    def get_employee(self, token: str, employeeId: str) -> Dict[str, Any]:
        """
        Сотрудники → получить одного сотрудника по его ID.

        :param token: API-ключ
        :param employeeId: ID сотрудника
        :return: информация о сотруднике
        """
        self.logger.info(f"Получение информации о сотруднике {employeeId}")
        return self._request(
            "GET",
            f"/employees/{employeeId}",
            token=token,
            error_msg=f"Ошибка при получении информации о сотруднике {employeeId}"
        )

    def change_employee(
        self,
        token: str,
        employeeId: str,
        position: Optional[str] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Сотрудники → изменить должность или пометить на удаление.

        :param token: API-ключ
        :param employeeId: ID сотрудника
        :param position: новая должность (опционально)
        :param delete: пометить сотрудника на удаление
        :return: обновленная информация о сотруднике
        """
        self.logger.info(f"Изменение сотрудника {employeeId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if position is not None:
            payload["position"] = position
        return self._request(
            "PUT",
            f"/employees/{employeeId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении сотрудника {employeeId}"
        )

    def delete_employee(self, token: str, employeeId: str) -> None:
        """
        Сотрудники → физически удалить сотрудника из отдела.

        :param token: API-ключ
        :param employeeId: ID сотрудника для удаления
        """
        self.logger.info(f"Удаление сотрудника {employeeId}")
        self._request(
            "DELETE",
            f"/employees/{employeeId}",
            token=token,
            error_msg=f"Ошибка при удалении сотрудника {employeeId}"
        )

    # ===================================================================== #
    #                            9.  GROUP CHATS                            #
    # ===================================================================== #

    def get_group_chats(self, token: str) -> List[Dict[str, Any]]:
        """
        Групповые чаты → получить список групповых чатов.

        :param token: API-ключ
        :return: список групповых чатов
        """
        self.logger.info("Получение списка групповых чатов")
        self.group_chats = self._request(
            "GET",
            "/groupchats",
            token=token,
            error_msg="Ошибка при получении списка групповых чатов"
        )
        return self.group_chats

    def create_group_chat(
        self,
        token: str,
        title: str,
        users: List[str],
    ) -> Dict[str, Any]:
        """
        Групповые чаты → создать новый групповой чат.

        :param token: API-ключ
        :param title: название чата
        :param users: список ID пользователей-участников чата
        :return: информация о созданном групповом чате
        """
        self.logger.info(f"Создание нового группового чата '{title}'")
        return self._request(
            "POST",
            "/groupchats",
            token=token,
            json={"title": title, "users": users},
            error_msg=f"Ошибка при создании группового чата '{title}'"
        )

    def get_group_chat(self, token: str, chatId: str) -> Dict[str, Any]:
        """
        Групповые чаты → получить один групповой чат по его ID.

        :param token: API-ключ
        :param chatId: ID группового чата
        :return: информация о групповом чате
        """
        self.logger.info(f"Получение информации о групповом чате {chatId}")
        return self._request(
            "GET",
            f"/groupchats/{chatId}",
            token=token,
            error_msg=f"Ошибка при получении информации о групповом чате {chatId}"
        )

    def change_group_chat(
        self,
        token: str,
        chatId: str,
        title: Optional[str] = None,
        users: Optional[List[str]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Групповые чаты → переименовать, изменить состав участников или пометить на удаление.

        :param token: API-ключ
        :param chatId: ID группового чата
        :param title: новое название чата (опционально)
        :param users: новый список ID пользователей-участников чата (опционально)
        :param delete: пометить групповой чат на удаление
        :return: обновленная информация о групповом чате
        """
        self.logger.info(f"Изменение группового чата {chatId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if users is not None:
            payload["users"] = users
        return self._request(
            "PUT",
            f"/groupchats/{chatId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении группового чата {chatId}"
        )

    def delete_group_chat(self, token: str, chatId: str) -> None:
        """
        Групповые чаты → физически удалить групповой чат.

        :param token: API-ключ
        :param chatId: ID группового чата для удаления
        """
        self.logger.info(f"Удаление группового чата {chatId}")
        self._request(
            "DELETE",
            f"/groupchats/{chatId}",
            token=token,
            error_msg=f"Ошибка при удалении группового чата {chatId}"
        )

    # ===================================================================== #
    #                           10.  CHAT MESSAGES                          #
    # ===================================================================== #

    def get_chat_messages(
        self,
        token: str,
        chatId: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Сообщения чатов → получить список сообщений в чате.

        :param token: API-ключ
        :param chatId: ID чата
        :param limit: максимальное количество сообщений (по умолчанию 50)
        :param offset: смещение для пагинации (по умолчанию 0)
        :return: список сообщений
        """
        self.logger.info(f"Получение списка сообщений в чате {chatId}")
        return self._request(
            "GET",
            "/chatmessages",
            token=token,
            params={"chatId": chatId, "limit": limit, "offset": offset},
            error_msg=f"Ошибка при получении списка сообщений в чате {chatId}"
        )

    def create_chat_message(
        self,
        token: str,
        chatId: str,
        text: str,
    ) -> Dict[str, Any]:
        """
        Сообщения чатов → отправить новое сообщение в чат.

        :param token: API-ключ
        :param chatId: ID чата
        :param text: текст сообщения
        :return: информация о созданном сообщении
        """
        self.logger.info(f"Отправка сообщения в чат {chatId}")
        return self._request(
            "POST",
            "/chatmessages",
            token=token,
            json={"chatId": chatId, "text": text},
            error_msg=f"Ошибка при отправке сообщения в чат {chatId}"
        )

    def get_chat_message(self, token: str, messageId: str) -> Dict[str, Any]:
        """
        Сообщения чатов → получить одно сообщение по его ID.

        :param token: API-ключ
        :param messageId: ID сообщения
        :return: информация о сообщении
        """
        self.logger.info(f"Получение информации о сообщении {messageId}")
        return self._request(
            "GET",
            f"/chatmessages/{messageId}",
            token=token,
            error_msg=f"Ошибка при получении информации о сообщении {messageId}"
        )

    def change_chat_message(
        self,
        token: str,
        messageId: str,
        text: str,
    ) -> Dict[str, Any]:
        """
        Сообщения чатов → изменить текст сообщения.

        :param token: API-ключ
        :param messageId: ID сообщения
        :param text: новый текст сообщения
        :return: обновленная информация о сообщении
        """
        self.logger.info(f"Изменение сообщения {messageId}")
        return self._request(
            "PUT",
            f"/chatmessages/{messageId}",
            token=token,
            json={"text": text},
            error_msg=f"Ошибка при изменении сообщения {messageId}"
        )

    def delete_chat_message(self, token: str, messageId: str) -> None:
        """
        Сообщения чатов → удалить сообщение.

        :param token: API-ключ
        :param messageId: ID сообщения для удаления
        """
        self.logger.info(f"Удаление сообщения {messageId}")
        self._request(
            "DELETE",
            f"/chatmessages/{messageId}",
            token=token,
            error_msg=f"Ошибка при удалении сообщения {messageId}"
        )

    # ===================================================================== #
    #                          11.  PROJECT ROLES                           #
    # ===================================================================== #

    def get_project_roles(self, token: str, projectId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Роли проекта → получить список ролей в проекте.

        :param token: API-ключ
        :param projectId: ID проекта (опционально)
        :return: список ролей
        """
        self.logger.info(f"Получение списка ролей{' проекта ' + projectId if projectId else ''}")
        params = {"projectId": projectId} if projectId else None
        self.project_roles = self._request(
            "GET",
            "/projectroles",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка ролей{' проекта ' + projectId if projectId else ''}"
        )
        return self.project_roles

    def create_project_role(
        self,
        token: str,
        title: str,
        projectId: str,
        permissions: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Роли проекта → создать новую роль в проекте.

        :param token: API-ключ
        :param title: название роли
        :param projectId: ID проекта
        :param permissions: права роли
        :return: информация о созданной роли
        """
        self.logger.info(f"Создание новой роли '{title}' в проекте {projectId}")
        return self._request(
            "POST",
            "/projectroles",
            token=token,
            json={"title": title, "projectId": projectId, "permissions": permissions},
            error_msg=f"Ошибка при создании роли '{title}' в проекте {projectId}"
        )

    def get_project_role(self, token: str, roleId: str) -> Dict[str, Any]:
        """
        Роли проекта → получить одну роль по её ID.

        :param token: API-ключ
        :param roleId: ID роли
        :return: информация о роли
        """
        self.logger.info(f"Получение информации о роли {roleId}")
        return self._request(
            "GET",
            f"/projectroles/{roleId}",
            token=token,
            error_msg=f"Ошибка при получении информации о роли {roleId}"
        )

    def change_project_role(
        self,
        token: str,
        roleId: str,
        title: Optional[str] = None,
        permissions: Optional[Dict[str, bool]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Роли проекта → переименовать, изменить права или пометить на удаление.

        :param token: API-ключ
        :param roleId: ID роли
        :param title: новое название роли (опционально)
        :param permissions: новые права роли (опционально)
        :param delete: пометить роль на удаление
        :return: обновленная информация о роли
        """
        self.logger.info(f"Изменение роли {roleId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if permissions is not None:
            payload["permissions"] = permissions
        return self._request(
            "PUT",
            f"/projectroles/{roleId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении роли {roleId}"
        )

    def delete_project_role(self, token: str, roleId: str) -> None:
        """
        Роли проекта → физически удалить роль.

        :param token: API-ключ
        :param roleId: ID роли для удаления
        """
        self.logger.info(f"Удаление роли {roleId}")
        self._request(
            "DELETE",
            f"/projectroles/{roleId}",
            token=token,
            error_msg=f"Ошибка при удалении роли {roleId}"
        )

    # ===================================================================== #
    #                             12.  WEBHOOKS                             #
    # ===================================================================== #

    def get_webhooks(self, token: str) -> List[Dict[str, Any]]:
        """
        Вебхуки → получить список вебхуков.

        :param token: API-ключ
        :return: список вебхуков
        """
        self.logger.info("Получение списка вебхуков")
        self.webhooks = self._request(
            "GET",
            "/webhooks",
            token=token,
            error_msg="Ошибка при получении списка вебхуков"
        )
        return self.webhooks

    def create_webhook(
        self,
        token: str,
        url: str,
        events: List[str],
    ) -> Dict[str, Any]:
        """
        Вебхуки → создать новый вебхук.

        :param token: API-ключ
        :param url: URL вебхука
        :param events: список событий для отслеживания
        :return: информация о созданном вебхуке
        """
        self.logger.info(f"Создание нового вебхука для URL {url}")
        return self._request(
            "POST",
            "/webhooks",
            token=token,
            json={"url": url, "events": events},
            error_msg=f"Ошибка при создании вебхука для URL {url}"
        )

    def get_webhook(self, token: str, webhookId: str) -> Dict[str, Any]:
        """
        Вебхуки → получить один вебхук по его ID.

        :param token: API-ключ
        :param webhookId: ID вебхука
        :return: информация о вебхуке
        """
        self.logger.info(f"Получение информации о вебхуке {webhookId}")
        return self._request(
            "GET",
            f"/webhooks/{webhookId}",
            token=token,
            error_msg=f"Ошибка при получении информации о вебхуке {webhookId}"
        )

    def change_webhook(
        self,
        token: str,
        webhookId: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Вебхуки → изменить URL, события или пометить на удаление.

        :param token: API-ключ
        :param webhookId: ID вебхука
        :param url: новый URL вебхука (опционально)
        :param events: новый список событий для отслеживания (опционально)
        :param delete: пометить вебхук на удаление
        :return: обновленная информация о вебхуке
        """
        self.logger.info(f"Изменение вебхука {webhookId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if url is not None:
            payload["url"] = url
        if events is not None:
            payload["events"] = events
        return self._request(
            "PUT",
            f"/webhooks/{webhookId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении вебхука {webhookId}"
        )

    def delete_webhook(self, token: str, webhookId: str) -> None:
        """
        Вебхуки → физически удалить вебхук.

        :param token: API-ключ
        :param webhookId: ID вебхука для удаления
        """
        self.logger.info(f"Удаление вебхука {webhookId}")
        self._request(
            "DELETE",
            f"/webhooks/{webhookId}",
            token=token,
            error_msg=f"Ошибка при удалении вебхука {webhookId}"
        )

    # ===================================================================== #
    #                          13.  SPRINT STICKERS                         #
    # ===================================================================== #

    def get_sprint_stickers(self, token: str, boardId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Стикеры спринта → получить список стикеров спринта на доске.

        :param token: API-ключ
        :param boardId: ID доски (опционально)
        :return: список стикеров спринта
        """
        self.logger.info(f"Получение списка стикеров спринта{' на доске ' + boardId if boardId else ''}")
        params = {"boardId": boardId} if boardId else None
        self.sprint_stickers = self._request(
            "GET",
            "/sprintstickers",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка стикеров спринта{' на доске ' + boardId if boardId else ''}"
        )
        return self.sprint_stickers

    def create_sprint_sticker(
        self,
        token: str,
        title: str,
        boardId: str,
        states: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Стикеры спринта → создать новый стикер спринта на доске.

        :param token: API-ключ
        :param title: название стикера
        :param boardId: ID доски
        :param states: список состояний стикера
        :return: информация о созданном стикере спринта
        """
        self.logger.info(f"Создание нового стикера спринта '{title}' на доске {boardId}")
        return self._request(
            "POST",
            "/sprintstickers",
            token=token,
            json={"title": title, "boardId": boardId, "states": states},
            error_msg=f"Ошибка при создании стикера спринта '{title}' на доске {boardId}"
        )

    def get_sprint_sticker(self, token: str, stickerId: str) -> Dict[str, Any]:
        """
        Стикеры спринта → получить один стикер спринта по его ID.

        :param token: API-ключ
        :param stickerId: ID стикера спринта
        :return: информация о стикере спринта
        """
        self.logger.info(f"Получение информации о стикере спринта {stickerId}")
        return self._request(
            "GET",
            f"/sprintstickers/{stickerId}",
            token=token,
            error_msg=f"Ошибка при получении информации о стикере спринта {stickerId}"
        )

    def change_sprint_sticker(
        self,
        token: str,
        stickerId: str,
        title: Optional[str] = None,
        states: Optional[List[Dict[str, Any]]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Стикеры спринта → переименовать, изменить состояния или пометить на удаление.

        :param token: API-ключ
        :param stickerId: ID стикера спринта
        :param title: новое название стикера (опционально)
        :param states: новый список состояний стикера (опционально)
        :param delete: пометить стикер на удаление
        :return: обновленная информация о стикере спринта
        """
        self.logger.info(f"Изменение стикера спринта {stickerId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if states is not None:
            payload["states"] = states
        return self._request(
            "PUT",
            f"/sprintstickers/{stickerId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении стикера спринта {stickerId}"
        )

    def delete_sprint_sticker(self, token: str, stickerId: str) -> None:
        """
        Стикеры спринта → физически удалить стикер спринта.

        :param token: API-ключ
        :param stickerId: ID стикера спринта для удаления
        """
        self.logger.info(f"Удаление стикера спринта {stickerId}")
        self._request(
            "DELETE",
            f"/sprintstickers/{stickerId}",
            token=token,
            error_msg=f"Ошибка при удалении стикера спринта {stickerId}"
        )

    # ===================================================================== #
    #                         14.  STRING STICKERS                          #
    # ===================================================================== #

    def get_string_stickers(self, token: str, boardId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Текстовые стикеры → получить список текстовых стикеров на доске.

        :param token: API-ключ
        :param boardId: ID доски (опционально)
        :return: список текстовых стикеров
        """
        self.logger.info(f"Получение списка текстовых стикеров{' на доске ' + boardId if boardId else ''}")
        params = {"boardId": boardId} if boardId else None
        self.string_stickers = self._request(
            "GET",
            "/stringstickers",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка текстовых стикеров{' на доске ' + boardId if boardId else ''}"
        )
        return self.string_stickers

    def create_string_sticker(
        self,
        token: str,
        title: str,
        boardId: str,
        states: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Текстовые стикеры → создать новый текстовый стикер на доске.

        :param token: API-ключ
        :param title: название стикера
        :param boardId: ID доски
        :param states: список состояний стикера
        :return: информация о созданном текстовом стикере
        """
        self.logger.info(f"Создание нового текстового стикера '{title}' на доске {boardId}")
        return self._request(
            "POST",
            "/stringstickers",
            token=token,
            json={"title": title, "boardId": boardId, "states": states},
            error_msg=f"Ошибка при создании текстового стикера '{title}' на доске {boardId}"
        )

    def get_string_sticker(self, token: str, stickerId: str) -> Dict[str, Any]:
        """
        Текстовые стикеры → получить один текстовый стикер по его ID.

        :param token: API-ключ
        :param stickerId: ID текстового стикера
        :return: информация о текстовом стикере
        """
        self.logger.info(f"Получение информации о текстовом стикере {stickerId}")
        return self._request(
            "GET",
            f"/stringstickers/{stickerId}",
            token=token,
            error_msg=f"Ошибка при получении информации о текстовом стикере {stickerId}"
        )

    def change_string_sticker(
        self,
        token: str,
        stickerId: str,
        title: Optional[str] = None,
        states: Optional[List[Dict[str, Any]]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Текстовые стикеры → переименовать, изменить состояния или пометить на удаление.

        :param token: API-ключ
        :param stickerId: ID текстового стикера
        :param title: новое название стикера (опционально)
        :param states: новый список состояний стикера (опционально)
        :param delete: пометить стикер на удаление
        :return: обновленная информация о текстовом стикере
        """
        self.logger.info(f"Изменение текстового стикера {stickerId}")
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if states is not None:
            payload["states"] = states
        return self._request(
            "PUT",
            f"/stringstickers/{stickerId}",
            token=token,
            json=payload,
            error_msg=f"Ошибка при изменении текстового стикера {stickerId}"
        )

    def delete_string_sticker(self, token: str, stickerId: str) -> None:
        """
        Текстовые стикеры → физически удалить текстовый стикер.

        :param token: API-ключ
        :param stickerId: ID текстового стикера для удаления
        """
        self.logger.info(f"Удаление текстового стикера {stickerId}")
        self._request(
            "DELETE",
            f"/stringstickers/{stickerId}",
            token=token,
            error_msg=f"Ошибка при удалении текстового стикера {stickerId}"
        )

    # ===================================================================== #
    #                              15.  FILES                               #
    # ===================================================================== #

    def get_files(self, token: str, taskId: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Файлы → получить список файлов задачи.

        :param token: API-ключ
        :param taskId: ID задачи (опционально)
        :return: список файлов
        """
        self.logger.info(f"Получение списка файлов{' задачи ' + taskId if taskId else ''}")
        params = {"taskId": taskId} if taskId else None
        return self._request(
            "GET",
            "/files",
            token=token,
            params=params,
            error_msg=f"Ошибка при получении списка файлов{' задачи ' + taskId if taskId else ''}"
        )

    def get_file(self, token: str, fileId: str) -> Dict[str, Any]:
        """
        Файлы → получить один файл по его ID.

        :param token: API-ключ
        :param fileId: ID файла
        :return: информация о файле
        """
        self.logger.info(f"Получение информации о файле {fileId}")
        return self._request(
            "GET",
            f"/files/{fileId}",
            token=token,
            error_msg=f"Ошибка при получении информации о файле {fileId}"
        )

    def delete_file(self, token: str, fileId: str) -> None:
        """
        Файлы → удалить файл.

        :param token: API-ключ
        :param fileId: ID файла для удаления
        """
        self.logger.info(f"Удаление файла {fileId}")
        self._request(
            "DELETE",
            f"/files/{fileId}",
            token=token,
            error_msg=f"Ошибка при удалении файла {fileId}"
        )
