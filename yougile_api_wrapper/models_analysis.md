# Анализ моделей и эндпоинтов YouGile API

## Перечень файлов моделей
1. auth.py - Аутентификация
2. boards.py - Доски
3. chatmessages.py - Сообщения чата
4. columns.py - Колонки
5. departments.py - Отделы
6. employees.py - Сотрудники
7. groupchats.py - Групповые чаты
8. projectroles.py - Роли проекта
9. projects.py - Проекты
10. sprintsticker.py - Стикеры спринта
11. sprintstickerstate.py - Состояния стикеров спринта
12. stringsticker.py - Строковые стикеры
13. stringstickerstate.py - Состояния строковых стикеров
14. tasks.py - Задачи
15. webhooks.py - Вебхуки

## Детальный анализ моделей и эндпоинтов

### 1. Аутентификация (auth.py)
- **AuthKeyController_companiesList** - POST /api-v2/auth/companies - Получить список компаний
- **AuthKeyController_search** - POST /api-v2/auth/keys/get - Получить список ключей
- **AuthKeyController_create** - POST /api-v2/auth/keys - Создать ключ
- **AuthKeyController_delete** - DELETE /api-v2/auth/keys/{key} - Удалить ключ

### 2. Доски (boards.py)
- **BoardController_search** - GET /api-v2/boards - Получить список
- **BoardController_create** - POST /api-v2/boards - Создать
- **BoardController_get** - GET /api-v2/boards/{id} - Получить по ID
- **BoardController_update** - PUT /api-v2/boards/{id} - Изменить

### 3. Сообщения чата (chatmessages.py)
- **ChatMessageController_search** - GET /api-v2/chats/{chatId}/messages - Получить историю сообщений
- **ChatMessageController_sendMessage** - POST /api-v2/chats/{chatId}/messages - Написать в чат
- **ChatMessageController_get** - GET /api-v2/chats/{chatId}/messages/{id} - Получить сообщение по ID
- **ChatMessageController_update** - PUT /api-v2/chats/{chatId}/messages/{id} - Изменить сообщение

### 4. Колонки (columns.py)
- **ColumnController_search** - GET /api-v2/columns - Получить список
- **ColumnController_create** - POST /api-v2/columns - Создать
- **ColumnController_get** - GET /api-v2/columns/{id} - Получить по ID
- **ColumnController_update** - PUT /api-v2/columns/{id} - Изменить

### 5. Отделы (departments.py)
- **DepartmentController_search** - GET /api-v2/departments - Получить список
- **DepartmentController_create** - POST /api-v2/departments - Создать
- **DepartmentController_get** - GET /api-v2/departments/{id} - Получить по ID
- **DepartmentController_update** - PUT /api-v2/departments/{id} - Изменить

### 6. Сотрудники (employees.py)
- **UserController_search** - GET /api-v2/users - Получить список
- **UserController_create** - POST /api-v2/users - Пригласить в компанию
- **UserController_get** - GET /api-v2/users/{id} - Получить по ID
- **UserController_update** - PUT /api-v2/users/{id} - Изменить
- **UserController_delete** - DELETE /api-v2/users/{id} - Удалить из компании

### 7. Групповые чаты (groupchats.py)
- **GroupChatController_search** - GET /api-v2/group-chats - Получить список чатов
- **GroupChatController_create** - POST /api-v2/group-chats - Создать чат
- **GroupChatController_get** - GET /api-v2/group-chats/{id} - Получить по ID
- **BoardController_update** - PUT /api-v2/group-chats/{id} - Изменить (ошибка в имени класса, должно быть GroupChatController_update)

### 8. Роли проекта (projectroles.py)
- **ProjectRolesController_search** - GET /api-v2/projects/{projectId}/roles - Получить список
- **ProjectRolesController_create** - POST /api-v2/projects/{projectId}/roles - Создать
- **ProjectRolesController_get** - GET /api-v2/projects/{projectId}/roles/{id} - Получить по ID
- **ProjectRolesController_update** - PUT /api-v2/projects/{projectId}/roles/{id} - Изменить
- **ProjectRolesController_delete** - DELETE /api-v2/projects/{projectId}/roles/{id} - Удалить

### 9. Проекты (projects.py)
- **ProjectController_search** - GET /api-v2/projects - Получить список
- **ProjectController_create** - POST /api-v2/projects - Создать
- **ProjectController_get** - GET /api-v2/projects/{id} - Получить по ID
- **ProjectController_update** - PUT /api-v2/projects/{id} - Изменить

### 10. Стикеры спринта (sprintsticker.py)
- **SprintStickerController_search** - GET /api-v2/sprint-stickers - Получить список
- **SprintStickerController_create** - POST /api-v2/sprint-stickers - Создать
- **SprintStickerController_getSticker** - GET /api-v2/sprint-stickers/{id} - Получить по ID
- **SprintStickerController_update** - PUT /api-v2/sprint-stickers/{id} - Изменить

### 11. Состояния стикеров спринта (sprintstickerstate.py)
- **SprintStickerStateController_get** - GET /api-v2/sprint-stickers/{stickerId}/states/{stickerStateId} - Получить по ID
- **SprintStickerStateController_update** - PUT /api-v2/sprint-stickers/{stickerId}/states/{stickerStateId} - Изменить
- **SprintStickerStateController_create** - POST /api-v2/sprint-stickers/{stickerId}/states - Создать

### 12. Строковые стикеры (stringsticker.py)
- **StringStickerController_search** - GET /api-v2/string-stickers - Получить список
- **StringStickerController_create** - POST /api-v2/string-stickers - Создать
- **StringStickerController_get** - GET /api-v2/string-stickers/{id} - Получить по ID
- **StringStickerController_update** - PUT /api-v2/string-stickers/{id} - Изменить

### 13. Состояния строковых стикеров (stringstickerstate.py)
- **StringStickerStateController_get** - GET /api-v2/string-stickers/{stickerId}/states/{stickerStateId} - Получить по ID
- **StringStickerStateController_update** - PUT /api-v2/string-stickers/{stickerId}/states/{stickerStateId} - Изменить
- **StringStickerStateController_create** - POST /api-v2/string-stickers/{stickerId}/states - Создать

### 14. Задачи (tasks.py)
- **TaskController_search** - GET /api-v2/tasks - Получить список
- **TaskController_create** - POST /api-v2/tasks - Создать
- **TaskController_get** - GET /api-v2/tasks/{id} - Получить по ID
- **TaskController_update** - PUT /api-v2/tasks/{id} - Изменить

### 15. Вебхуки (webhooks.py)
- **WebhookController_create** - POST /api-v2/webhooks - Создать подписку
- **WebhookController_search** - GET /api-v2/webhooks - Получить список подписок
- **WebhookController_put** - PUT /api-v2/webhooks/{id} - Изменить подписку
