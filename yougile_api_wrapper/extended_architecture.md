# Проектирование расширенной обертки для YouGile API

## Архитектурные принципы
1. **Модульность** - каждый ресурс API выделен в отдельный модуль
2. **Единообразие интерфейсов** - все ресурсы следуют одинаковым паттернам
3. **Типизация** - использование Pydantic для валидации данных
4. **Расширяемость** - возможность легко добавлять новые ресурсы и методы
5. **Документированность** - подробные docstrings для всех классов и методов

## Структура проекта

```
yougile_api/
├── yougile_api/
│   ├── __init__.py
│   ├── client.py              # Основной клиент API
│   ├── exceptions.py          # Исключения
│   ├── models/                # Модели данных
│   │   ├── __init__.py
│   │   ├── auth.py            # Модели аутентификации
│   │   ├── board.py           # Модели досок
│   │   ├── chat_message.py    # Модели сообщений чата
│   │   ├── column.py          # Модели колонок
│   │   ├── department.py      # Модели отделов
│   │   ├── employee.py        # Модели сотрудников
│   │   ├── group_chat.py      # Модели групповых чатов
│   │   ├── project.py         # Модели проектов
│   │   ├── project_role.py    # Модели ролей проекта
│   │   ├── sprint_sticker.py  # Модели стикеров спринта
│   │   ├── string_sticker.py  # Модели строковых стикеров
│   │   ├── task.py            # Модели задач
│   │   └── webhook.py         # Модели вебхуков
│   └── resources/             # Ресурсные классы для работы с API
│       ├── __init__.py
│       ├── auth.py            # Ресурс аутентификации
│       ├── boards.py          # Ресурс досок
│       ├── chat_messages.py   # Ресурс сообщений чата
│       ├── columns.py         # Ресурс колонок
│       ├── departments.py     # Ресурс отделов
│       ├── employees.py       # Ресурс сотрудников
│       ├── group_chats.py     # Ресурс групповых чатов
│       ├── projects.py        # Ресурс проектов
│       ├── project_roles.py   # Ресурс ролей проекта
│       ├── sprint_stickers.py # Ресурс стикеров спринта
│       ├── string_stickers.py # Ресурс строковых стикеров
│       ├── tasks.py           # Ресурс задач
│       └── webhooks.py        # Ресурс вебхуков
└── example.py                 # Пример использования
```

## Базовые интерфейсы

### Базовый ресурсный класс
```python
class BaseResource:
    """Базовый класс для всех ресурсов API."""
    
    def __init__(self, client):
        """
        Инициализация ресурса.
        
        Args:
            client: Экземпляр клиента API
        """
        self._client = client
```

### Интерфейсы для ресурсов

#### Интерфейс для ресурсов с CRUD операциями
```python
class CRUDResourceMixin:
    """Миксин для ресурсов с CRUD операциями."""
    
    def list(self, **params):
        """
        Получить список объектов.
        
        Args:
            **params: Параметры запроса
            
        Returns:
            list: Список объектов
        """
        pass
        
    def create(self, **data):
        """
        Создать новый объект.
        
        Args:
            **data: Данные для создания объекта
            
        Returns:
            object: Созданный объект
        """
        pass
        
    def get(self, id, **params):
        """
        Получить объект по ID.
        
        Args:
            id: Идентификатор объекта
            **params: Дополнительные параметры запроса
            
        Returns:
            object: Объект
        """
        pass
        
    def update(self, id, **data):
        """
        Обновить объект.
        
        Args:
            id: Идентификатор объекта
            **data: Данные для обновления
            
        Returns:
            object: Обновленный объект
        """
        pass
        
    def delete(self, id):
        """
        Удалить объект.
        
        Args:
            id: Идентификатор объекта
            
        Returns:
            bool: Результат операции
        """
        pass
```

#### Интерфейс для вложенных ресурсов
```python
class NestedResourceMixin:
    """Миксин для вложенных ресурсов."""
    
    def list(self, parent_id, **params):
        """
        Получить список вложенных объектов.
        
        Args:
            parent_id: Идентификатор родительского объекта
            **params: Параметры запроса
            
        Returns:
            list: Список объектов
        """
        pass
        
    def create(self, parent_id, **data):
        """
        Создать новый вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            **data: Данные для создания объекта
            
        Returns:
            object: Созданный объект
        """
        pass
        
    def get(self, parent_id, id, **params):
        """
        Получить вложенный объект по ID.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            **params: Дополнительные параметры запроса
            
        Returns:
            object: Объект
        """
        pass
        
    def update(self, parent_id, id, **data):
        """
        Обновить вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            **data: Данные для обновления
            
        Returns:
            object: Обновленный объект
        """
        pass
        
    def delete(self, parent_id, id):
        """
        Удалить вложенный объект.
        
        Args:
            parent_id: Идентификатор родительского объекта
            id: Идентификатор объекта
            
        Returns:
            bool: Результат операции
        """
        pass
```

## Проектирование ресурсных классов

### 1. Аутентификация (AuthResource)
```python
class AuthResource(BaseResource):
    """Ресурс для работы с аутентификацией."""
    
    def get_companies(self, login, password, **params):
        """Получить список компаний."""
        pass
        
    def get_keys(self, login, password, company_id):
        """Получить список ключей."""
        pass
        
    def create_key(self, login, password, company_id):
        """Создать ключ."""
        pass
        
    def delete_key(self, key):
        """Удалить ключ."""
        pass
```

### 2. Доски (BoardsResource)
```python
class BoardsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с досками."""
    
    def list(self, **params):
        """Получить список досок."""
        pass
        
    def create(self, title, project_id, stickers=None, **data):
        """Создать доску."""
        pass
        
    def get(self, id):
        """Получить доску по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить доску."""
        pass
```

