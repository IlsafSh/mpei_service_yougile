"""
Пример использования YouGile API клиента.

Этот файл содержит примеры использования всех ресурсов и методов API.
Примечание: Для выполнения всех запросов (кроме авторизации)_ требуется действующий токен авторизации.
"""

from yougile_api import YouGileClient


def auth_examples(client):
    """Примеры работы с аутентификацией."""
    print("\n=== Примеры аутентификации ===")

    login = "parov.duvel@mail.ru"
    password = "pavel123"

    # Пример аутентификации
    companies_response = client.auth.get_companies(login=login, password=password)  # Получение списка компаний
    print(f"Companies Response: {companies_response}")

    if companies_response and 'content' in companies_response:
        companies = companies_response['content']
        print(f"List of companies: {companies}")
        if companies:
            id_company = companies[0].get('id')  # ID компании
            keys_response = client.auth.get_keys(login, password, id_company)  # Получение списка ключей
            print(f"List of keys: {keys_response}")

            if keys_response:
                token = keys_response[0].get('key')  # Берём первый ключ авторизации
            else:
                # Создаем ключ авторизации
                new_key = client.auth.create_key(login=login, password=password, company_id=id_company)
                print(f"Created new key: {new_key}")
                keys_response = client.auth.get_keys(login, password, id_company)
                if keys_response and 'content' in keys_response and keys_response['content']:
                    token = keys_response['content'][0].get('key')
                else:
                    token = None
                    print("Не удалось получить токен")

            if token:
                print(f"Authorization token: {token}")

                # Установка токена для дальнейших запросов
                client.set_token(token)

                # Пример удаления ключа
                # result = client.auth.delete_key(token)
                # print(f"Key deletion result: {result}")


def employees_examples(client):
    """Примеры работы с сотрудниками."""
    print("\n=== Примеры работы с сотрудниками ===")

    # Получение списка сотрудников
    try:
        employees_response = client.employees.list(limit=10)
        print(f"Employees Response: {employees_response}")

        if 'content' in employees_response:
            employees = employees_response['content']
        else:
            employees = []

        print(f"Получено сотрудников: {len(employees)}")

        # Вывод информации о сотрудниках
        for employee in employees:
            print(f"Сотрудник: {employee.get('email')} (ID: {employee.get('id')})")

        # Если есть сотрудники, используем первого для примеров
        if employees:
            employee_id = employees[0]['id']

            # Получение сотрудника по ID
            employee = client.employees.get(employee_id)
            print(f"\nПолучен сотрудник: {employee.get('email')}")

    except Exception as e:
        print(f"Ошибка при работе с сотрудниками: {e}")

    # Создание нового сотрудника
    try:
        new_employee = client.employees.create(
            email="new.employee@example.com"
        )
        print(f"Создан новый сотрудник: {new_employee}")

    except Exception as e:
        print(f"Ошибка при создании сотрудника: {e}")

    # Обновление сотрудника
    try:
        updated_employee = client.employees.update(
            id=new_employee.get('id'),
            is_admin=False
        )
        print(f"Сотрудник обновлен: {updated_employee}")

    except Exception as e:
        print(f"Ошибка при создании сотрудника: {e}")

    # Удаление сотрудника
    try:
        deleted_employee = client.employees.delete(new_employee.get('id'))
        print(f"Сотрудник удален: {deleted_employee}")

    except Exception as e:
        print(f"Ошибка при создании сотрудника: {e}")


