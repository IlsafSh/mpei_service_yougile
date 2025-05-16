"""
------------------------------------------------------------
Обёртка над REST API YouGile v2.0
------------------------------------------------------------
Документация API: https://ru.yougile.com/api-v2#/
------------------------------------------------------------
"""

from typing import Any, Dict, List, Optional
import requests


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

    def __init__(self, base_url: str = "https://ru.yougile.com/api-v2") -> None:
        """
        Инициализация клиента.
        :param base_url: базовый URL API (может пригодиться на тестовом стенде)
        """
        self.url = base_url.rstrip("/")

        # «кеш» для списковых запросов – для повторного использования
        self.companies: List[Dict[str, Any]] = []
        self.keys: List[Dict[str, Any]] = []
        self.users: List[Dict[str, Any]] = []
        self.projects: List[Dict[str, Any]] = []
        self.boards: List[Dict[str, Any]] = []
        self.columns: List[Dict[str, Any]] = []
        self.tasks: List[Dict[str, Any]] = []
        self.chat_subscribers: List[int] = []

    # ------------------------- ВНУТРЕННЯЯ КУХНЯ --------------------------- #

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        params: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Универсальный запрос к API.
        Добавляет заголовок Content-Type, Bearer-токен (если указан),
        бросает исключение, если код ответа ≠ 200.
        Возвращает «content», если YouGile заворачивает данные в обёртку.
        """
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        resp = requests.request(
            method,
            f"{self.url}{path}",
            headers=headers,
            params=params,
            json=json,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # Если прилетел dict c ключом 'content' – возвращаем его,
        # иначе отдаём «как есть» (это может быть list или dict без content).
        if isinstance(data, dict) and "content" in data:
            return data["content"]
        return data

    # ===================================================================== #
    #                               1.  AUTH                                #
    # ===================================================================== #

    def get_companies(self, login: str, password: str, name: str = "") -> List[Dict[str, Any]]:
        """
        Авторизация → получить список компаний, к которым доступен пользователь.
        """
        self.companies = self._request(
            "POST",
            "/auth/companies",
            json={"login": login, "password": password, "name": name},
        )
        return self.companies

    def get_keys(self, login: str, password: str, companyId: int) -> List[Dict[str, Any]]:
        """
        Авторизация → получить все сохранённые API-ключи для конкретной компании.
        """
        self.keys = self._request(
            "POST",
            "/auth/keys/get",
            json={"login": login, "password": password, "companyId": companyId},
        )
        return self.keys

    def create_key(self, login: str, password: str, companyId: int) -> Dict[str, Any]:
        """
        Авторизация → создать новый API-ключ (Bearer token).
        """
        return self._request(
            "POST",
            "/auth/keys",
            json={"login": login, "password": password, "companyId": companyId},
        )

    def delete_key(self, key: str) -> Dict[str, Any]:
        """
        Авторизация → удалить (отозвать) ключ по его значению.
        """
        return self._request("DELETE", f"/auth/keys/{key}")

    # ===================================================================== #
    #                               2.  USERS                               #
    # ===================================================================== #

    def get_users(self, token: str) -> List[Dict[str, Any]]:
        """
        Сотрудники → получить всех юзеров компании.
        """
        self.users = self._request("GET", "/users", token=token)
        return self.users

    def create_user(self, token: str, email: str, isAdmin: bool = False) -> Dict[str, Any]:
        """
        Сотрудники → пригласить нового пользователя по e-mail.
        """
        return self._request("POST", "/users", token=token, json={"email": email, "isAdmin": isAdmin})

    def get_user(self, token: str, userId: int) -> Dict[str, Any]:
        """Сотрудники → получить данные конкретного сотрудника по ID."""
        return self._request("GET", f"/users/{userId}", token=token)

    def change_user(self, token: str, userId: int, isAdmin: bool = False) -> Dict[str, Any]:
        """Сотрудники → изменить флаг администратора у пользователя."""
        return self._request("PUT", f"/users/{userId}", token=token, json={"isAdmin": isAdmin})

    def delete_user(self, token: str, userId: int) -> None:
        """Сотрудники → удалить сотрудника (безвозвратно)."""
        self._request("DELETE", f"/users/{userId}", token=token)

    # ===================================================================== #
    #                              3.  PROJECTS                             #
    # ===================================================================== #

    def get_projects(self, token: str) -> List[Dict[str, Any]]:
        """Проекты → получить список проектов компании."""
        self.projects = self._request("GET", "/projects", token=token)
        return self.projects

    def create_project(self, token: str, title: str, users: List[int]) -> Dict[str, Any]:
        """Проекты → создать новый проект с указанными участниками."""
        return self._request("POST", "/projects", token=token, json={"title": title, "users": users})

    def get_project(self, token: str, projectId: int) -> Dict[str, Any]:
        """Проекты → получить один проект по его ID."""
        return self._request("GET", f"/projects/{projectId}", token=token)

    def change_project(
        self,
        token: str,
        projectId: int,
        title: Optional[str] = None,
        users: Optional[List[int]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Проекты → переименовать, изменить состав участников или пометить на удаление.
        """
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if users is not None:
            payload["users"] = users
        return self._request("PUT", f"/projects/{projectId}", token=token, json=payload)

    def delete_project(self, token: str, projectId: int) -> None:
        """Проекты → физически удалить проект."""
        self._request("DELETE", f"/projects/{projectId}", token=token)

    # ===================================================================== #
    #                               4.  BOARDS                              #
    # ===================================================================== #

    def get_boards(self, token: str) -> List[Dict[str, Any]]:
        """Доски → получить список всех досок во всех проектах."""
        self.boards = self._request("GET", "/boards", token=token)
        return self.boards

    def create_board(
        self,
        token: str,
        title: str,
        projectId: int,
        stickers: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Доски → создать новую доску внутри проекта."""
        return self._request(
            "POST",
            "/boards",
            token=token,
            json={"title": title, "projectId": projectId, "stickers": stickers or {}},
        )

    def get_board(self, token: str, boardId: int) -> Dict[str, Any]:
        """Доски → получить одну доску по ID."""
        return self._request("GET", f"/boards/{boardId}", token=token)

    def change_board(
        self,
        token: str,
        boardId: int,
        title: Optional[str] = None,
        projectId: Optional[int] = None,
        stickers: Optional[Dict[str, Any]] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """Доски → изменить название, принадлежность или удалить доску."""
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if projectId is not None:
            payload["projectId"] = projectId
        if stickers is not None:
            payload["stickers"] = stickers
        return self._request("PUT", f"/boards/{boardId}", token=token, json=payload)

    def delete_board(self, token: str, boardId: int) -> None:
        """Доски → физически удалить доску."""
        self._request("DELETE", f"/boards/{boardId}", token=token)

    # ===================================================================== #
    #                              5.  COLUMNS                              #
    # ===================================================================== #

    def get_columns(self, token: str) -> List[Dict[str, Any]]:
        """Колонки → получить все колонки всех досок."""
        self.columns = self._request("GET", "/columns", token=token)
        return self.columns

    def create_column(self, token: str, title: str, color: str, boardId: int) -> Dict[str, Any]:
        """Колонки → создать новую колонку на доске."""
        return self._request(
            "POST",
            "/columns",
            token=token,
            json={"title": title, "color": color, "boardId": boardId},
        )

    def get_column(self, token: str, columnId: int) -> Dict[str, Any]:
        """Колонки → получить одну колонку по ID."""
        return self._request("GET", f"/columns/{columnId}", token=token)

    def change_column(
        self,
        token: str,
        columnId: int,
        title: Optional[str] = None,
        color: Optional[str] = None,
        boardId: Optional[int] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """Колонки → переименовать, сменить цвет или удалить колонку."""
        payload: Dict[str, Any] = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if color is not None:
            payload["color"] = color
        if boardId is not None:
            payload["boardId"] = boardId
        return self._request("PUT", f"/columns/{columnId}", token=token, json=payload)

    def delete_column(self, token: str, columnId: int) -> None:
        """Колонки → фізически удалить колонку."""
        self._request("DELETE", f"/columns/{columnId}", token=token)

    # ===================================================================== #
    #                               6.  TASKS                               #
    # ===================================================================== #

    def get_tasks(self, token: str) -> List[Dict[str, Any]]:
        """Задачи → получить список всех задач компании."""
        self.tasks = self._request("GET", "/task-list", token=token)
        return self.tasks

    def get_tasks_reverse(self, token: str) -> List[Dict[str, Any]]:
        """Задачи → получить список всех задач компании в обратном порядке."""
        self.tasks = self._request("GET", "/tasks", token=token)
        return self.tasks

    def create_task(
        self,
        token: str,
        *,
        title: str,
        columnId: int,
        subtasks: List[Dict[str, Any]] | None = None,
        assigned: List[int] | None = None,
        deadline: Optional[int] = None,
        timeTracking: Dict[str, Any] | None = None,
        checklists: List[Dict[str, Any]] | None = None,
        stickers: Dict[str, Any] | None = None,
        description: str = "",
        archived: bool = False,
        completed: bool = False,
    ) -> Dict[str, Any]:
        """
        Задачи → создать карточку с полной структурой (подзадачи, стикеры и т.д.).
        """
        payload = {
            "title": title,
            "columnId": columnId,
            "description": description,
            "archived": archived,
            "completed": completed,
            "subtasks": subtasks or [],
            "assigned": assigned or [],
            "deadline": deadline,
            "timeTracking": timeTracking or {},
            "checklists": checklists or [],
            "stickers": stickers or {},
        }
        return self._request("POST", "/tasks", token=token, json=payload)

    def get_task(self, token: str, taskId: int) -> Dict[str, Any]:
        """Задачи → получить одну задачу по её ID."""
        return self._request("GET", f"/tasks/{taskId}", token=token)

    def change_task(
        self,
        token: str,
        taskId: int,
        *,
        title: Optional[str] = None,
        columnId: Optional[int] = None,
        subtasks: Optional[List[Dict[str, Any]]] = None,
        assigned: Optional[List[int]] = None,
        deadline: Optional[int] = None,
        timeTracking: Optional[Dict[str, Any]] = None,
        checklists: Optional[List[Dict[str, Any]]] = None,
        stickers: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
        completed: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Задачи → изменить карточку. Передавайте только те поля, которые хотите
        поменять — остальные останутся прежними.
        """
        payload: Dict[str, Any] = {}
        for k, v in {
            "title": title,
            "columnId": columnId,
            "subtasks": subtasks,
            "assigned": assigned,
            "deadline": deadline,
            "timeTracking": timeTracking,
            "checklists": checklists,
            "stickers": stickers,
            "description": description,
            "archived": archived,
            "completed": completed,
        }.items():
            if v is not None:
                payload[k] = v
        return self._request("PUT", f"/tasks/{taskId}", token=token, json=payload)

    def delete_task(self, token: str, taskId: int) -> None:
        """Задачи → физически удалить карточку."""
        self._request("DELETE", f"/tasks/{taskId}", token=token)

    # ------------ подписчики чата задачи ---------------------------------- #

    def get_chat_subscribers(self, token: str, taskId: int) -> List[int]:
        """Задачи → получить ID пользователей, подписанных на чат карточки."""
        self.chat_subscribers = self._request("GET", f"/tasks/{taskId}/chat-subscribers", token=token)
        return self.chat_subscribers

    def change_chat_subscribers(self, token: str, taskId: int, subscribers: List[int]) -> Dict[str, Any]:
        """Задачи → заменить список подписчиков чата карточки."""
        return self._request(
            "PUT", f"/tasks/{taskId}/chat-subscribers", token=token, json={"content": subscribers}
        )

    # ===================================================================== #
    #                           7.  DEPARTMENTS                             #
    # ===================================================================== #

    def get_departments(self, token: str) -> List[Dict[str, Any]]:
        """Отделы → вернуть список отделов компании."""
        return self._request("GET", "/departments", token=token)

    def create_department(
        self,
        token: str,
        title: str,
        users: List[int] | None = None,
        color: str | None = None,
    ) -> Dict[str, Any]:
        """Отделы → создать новый отдел (можно сразу назначить участников)."""
        payload = {"title": title}
        if users is not None:
            payload["users"] = users
        if color is not None:
            payload["color"] = color
        return self._request("POST", "/departments", token=token, json=payload)

    def get_department(self, token: str, departmentId: int) -> Dict[str, Any]:
        """Отделы → получить один отдел по ID."""
        return self._request("GET", f"/departments/{departmentId}", token=token)

    def change_department(
        self,
        token: str,
        departmentId: int,
        *,
        title: Optional[str] = None,
        users: Optional[List[int]] = None,
        color: Optional[str] = None,
        delete: bool = False,
    ) -> Dict[str, Any]:
        """Отделы → переименовать, изменить состав или удалить отдел."""
        payload = {"deleted": delete}
        if title is not None:
            payload["title"] = title
        if users is not None:
            payload["users"] = users
        if color is not None:
            payload["color"] = color
        return self._request("PUT", f"/departments/{departmentId}", token=token, json=payload)

    def delete_department(self, token: str, departmentId: int) -> None:
        """Отделы → физически удалить отдел."""
        self._request("DELETE", f"/departments/{departmentId}", token=token)

    # ===================================================================== #
    #                         8.  PROJECT ROLES                             #
    # ===================================================================== #

    def get_project_roles(self, token: str) -> List[Dict[str, Any]]:
        """Роли проекта → получить справочник ролей."""
        return self._request("GET", "/project-roles", token=token)

    def create_project_role(self, token: str, title: str) -> Dict[str, Any]:
        """Роли проекта → добавить новую роль."""
        return self._request("POST", "/project-roles", token=token, json={"title": title})

    def change_project_role(self, token: str, roleId: int, title: str, delete: bool = False) -> Dict[str, Any]:
        """Роли проекта → переименовать или удалить роль (delete=True)."""
        return self._request(
            "PUT",
            f"/project-roles/{roleId}",
            token=token,
            json={"title": title, "deleted": delete},
        )

    def delete_project_role(self, token: str, roleId: int) -> None:
        """Роли проекта → физически удалить роль."""
        self._request("DELETE", f"/project-roles/{roleId}", token=token)

    # ===================================================================== #
    #                       9.  GROUP CHATS & MESSAGES                      #
    # ===================================================================== #

    def get_group_chats(self, token: str) -> List[Dict[str, Any]]:
        """Групповые чаты → список всех корпоративных чатов."""
        return self._request("GET", "/group-chats", token=token)

    def get_group_chat(self, token: str, chatId: int) -> Dict[str, Any]:
        """Групповые чаты → получить один чат по ID (мета-информация)."""
        return self._request("GET", f"/group-chats/{chatId}", token=token)

    def get_chat_messages(self, token: str, chatId: int) -> List[Dict[str, Any]]:
        """Групповые чаты → загрузить последние сообщения чата."""
        return self._request("GET", f"/group-chats/{chatId}/messages", token=token)

    def send_chat_message(self, token: str, chatId: int, text: str) -> Dict[str, Any]:
        """Групповые чаты → отправить сообщение в чат."""
        return self._request("POST", f"/group-chats/{chatId}/messages", token=token, json={"text": text})

    # ===================================================================== #
    #                        10.  EVENT SUBSCRIPTIONS                       #
    # ===================================================================== #

    def get_event_subscriptions(self, token: str, with_deleted: bool = False) -> List[Dict[str, Any]]:
        """Веб-хуки → получить все подписки на события (webhook)."""
        params = {"deleted": "true"} if with_deleted else None
        return self._request("GET", "/event-subs", token=token, params=params)

    def create_event_subscription(self, token: str, url: str, event: str) -> Dict[str, Any]:
        """Веб-хуки → создать подписку на конкретное событие."""
        return self._request("POST", "/event-subs", token=token, json={"url": url, "event": event})

    def change_event_subscription(
        self, token: str, subId: int, url: Optional[str] = None, delete: bool = False
    ) -> Dict[str, Any]:
        """Веб-хуки → изменить URL или удалить подписку."""
        payload: Dict[str, Any] = {"deleted": delete}
        if url is not None:
            payload["url"] = url
        return self._request("PUT", f"/event-subs/{subId}", token=token, json=payload)

    def delete_event_subscription(self, token: str, subId: int) -> None:
        """Веб-хуки → физически удалить подписку на событие."""
        self._request("DELETE", f"/event-subs/{subId}", token=token)

    # ===================================================================== #
    #                             11.  STICKERS                            #
    # ===================================================================== #

    # Generic-методы — позволяют не дублировать код для разных типов стикеров
    def _generic_sticker(
        self,
        token: str,
        sticker_type: str,
        *,
        method: str,
        stickerId: int | None = None,
        payload: dict | None = None,
    ):
        """
        Внутренняя универсальная обёртка для CRUD-операций над стикерами.
        :param sticker_type: тип коллекции, например 'text-stickers'
        :param method: HTTP-метод ('GET', 'POST', …)
        """
        path = f"/{sticker_type}" + (f"/{stickerId}" if stickerId else "")
        return self._request(method, path, token=token, json=payload)

    # ------------------------- Text-stickers ----------------------------- #

    def get_text_stickers(self, token: str):
        """Стикеры-тексты → получить справочник пользовательских ярлыков."""
        return self._generic_sticker(token, "text-stickers", method="GET")

    def create_text_sticker(self, token: str, text: str, color: str):
        """Стикеры-тексты → создать новый текстовый стикер."""
        return self._generic_sticker(
            token,
            "text-stickers",
            method="POST",
            payload={"text": text, "color": color},
        )

    # -------------- Аналогичные эндпоинты для статусов/спринтов ----------- #

    def get_status_text_stickers(self, token: str):
        """Стикеры-статусы (текст) → получить список."""
        return self._generic_sticker(token, "status-text-stickers", method="GET")

    def get_sprint_stickers(self, token: str):
        """Стикеры спринта → получить список."""
        return self._generic_sticker(token, "sprint-sticker", method="GET")

    def get_status_sprint_stickers(self, token: str):
        """Стикеры-статусы (спринт) → получить список."""
        return self._generic_sticker(token, "status-sprint-sticker", method="GET")