### 3. Сообщения чата (ChatMessagesResource)
```python
class ChatMessagesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с сообщениями чата."""
    
    def list(self, chat_id, **params):
        """Получить историю сообщений."""
        pass
        
    def create(self, chat_id, text, text_html, label):
        """Написать в чат."""
        pass
        
    def get(self, chat_id, id):
        """Получить сообщение по ID."""
        pass
        
    def update(self, chat_id, id, **data):
        """Изменить сообщение."""
        pass
```

### 4. Колонки (ColumnsResource)
```python
class ColumnsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с колонками."""
    
    def list(self, **params):
        """Получить список колонок."""
        pass
        
    def create(self, title, board_id, color=None):
        """Создать колонку."""
        pass
        
    def get(self, id):
        """Получить колонку по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить колонку."""
        pass
```

### 5. Отделы (DepartmentsResource)
```python
class DepartmentsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с отделами."""
    
    def list(self, **params):
        """Получить список отделов."""
        pass
        
    def create(self, title=None, parent_id=None, users=None):
        """Создать отдел."""
        pass
        
    def get(self, id):
        """Получить отдел по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить отдел."""
        pass
```

### 6. Сотрудники (EmployeesResource)
```python
class EmployeesResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с сотрудниками."""
    
    def list(self, **params):
        """Получить список сотрудников."""
        pass
        
    def create(self, email, is_admin=None):
        """Пригласить сотрудника в компанию."""
        pass
        
    def get(self, id):
        """Получить сотрудника по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить сотрудника."""
        pass
        
    def delete(self, id):
        """Удалить сотрудника из компании."""
        pass
```

### 7. Групповые чаты (GroupChatsResource)
```python
class GroupChatsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с групповыми чатами."""
    
    def list(self, **params):
        """Получить список чатов."""
        pass
        
    def create(self, title, users):
        """Создать чат."""
        pass
        
    def get(self, id):
        """Получить чат по ID."""
        pass
        
    def update(self, id, deleted, title, users):
        """Обновить чат."""
        pass
```

### 8. Роли проекта (ProjectRolesResource)
```python
class ProjectRolesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с ролями проекта."""
    
    def list(self, project_id, **params):
        """Получить список ролей."""
        pass
        
    def create(self, project_id, name, permissions, description=None):
        """Создать роль."""
        pass
        
    def get(self, project_id, id):
        """Получить роль по ID."""
        pass
        
    def update(self, project_id, id, **data):
        """Обновить роль."""
        pass
        
    def delete(self, project_id, id):
        """Удалить роль."""
        pass
```

### 9. Проекты (ProjectsResource)
```python
class ProjectsResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с проектами."""
    
    def list(self, **params):
        """Получить список проектов."""
        pass
        
    def create(self, title, users=None):
        """Создать проект."""
        pass
        
    def get(self, id):
        """Получить проект по ID."""
        pass
        
    def update(self, id, title, **data):
        """Обновить проект."""
        pass
```

### 10. Стикеры спринта (SprintStickersResource)
```python
class SprintStickersResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы со стикерами спринта."""
    
    def list(self, **params):
        """Получить список стикеров."""
        pass
        
    def create(self, name, states):
        """Создать стикер."""
        pass
        
    def get(self, id):
        """Получить стикер по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить стикер."""
        pass
```

### 11. Состояния стикеров спринта (SprintStickerStatesResource)
```python
class SprintStickerStatesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с состояниями стикеров спринта."""
    
    def get(self, sticker_id, state_id, **params):
        """Получить состояние по ID."""
        pass
        
    def update(self, sticker_id, state_id, **data):
        """Обновить состояние."""
        pass
        
    def create(self, sticker_id, name, begin=None, end=None):
        """Создать состояние."""
        pass
```

### 12. Строковые стикеры (StringStickersResource)
```python
class StringStickersResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы со строковыми стикерами."""
    
    def list(self, **params):
        """Получить список стикеров."""
        pass
        
    def create(self, name, states, icon=None):
        """Создать стикер."""
        pass
        
    def get(self, id):
        """Получить стикер по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить стикер."""
        pass
```

### 13. Состояния строковых стикеров (StringStickerStatesResource)
```python
class StringStickerStatesResource(BaseResource, NestedResourceMixin):
    """Ресурс для работы с состояниями строковых стикеров."""
    
    def get(self, sticker_id, state_id, **params):
        """Получить состояние по ID."""
        pass
        
    def update(self, sticker_id, state_id, **data):
        """Обновить состояние."""
        pass
        
    def create(self, sticker_id, name, color=None):
        """Создать состояние."""
        pass
```

### 14. Задачи (TasksResource)
```python
class TasksResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с задачами."""
    
    def list(self, **params):
        """Получить список задач."""
        pass
        
    def create(self, title, **data):
        """Создать задачу."""
        pass
        
    def get(self, id):
        """Получить задачу по ID."""
        pass
        
    def update(self, id, **data):
        """Обновить задачу."""
        pass
```

### 15. Вебхуки (WebhooksResource)
```python
class WebhooksResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с вебхуками."""
    
    def list(self, **params):
        """Получить список подписок."""
        pass
        
    def create(self, url, event):
        """Создать подписку."""
        pass
        
    def update(self, id, **data):
        """Обновить подписку."""
        pass
```

## Интеграция ресурсов в клиент API

```python
class YouGileClient:
    """Клиент для работы с YouGile API."""
    
    def __init__(self, token=None):
        """
        Инициализация клиента.
        
        Args:
            token: Токен для аутентификации
        """
        self.token = token
        
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
```