def projects_examples(client):
    """Примеры работы с проектами."""
    print("\n=== Примеры работы с проектами ===")

    # Получение списка проектов
    try:
        projects_response = client.projects.list(limit=10)
        print(f"Projects Response: {projects_response}")

        if 'content' in projects_response:
            projects = projects_response['content']
        else:
            projects = []

        print(f"Получено проектов: {len(projects)}")

        # Вывод информации о проектах
        for project in projects:
            print(f"Проект: {project.get('title')} (ID: {project.get('id')})")

        # Если есть проекты, используем первый для примеров
        if projects:
            project_id = projects[0]['id']

            # Получение проекта по ID
            project = client.projects.get(project_id)
            print(f"\nПолучен проект: {project.get('title')}")

    except Exception as e:
        print(f"Ошибка при работе с проектами: {e}")

    # Создание нового проекта
    try:
        new_project = client.projects.create(
            title="Новый тестовый проект",
            users={"807972fa-dcf1-4d52-a9a3-9b9c8ef0100d": "admin"}
        )
        print(f"Создан новый проект: {new_project})")

        # Обновление проекта
        updated_project = client.projects.update(
            id=new_project.get('id'),
            title="Обновленный проект"
        )
        print(f"Проект обновлен: {updated_project}")

        # Удаление проекта
        deleted_project = client.projects.update(
            id=new_project.get('id'),
            title=new_project.get('title'),
            deleted=True
        )
        print(f"Проект удален: {deleted_project}")
    except Exception as e:
        print(f"Ошибка при создании проекта: {e}")


def project_roles_examples(client):
    """Примеры работы с ролями проекта."""
    print("\n=== Примеры работы с ролями проекта ===")

    # Получение списка ролей проекта
    try:
        # Для получения ролей нужен ID проекта
        projects_response = client.projects.list(limit=1)
        print(f"Projects Response: {projects_response}")

        projects = []
        if 'content' in projects_response:
            projects = projects_response['content']

        if projects:
            project_id = projects[0]['id']

            roles_response = client.project_roles.list(project_id=project_id, limit=10)
            print(f"Roles Response: {roles_response}")
            if 'content' in roles_response:
                roles = roles_response['content']
            else:
                roles = []

            print(f"Получено ролей: {len(roles)}")

            # Вывод информации о ролях
            for role in roles:
                print(f"Роль: {role.get('name')} (ID: {role.get('id')})")

            # Если есть роли, используем первую для примеров
            if roles:
                role_id = roles[0]['id']

                # Получение роли по ID
                role = client.project_roles.get(parent_id=project_id, id=role_id)
                print(f"\nПолучена роль: {role.get('name')}")
        else:
            print("Нет доступных проектов для получения ролей")

    except Exception as e:
        print(f"Ошибка при работе с ролями проекта: {e}")

    try:
        # Создание новой роли
        permissions = {
        "editTitle": True,
        "delete": True,
        "addBoard": True,
        "boards": {
            "editTitle": True,
            "delete": True,
            "move": True,
            "showStickers": True,
            "editStickers": True,
            "addColumn": True,
            "columns": {
                "editTitle": True,
                "delete": True,
                "move": "no",
                "addTask": True,
                "allTasks": {
                    "show": True,
                    "delete": True,
                    "editTitle": True,
                    "editDescription": True,
                    "complete": True,
                    "close": True,
                    "assignUsers": "no",
                    "connect": True,
                    "editSubtasks": "no",
                    "editStickers": True,
                    "editPins": True,
                    "move": "no",
                    "sendMessages": True,
                    "sendFiles": True,
                    "editWhoToNotify": "no"
                },
                "withMeTasks": {
                    "show": True,
                    "delete": True,
                    "editTitle": True,
                    "editDescription": True,
                    "complete": True,
                    "close": True,
                    "assignUsers": "no",
                    "connect": True,
                    "editSubtasks": "no",
                    "editStickers": True,
                    "editPins": True,
                    "move": "no",
                    "sendMessages": True,
                    "sendFiles": True,
                    "editWhoToNotify": "no"
                },
                "myTasks": {
                    "show": True,
                    "delete": True,
                    "editTitle": True,
                    "editDescription": True,
                    "complete": True,
                    "close": True,
                    "assignUsers": "no",
                    "connect": True,
                    "editSubtasks": "no",
                    "editStickers": True,
                    "editPins": True,
                    "move": "no",
                    "sendMessages": True,
                    "sendFiles": True,
                    "editWhoToNotify": "no"
                },
                "createdByMeTasks": {
                    "show": True,
                    "delete": True,
                    "editTitle": True,
                    "editDescription": True,
                    "complete": True,
                    "close": True,
                    "assignUsers": "no",
                    "connect": True,
                    "editSubtasks": "no",
                    "editStickers": True,
                    "editPins": True,
                    "move": "no",
                    "sendMessages": True,
                    "sendFiles": True,
                    "editWhoToNotify": "no"
                }
            },
            "settings": True
        },
        "children": {}
        }
        new_role = client.project_roles.create(
            project_id=project_id,
            name="Новая роль",
            permissions=permissions
        )
        print(f"Создана новая роль: {new_role})")

        # Обновление роли
        updated_role = client.project_roles.update(
            project_id=project_id,
            id=new_role.get('id'),
            name="Обновленная роль",
            permissions=permissions
        )
        print(f"Роль обновлена: {updated_role}")

        # Удаление роли
        deleted_role = client.project_roles.delete(
            project_id=project_id,
            id=new_role.get('id')
        )
        print(f"Роль удалена: {deleted_role}")
    except Exception as e:
        print(f"Ошибка при создании роли: {e}")


