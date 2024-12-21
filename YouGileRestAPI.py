import requests

class YouGileRestAPI:
    def __init__(self):
        """
        Инициализация
        """
        self.url = "https://ru.yougile.com/api-v2"
        self.companies = []
        self.keys = []
        self.projects = []
        self.boards = []
        self.columns = []
        self.tasks = []
        self.chat_subscribers = []


    def get_companies(self, login, password, name=""):
        """
        Авторизация. Получить список компаний
        """
        payload = {
            "login": login,
            "password": password,
            "name": name
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", f"{self.url}/auth/companies", json=payload, headers=headers)
        self.companies = response.json().get("content", [])     # [{'id': , 'name': , 'isAdmin': }]
        return self.companies

    def get_keys(self, login, password, companyId):
        """
        Авторизация. Получить список ключей авторизации
        """
        payload = {
            "login": login,
            "password": password,
            "companyId": companyId
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", f"{self.url}/auth/keys/get", json=payload, headers=headers)
        self.keys = response.json()      # [{'key': , 'timestamp': , 'companyId': }]
        return self.keys

    def create_key(self, login, password, companyId):
        """
        Авторизация. Создать ключ авторизации
        """
        payload = {
            "login": login,
            "password": password,
            "companyId": companyId
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", f"{self.url}/auth/keys", json=payload, headers=headers)
        return response.json()

    def delete_key(self, key=""):
        """
        Авторизация. Удалить ключ авторизации
        """
        headers = {"Content-Type": "application/json"}

        response = requests.request("DELETE", f"{self.url}/auth/keys/{key}", headers=headers)
        return response.json()


    def get_users(self, token):
        """
        Сотрудники. Получить список сотрудников
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/users", headers=headers)
        self.projects = response.json().get("content", [])     # [{'title': , 'timestamp': , 'users': {}, 'id': }, ...]
        return self.projects

    def create_user(self, token, email, isAdmin=False):
        """
        Сотрудники. Пригласить в компанию
        """
        payload = {
            "email": email,
            "isAdmin": isAdmin
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("POST", f"{self.url}/users", json=payload, headers=headers)
        return response.json()

    def get_user(self, token, userId):
        """
        Сотрудники. Получить сотрудника по ID
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/users/{userId}", headers=headers)
        return response.json()

    def change_user(self, token, userId, isAdmin=False):
        """
        Сотрудники. Изменить сотрудника по ID
        """
        payload = {"isAdmin": isAdmin}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("PUT", f"{self.url}/users/{userId}", json=payload, headers=headers)
        return response.json()

    def delete_user(self, token, userId):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("DELETE", f"{self.url}/users/{userId}", headers=headers)


    def get_projects(self, token):
        """
        Проекты. Получить список проектов
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/projects", headers=headers)
        self.projects = response.json().get("content", [])     # [{'title': , 'timestamp': , 'users': {}, 'id': }, ...]
        return self.projects

    def create_project(self, token, title, users):
        """
        Проекты. Создать проект
        """
        payload = {
            "title": title,
            "users": users
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("POST", f"{self.url}/projects", json=payload, headers=headers)
        return response.json()

    def get_project(self, token, projectId):
        """
        Проекты. Получить проект по ID
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/projects/{projectId}", headers=headers)
        return response.json()

    def change_project(self, token, projectId, title, users, delete=False):
        """
        Проекты. Изменить проект по ID
        """
        payload = {
            "deleted": delete,
            "title": title,
            "users": users
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("PUT", f"{self.url}/projects/{projectId}", json=payload, headers=headers)
        return response.json()


    def get_boards(self, token):
        """
        Доски. Получить список досок
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/boards", headers=headers)
        self.boards = response.json().get("content", [])     # [{'title': , 'projectId': , 'stickers': {'deadline': ,
        # 'stopwatch': , 'assignee': , 'custom': {}}, 'id': }, ...]
        return self.boards

    def create_board(self, token, title, projectId, stickers):
        """
        Доски. Создать доску
        """
        payload = {
            "title": title,
            "projectId": projectId,
            "stickers": stickers
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("POST", f"{self.url}/boards", json=payload, headers=headers)
        return response.json()

    def get_board(self, token, boardId):
        """
        Доски. Получить доску по ID
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/boards/{boardId}", headers=headers)
        return response.json()

    def change_board(self, token, boardId, title, projectId, stickers, delete=False):
        """
        Доски. Изменить доску по ID
        """
        payload = {
            "deleted": delete,
            "title": title,
            "projectId": projectId,
            "stickers": stickers
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("PUT", f"{self.url}/boards/{boardId}", json=payload, headers=headers)
        return response.json()


    def get_columns(self, token):
        """
        Колонки. Получить список колонок
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/columns", headers=headers)
        self.columns = response.json().get("content", [])     # [{'title': , 'color': , 'boardId': , 'id': }, ...]
        return self.columns

    def create_column(self, token, title, color, boardId):
        """
        Колонки. Создать колонку
        """
        payload = {
            "title": title,
            "color": color,
            "boardId": boardId
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("POST", f"{self.url}/columns", json=payload, headers=headers)
        return response.json()

    def get_column(self, token, columnId):
        """
        Колонки. Получить колонку по ID
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/columns/{columnId}", headers=headers)
        return response.json()

    def change_column(self, token, columnId, title, color, boardId, delete=False):
        """
        Колонки. Изменить колонку по ID
        """
        payload = {
            "deleted": delete,
            "title": title,
            "color": color,
            "boardId": boardId
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("PUT", f"{self.url}/columns/{columnId}", json=payload, headers=headers)
        return response.json()


    def get_tasks(self, token):
        """
        Задачи. Получить список задач
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/tasks", headers=headers)
        self.tasks = response.json().get("content", [])     # [{'title': , 'timestamp': , 'columnId': , 'archived': ,
        # 'completed': , 'completedTimestamp': . 'subtasks': [], 'assigned': , 'createdBy': , 'id': }, ...]
        return self.tasks

    def create_task(self, token, title, columnId, subtasks, assigned, deadline, timeTracking, checklists, stickers,
                    description="", archived=False, completed=False):
        """
        Задачи. Создать задачу
        """
        payload = {
            "title": title,
            "columnId": columnId,
            "description": description,
            "archived": archived,
            "completed": completed,
            "subtasks": subtasks,
            "assigned": assigned,
            "deadline": deadline,
            "timeTracking": timeTracking,
            "checklists": checklists,
            "stickers": stickers
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("POST", f"{self.url}/tasks", json=payload, headers=headers)
        return response.json()

    def get_task(self, token, taskId):
        """
        Задачи. Получить задачу по ID
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("GET", f"{self.url}/tasks/{taskId}", headers=headers)
        return response.json()

    def change_task(self, token, taskId, title, columnId, subtasks, assigned, deadline, timeTracking, checklists, stickers,
                    description="", archived=False, completed=False):
        """
        Задачи. Изменить задачу по ID
        """
        payload = {
            "title": title,
            "columnId": columnId,
            "description": description,
            "archived": archived,
            "completed": completed,
            "subtasks": subtasks,
            "assigned": assigned,
            "deadline": deadline,
            "timeTracking": timeTracking,
            "checklists": checklists,
            "stickers": stickers
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.request("PUT", f"{self.url}/tasks/{taskId}", json=payload, headers=headers)
        return response.json()

    # def get_chat_subscribers(self, token, taskId):
    #     """
    #     Задачи. Получить список участников чата задачи
    #     """
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {token}"
    #     }
    #
    #     response = requests.request("GET", f"{self.url}/tasks/{taskId}/chat-subscribers", headers=headers)
    #     self.chat_subscribers = response.json()
    #     return self.chat_subscribers
    #
    # def change_chat_subscribers(self, token, taskId, content):
    #     """
    #     Задачи. Изменить список участников чата задачи
    #     """
    #     payload = {"content": content}
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {token}"
    #     }
    #
    #     response = requests.request("PUT", f"{self.url}/tasks/{taskId}/chat-subscribers", json=payload, headers=headers)
    #     return response.json()