def departments_examples(client):
    """Примеры работы с отделами."""
    print("\n=== Примеры работы с отделами ===")

    # Получение списка отделов
    try:
        departments_response = client.departments.list(limit=10)

        if 'content' in departments_response:
            departments = departments_response['content']
        else:
            departments = []

        print(f"Получено отделов: {len(departments)}")

        # Вывод информации об отделах
        for department in departments:
            print(f"Отдел: {department.get('title')} (ID: {department.get('id')})")

        # Если есть отделы, используем первый для примеров
        if departments:
            department_id = departments[0]['id']

            # Получение отдела по ID
            department = client.departments.get(department_id)
            print(f"\nПолучен отдел: {department.get('title')}")

    except Exception as e:
        print(f"Ошибка при работе с отделами: {e}")

    try:
        # Создание нового отдела
        new_department = client.departments.create(
            title="Новый отдел"
        )
        print(f"Создан новый отдел: {new_department.get('title')} (ID: {new_department.get('id')})")

        # Обновление отдела
        updated_department = client.departments.update(
            id=new_department.get('id'),
            title="Обновленный отдел"
        )
        print(f"Отдел обновлен: (ID: {updated_department.get('id')})")

        # Удаление отдела
        deleted_department = client.departments.update(
            id=new_department.get('id'),
            deleted=True
        )
        print(f"Отдел удален: (ID: {deleted_department.get('id')})")

    except Exception as e:
        print(f"Ошибка при создании отдела: {e}")


def boards_examples(client):
    """Примеры работы с досками."""
    print("\n=== Примеры работы с досками ===")

    # Получение списка досок
    try:
        boards_response = client.boards.list(limit=10)

        if 'content' in boards_response:
            boards = boards_response['content']
        else:
            boards = []

        print(f"Получено досок: {len(boards)}")

        # Вывод информации о досках
        for board in boards:
            print(f"Доска: {board.get('title')} (ID: {board.get('id')})")

        # Если есть доски, используем первую для примеров
        if boards:
            board_id = boards[0]['id']

            # Получение доски по ID
            board = client.boards.get(board_id)
            print(f"\nПолучена доска: {board.get('title')}")

    except Exception as e:
        print(f"Ошибка при работе с досками: {e}")

    # Создание новой доски
    try:
        new_board = client.boards.create(
            title="Новая тестовая доска",
            project_id=board.get('projectId')
        )
        print(f"Создана новая доска: (ID: {new_board.get('id')})")

        # Обновление доски
        updated_board = client.boards.update(
            id=new_board.get('id'),
            title="Обновленная доска",
            deleted=False
        )
        print(f"Доска обновлена: {updated_board}")

        # Удаление доски
        deleted_borad = client.boards.update(
            id=new_board.get('id'),
            deleted=True,
        )
        print(f"Доска удалена: {updated_board}")

    except Exception as e:
        print(f"Ошибка при создании доски: {e}")


def columns_examples(client):
    """Примеры работы с колонками."""
    print("\n=== Примеры работы с колонками ===")

    # Получение списка колонок
    try:
        # Для получения колонок нужен ID доски
        boards_response = client.boards.list(limit=1)

        boards = []
        if 'content' in boards_response:
            boards = boards_response['content']

        if boards:
            board_id = boards[0]['id']

            columns_response = client.columns.list(board_id=board_id, limit=10)

            if 'content' in columns_response:
                columns = columns_response['content']
            else:
                columns = []

            print(f"Получено колонок: {len(columns)}")

            # Вывод информации о колонках
            for column in columns:
                print(f"Колонка: {column.get('title')} (ID: {column.get('id')})")

            # Если есть колонки, используем первую для примеров
            if columns:
                column_id = columns[0]['id']

                # Получение колонки по ID
                column = client.columns.get(column_id)
                print(f"\nПолучена колонка: {column.get('title')}")

        else:
            print("Нет доступных досок для получения колонок")

    except Exception as e:
        print(f"Ошибка при работе с колонками: {e}")

    # Создание новой колонки
    try:
        new_column = client.columns.create(
            title="Новая колонка",
            color=1,
            board_id=board_id
        )
        print(f"Создана новая колонка: {new_column})")

        # Обновление колонки
        updated_column = client.columns.update(
            title="Обновленная колонка",
            color=16,
            id=new_column.get('id')
        )
        print(f"Колонка обновлена: {updated_column}")

        # Удаление колонки
        deleted_column = client.columns.update(
            deleted=True,
            id=new_column.get('id')
        )
        print(f"Колонка удалена: {deleted_column}")

    except Exception as e:
        print(f"Ошибка при создании колонки: {e}")


def tasks_examples(client):
    """Примеры работы с задачами."""
    print("\n=== Примеры работы с задачами ===")

    # Получение списка задач
    try:
        tasks_response = client.tasks.list(limit=10)

        if 'content' in tasks_response:
            tasks = tasks_response['content']
        else:
            tasks = []

        print(f"Получено задач: {len(tasks)}")

        # Вывод информации о задачах
        for task in tasks:
            print(f"Задача: {task.get('title')} (ID: {task.get('id')})")

        # Если есть задачи, используем первую для примеров
        if tasks:
            task_id = tasks[0]['id']

            # Получение задачи по ID
            task = client.tasks.get(task_id)
            print(f"\nПолучена задача: {task.get('title')}")

    except Exception as e:
        print(f"Ошибка при работе с задачами: {e}")

    # Создание новой задачи
    try:
        new_task = client.tasks.create(
            title="Тестовая задача",
            column_id="column_id",
            description="Описание тестовой задачи"
        )
        print(f"Создана новая задача: {new_task})")

        # Обновление задачи
        updated_task = client.tasks.update(
            id=new_task.get('id'),
            title="Обновленная задача",
            color="task-turquoise"
        )
        print(f"Задача обновлена: {updated_task}")

        # Удаление задачи
        deleted_task = client.tasks.update(
            id=new_task.get('id'),
            deleted=True
        )
        print(f"Задача удалена: {deleted_task}")

    except Exception as e:
        print(f"Ошибка при создании задачи: {e}")


def string_stickers_examples(client):
    """Примеры работы со строковыми стикерами."""
    print("\n=== Примеры работы со строковыми стикерами ===")

    # Получение списка строковых стикеров
    try:
        stickers_response = client.string_stickers.list(limit=10)

        if 'content' in stickers_response:
            stickers = stickers_response['content']
        else:
            stickers = []

        print(f"Получено строковых стикеров: {len(stickers)}")

        # Вывод информации о стикерах
        for sticker in stickers:
            print(f"Строковый стикер: {sticker.get('name')} (ID: {sticker.get('id')})")

        # Если есть стикеры, используем первый для примеров
        if stickers:
            sticker_id = stickers[0]['id']

            # Получение стикера по ID
            sticker = client.string_stickers.get(sticker_id)
            print(f"\nПолучен строковый стикер: {sticker.get('name')}")

    except Exception as e:
        print(f"Ошибка при работе со строковыми стикерами: {e}")

    # Создание нового стикера
    try:
        new_sticker = client.string_stickers.create(
            name="Новый строковый стикер"
        )
        print(f"Создан новый строковый стикер: {new_sticker})")

        # Обновление стикера
        updated_sticker = client.string_stickers.update(
            id=new_sticker.get('id'),
            name="Обновленный строковый стикер"
        )
        print(f"Строковый стикер обновлен: {updated_sticker}")

        # Удаление стикера
        deleted_sticker = client.string_stickers.update(
            id=new_sticker.get('id'),
            deleted=True
        )
        print(f"Строковый стикер удален: {deleted_sticker}")

    except Exception as e:
        print(f"Ошибка при создании строкового стикера: {e}")


def string_sticker_states_examples(client):
    """Примеры работы с состояниями строковых стикеров."""
    print("\n=== Примеры работы с состояниями строковых стикеров ===")

    # Получение списка состояний строковых стикеров
    try:
        # Для получения состояний нужен ID стикера
        stickers_response = client.string_stickers.list(limit=1)

        stickers = []
        if 'content' in stickers_response:
            stickers = stickers_response['content']

        if stickers:
            sticker_id = stickers[0]['id']
            states_response = client.string_sticker_states.list(parent_id=sticker_id, limit=10)

            if 'content' in states_response:
                states = states_response['content']
            else:
                states = []

            print(f"Получено состояний строковых стикеров: {len(states)}")

            # Вывод информации о состояниях
            for state in states:
                print(f"Состояние строкового стикера: {state.get('name')} (ID: {state.get('id')})")

            # Если есть состояния, используем первое для примеров
            if states:
                state_id = states[0]['id']

                # Получение состояния по ID
                state = client.string_sticker_states.get(parent_id=sticker_id, id=state_id)
                print(f"\nПолучено состояние строкового стикера: {state.get('name')}")

                # Обновление состояния (закомментировано, так как изменяет данные)
                # updated_state = client.string_sticker_states.update(
                #     parent_id=sticker_id,
                #     id=state_id,
                #     name="Обновленное состояние"
                # )
                # print(f"Состояние строкового стикера обновлено: {updated_state.get('name')}")
        else:
            print("Нет доступных строковых стикеров для получения состояний")

    except Exception as e:
        print(f"Ошибка при работе с состояниями строковых стикеров: {e}")

    # Создание нового состояния (закомментировано, так как создает реальные данные)
    # try:
    #     new_state = client.string_sticker_states.create(
    #         parent_id="sticker_id_here",
    #         name="Новое состояние"
    #     )
    #     print(f"Создано новое состояние строкового стикера: {new_state.get('name')} (ID: {new_state.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании состояния строкового стикера: {e}")


def group_chats_examples(client):
    """Примеры работы с групповыми чатами."""
    print("\n=== Примеры работы с групповыми чатами ===")

    # Получение списка групповых чатов
    try:
        group_chats_response = client.group_chats.list(limit=10)

        if 'content' in group_chats_response:
            group_chats = group_chats_response['content']
        elif 'items' in group_chats_response:
            group_chats = group_chats_response['items']
        else:
            group_chats = []

        print(f"Получено групповых чатов: {len(group_chats)}")

        # Вывод информации о групповых чатах
        for chat in group_chats:
            print(f"Групповой чат: {chat.get('title')} (ID: {chat.get('id')})")

        # Если есть групповые чаты, используем первый для примеров
        if group_chats:
            chat_id = group_chats[0]['id']

            # Получение группового чата по ID
            chat = client.group_chats.get(chat_id)
            print(f"\nПолучен групповой чат: {chat.get('title')}")

            # Обновление группового чата (закомментировано, так как изменяет данные)
            # updated_chat = client.group_chats.update(
            #     id=chat_id,
            #     title="Обновленный чат"
            # )
            # print(f"Групповой чат обновлен: {updated_chat.get('title')}")

    except Exception as e:
        print(f"Ошибка при работе с групповыми чатами: {e}")

    # Создание нового группового чата (закомментировано, так как создает реальные данные)
    # try:
    #     new_chat = client.group_chats.create(
    #         title="Новый групповой чат",
    #         users={"user_id_here": {"role": "admin"}}
    #     )
    #     print(f"Создан новый групповой чат: {new_chat.get('title')} (ID: {new_chat.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании группового чата: {e}")


def chat_messages_examples(client):
    """Примеры работы с сообщениями чата."""
    print("\n=== Примеры работы с сообщениями чата ===")

    # Получение списка сообщений чата
    try:
        # Для получения сообщений нужен ID чата
        group_chats_response = client.group_chats.list(limit=1)

        group_chats = []
        if 'content' in group_chats_response:
            group_chats = group_chats_response['content']
        elif 'items' in group_chats_response:
            group_chats = group_chats_response['items']

        if group_chats:
            chat_id = group_chats[0]['id']

            messages_response = client.chat_messages.list(parent_id=chat_id, limit=10)

            if 'content' in messages_response:
                messages = messages_response['content']
            elif 'items' in messages_response:
                messages = messages_response['items']
            else:
                messages = []

            print(f"Получено сообщений: {len(messages)}")

            # Вывод информации о сообщениях
            for message in messages:
                print(f"Сообщение: {message.get('text')} (ID: {message.get('id')})")

            # Если есть сообщения, используем первое для примеров
            if messages:
                message_id = messages[0]['id']

                # Получение сообщения по ID
                message = client.chat_messages.get(parent_id=chat_id, id=message_id)
                print(f"\nПолучено сообщение: {message.get('text')}")

                # Обновление сообщения (закомментировано, так как изменяет данные)
                # updated_message = client.chat_messages.update(
                #     parent_id=chat_id,
                #     id=message_id,
                #     text="Обновленное сообщение"
                # )
                # print(f"Сообщение обновлено: {updated_message.get('text')}")
        else:
            print("Нет доступных групповых чатов для получения сообщений")

    except Exception as e:
        print(f"Ошибка при работе с сообщениями чата: {e}")

    # Создание нового сообщения (закомментировано, так как создает реальные данные)
    # try:
    #     new_message = client.chat_messages.create(
    #         parent_id="chat_id_here",
    #         text="Тестовое сообщение",
    #         text_html="<p>Тестовое сообщение</p>"
    #     )
    #     print(f"Создано новое сообщение: {new_message.get('text')} (ID: {new_message.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании сообщения: {e}")


def sprint_stickers_examples(client):
    """Примеры работы со стикерами спринта."""
    print("\n=== Примеры работы со стикерами спринта ===")

    # Получение списка стикеров спринта
    try:
        stickers_response = client.sprint_stickers.list(limit=10)

        if 'content' in stickers_response:
            stickers = stickers_response['content']
        elif 'items' in stickers_response:
            stickers = stickers_response['items']
        else:
            stickers = []

        print(f"Получено стикеров спринта: {len(stickers)}")

        # Вывод информации о стикерах
        for sticker in stickers:
            print(f"Стикер спринта: {sticker.get('name')} (ID: {sticker.get('id')})")

        # Если есть стикеры, используем первый для примеров
        if stickers:
            sticker_id = stickers[0]['id']

            # Получение стикера по ID
            sticker = client.sprint_stickers.get(sticker_id)
            print(f"\nПолучен стикер спринта: {sticker.get('name')}")

            # Обновление стикера (закомментировано, так как изменяет данные)
            # updated_sticker = client.sprint_stickers.update(
            #     id=sticker_id,
            #     name="Обновленный стикер"
            # )
            # print(f"Стикер спринта обновлен: {updated_sticker.get('name')}")

    except Exception as e:
        print(f"Ошибка при работе со стикерами спринта: {e}")

    # Создание нового стикера (закомментировано, так как создает реальные данные)
    # try:
    #     new_sticker = client.sprint_stickers.create(
    #         name="Новый стикер спринта",
    #         color="#FF5733"
    #     )
    #     print(f"Создан новый стикер спринта: {new_sticker.get('name')} (ID: {new_sticker.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании стикера спринта: {e}")


def sprint_sticker_states_examples(client):
    """Примеры работы с состояниями стикеров спринта."""
    print("\n=== Примеры работы с состояниями стикеров спринта ===")

    # Получение списка состояний стикеров спринта
    try:
        # Для получения состояний нужен ID стикера
        stickers_response = client.sprint_stickers.list(limit=1)

        stickers = []
        if 'content' in stickers_response:
            stickers = stickers_response['content']
        elif 'items' in stickers_response:
            stickers = stickers_response['items']

        if stickers:
            sticker_id = stickers[0]['id']

            states_response = client.sprint_sticker_states.list(parent_id=sticker_id, limit=10)

            if 'content' in states_response:
                states = states_response['content']
            elif 'items' in states_response:
                states = states_response['items']
            else:
                states = []

            print(f"Получено состояний стикеров: {len(states)}")

            # Вывод информации о состояниях
            for state in states:
                print(f"Состояние стикера: {state.get('name')} (ID: {state.get('id')})")

            # Если есть состояния, используем первое для примеров
            if states:
                state_id = states[0]['id']

                # Получение состояния по ID
                state = client.sprint_sticker_states.get(parent_id=sticker_id, id=state_id)
                print(f"\nПолучено состояние стикера: {state.get('name')}")

                # Обновление состояния (закомментировано, так как изменяет данные)
                # updated_state = client.sprint_sticker_states.update(
                #     parent_id=sticker_id,
                #     id=state_id,
                #     name="Обновленное состояние"
                # )
                # print(f"Состояние стикера обновлено: {updated_state.get('name')}")
        else:
            print("Нет доступных стикеров спринта для получения состояний")

    except Exception as e:
        print(f"Ошибка при работе с состояниями стикеров спринта: {e}")

    # Создание нового состояния (закомментировано, так как создает реальные данные)
    # try:
    #     new_state = client.sprint_sticker_states.create(
    #         parent_id="sticker_id_here",
    #         name="Новое состояние"
    #     )
    #     print(f"Создано новое состояние стикера: {new_state.get('name')} (ID: {new_state.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании состояния стикера: {e}")


def webhooks_examples(client):
    """Примеры работы с вебхуками."""
    print("\n=== Примеры работы с вебхуками ===")

    # Получение списка вебхуков
    try:
        webhooks_response = client.webhooks.list(limit=10)

        if 'content' in webhooks_response:
            webhooks = webhooks_response['content']
        elif 'items' in webhooks_response:
            webhooks = webhooks_response['items']
        else:
            webhooks = []

        print(f"Получено вебхуков: {len(webhooks)}")

        # Вывод информации о вебхуках
        for webhook in webhooks:
            print(f"Вебхук: {webhook.get('url')} (ID: {webhook.get('id')})")

        # Если есть вебхуки, используем первый для примеров
        if webhooks:
            webhook_id = webhooks[0]['id']

            # Получение вебхука по ID
            webhook = client.webhooks.get(webhook_id)
            print(f"\nПолучен вебхук: {webhook.get('url')}")

            # Обновление вебхука (закомментировано, так как изменяет данные)
            # updated_webhook = client.webhooks.update(
            #     id=webhook_id,
            #     url="https://example.com/updated-webhook"
            # )
            # print(f"Вебхук обновлен: {updated_webhook.get('url')}")

    except Exception as e:
        print(f"Ошибка при работе с вебхуками: {e}")

    # Создание нового вебхука (закомментировано, так как создает реальные данные)
    # try:
    #     new_webhook = client.webhooks.create(
    #         url="https://example.com/webhook",
    #         events=["task.created", "task.updated"]
    #     )
    #     print(f"Создан новый вебхук: {new_webhook.get('url')} (ID: {new_webhook.get('id')})")
    # except Exception as e:
    #     print(f"Ошибка при создании вебхука: {e}")


def main():
    """Основная функция для запуска примеров."""
    # Создание клиента
    client = YouGileClient()

    # Запуск примеров
    auth_examples(client)
    # employees_examples(client)
    # projects_examples(client)
    # project_roles_examples(client)
    # departments_examples(client)
    # boards_examples(client)
    # columns_examples(client)
    # tasks_examples(client)
    # string_stickers_examples(client)
    # string_sticker_states_examples(client)
    # sprint_stickers_examples(client)

    #sprint_sticker_states_examples(client)
    #group_chats_examples(client)
    #chat_messages_examples(client)
    #webhooks_examples(client)


if __name__ == "__main__":
    main()
