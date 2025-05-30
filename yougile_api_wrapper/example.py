"""
Пример использования YouGile API клиента.

Этот файл содержит примеры использования всех ресурсов и методов API с использованием моделей данных.
Примечание: Для выполнения всех запросов (кроме авторизации) требуется действующий токен авторизации.
"""

from yougile_api import YouGileClient
from yougile_api.models.employee import Employee
from yougile_api.models.project import Project
from yougile_api.models.project_role import ProjectRole
from yougile_api.models.department import Department
from yougile_api.models.board import Board
from yougile_api.models.column import Column
from yougile_api.models.task import Task
from yougile_api.models.string_sticker import StringSticker
from yougile_api.models.sprint_sticker import SprintSticker


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
    """Примеры работы с сотрудниками с использованием модели Employee."""
    print("\n=== Примеры работы с сотрудниками ===")

    # Получение списка сотрудников
    try:
        employees_response = client.employees.list(limit=10)
        print(f"Employees Response: {employees_response}")

        employees_list = []
        if 'content' in employees_response:
            # Преобразование словарей в объекты модели Employee
            for emp_data in employees_response['content']:
                employee_model = Employee(**emp_data)
                employees_list.append(employee_model)

        print(f"Получено сотрудников: {len(employees_list)}")

        # Вывод информации о сотрудниках через модель
        for employee in employees_list:
            print(f"Сотрудник: {employee.email} (ID: {employee.id})")

        # Если есть сотрудники, используем первого для примеров
        if employees_list:
            employee_id = employees_list[0].id

            # Получение сотрудника по ID
            employee_data = client.employees.get(employee_id)
            employee_model = Employee(**employee_data)
            print(f"\nПолучен сотрудник: {employee_model.email}")
            print(f"Администратор: {employee_model.is_admin}")

    except Exception as e:
        print(f"Ошибка при работе с сотрудниками: {e}")

    # Создание нового сотрудника с использованием модели
    try:
        # Создаем экземпляр модели
        new_employee_model = Employee(
            email="new.employee@example.com",
            is_admin=False
        )

        # Преобразуем модель в словарь для API запроса
        new_employee_data = new_employee_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_employee_data = client.employees.create(**new_employee_data)

        # Преобразуем ответ в модель
        created_employee = Employee(**created_employee_data)
        print(f"Создан новый сотрудник: {created_employee.email} (ID: {created_employee.id})")

        # Обновление сотрудника с использованием модели
        created_employee.is_admin = True
        updated_data = created_employee.dict(by_alias=True, exclude_none=True)

        updated_employee_data = client.employees.update(
            id=created_employee.id,
            **updated_data
        )

        updated_employee = Employee(**updated_employee_data)
        print(f"Сотрудник обновлен: {updated_employee.email} (Администратор: {updated_employee.is_admin})")

        # Удаление сотрудника
        deleted_employee_data = client.employees.delete(created_employee.id)
        deleted_employee = Employee(**deleted_employee_data)
        print(f"Сотрудник удален: {deleted_employee.email}")

    except Exception as e:
        print(f"Ошибка при работе с сотрудником: {e}")


def projects_examples(client):
    """Примеры работы с проектами с использованием модели Project."""
    print("\n=== Примеры работы с проектами ===")

    # Получение списка проектов
    try:
        projects_response = client.projects.list(limit=10)
        print(f"Projects Response: {projects_response}")

        projects_list = []
        if 'content' in projects_response:
            # Преобразование словарей в объекты модели Project
            for proj_data in projects_response['content']:
                project_model = Project(**proj_data)
                projects_list.append(project_model)

        print(f"Получено проектов: {len(projects_list)}")

        # Вывод информации о проектах через модель
        for project in projects_list:
            print(f"Проект: {project.title} (ID: {project.id})")

        # Если есть проекты, используем первый для примеров
        if projects_list:
            project_id = projects_list[0].id

            # Получение проекта по ID
            project_data = client.projects.get(project_id)
            project_model = Project(**project_data)
            print(f"\nПолучен проект: {project_model.title}")
            print(f"Пользователи проекта: {project_model.users}")

    except Exception as e:
        print(f"Ошибка при работе с проектами: {e}")

    # Создание нового проекта с использованием модели
    try:
        # Создаем экземпляр модели
        new_project_model = Project(
            title="Новый тестовый проект",
            users={"807972fa-dcf1-4d52-a9a3-9b9c8ef0100d": "admin"}
        )

        # Преобразуем модель в словарь для API запроса
        new_project_data = new_project_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_project_data = client.projects.create(**new_project_data)

        # Преобразуем ответ в модель
        created_project = Project(**created_project_data)
        print(f"Создан новый проект: {created_project.title} (ID: {created_project.id})")

        # Обновление проекта с использованием модели
        created_project.title = "Обновленный проект"
        updated_data = created_project.dict(by_alias=True, exclude_none=True)

        updated_project_data = client.projects.update(
            id=created_project.id,
            **updated_data
        )

        updated_project = Project(**updated_project_data)
        print(f"Проект обновлен: {updated_project.title}")

        # Удаление проекта (через обновление поля deleted)
        updated_project.deleted = True
        delete_data = updated_project.dict(by_alias=True, exclude_none=True)

        deleted_project_data = client.projects.update(
            id=updated_project.id,
            **delete_data
        )

        deleted_project = Project(**deleted_project_data)
        print(f"Проект удален: {deleted_project.title} (Удален: {deleted_project.deleted})")

    except Exception as e:
        print(f"Ошибка при работе с проектом: {e}")


def project_roles_examples(client):
    """Примеры работы с ролями проекта с использованием модели ProjectRole."""
    print("\n=== Примеры работы с ролями проекта ===")

    # Получение списка ролей проекта
    try:
        # Для получения ролей нужен ID проекта
        projects_response = client.projects.list(limit=1)

        projects_list = []
        if 'content' in projects_response:
            for proj_data in projects_response['content']:
                project_model = Project(**proj_data)
                projects_list.append(project_model)

        if projects_list:
            project_id = projects_list[0].id
            print(f"Используем проект: {projects_list[0].title} (ID: {project_id})")

            roles_response = client.project_roles.list(project_id=project_id, limit=10)

            roles_list = []
            if 'content' in roles_response:
                # Преобразование словарей в объекты модели ProjectRole
                for role_data in roles_response['content']:
                    role_model = ProjectRole(**role_data)
                    roles_list.append(role_model)

            print(f"Получено ролей: {len(roles_list)}")

            # Вывод информации о ролях через модель
            for role in roles_list:
                print(f"Роль: {role.name} (ID: {role.id})")

            # Если есть роли, используем первую для примеров
            if roles_list:
                role_id = roles_list[0].id

                # Получение роли по ID
                role_data = client.project_roles.get(parent_id=project_id, id=role_id)
                role_model = ProjectRole(**role_data)
                print(f"\nПолучена роль: {role_model.name}")
                print(f"Разрешения роли: {role_model.permissions}")
        else:
            print("Нет доступных проектов для получения ролей")

    except Exception as e:
        print(f"Ошибка при работе с ролями проекта: {e}")

    try:
        # Создание новой роли с использованием модели
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

        # Создаем экземпляр модели
        new_role_model = ProjectRole(
            name="Новая роль",
            permissions=permissions
        )

        # Преобразуем модель в словарь для API запроса
        new_role_data = new_role_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_role_data = client.project_roles.create(
            project_id=project_id,
            **new_role_data
        )

        # Преобразуем ответ в модель
        created_role = ProjectRole(**created_role_data)
        print(f"Создана новая роль: {created_role.name} (ID: {created_role.id})")

        # Обновление роли с использованием модели
        created_role.name = "Обновленная роль"
        updated_data = created_role.dict(by_alias=True, exclude_none=True)

        updated_role_data = client.project_roles.update(
            project_id=project_id,
            id=created_role.id,
            **updated_data
        )

        updated_role = ProjectRole(**updated_role_data)
        print(f"Роль обновлена: {updated_role.name}")

        # Удаление роли
        deleted_role_data = client.project_roles.delete(
            project_id=project_id,
            id=updated_role.id
        )

        if deleted_role_data:
            print(f"Роль удалена успешно")
        else:
            print(f"Ошибка при удалении роли")

    except Exception as e:
        print(f"Ошибка при работе с ролью: {e}")


def departments_examples(client):
    """Примеры работы с отделами с использованием модели Department."""
    print("\n=== Примеры работы с отделами ===")

    # Получение списка отделов
    try:
        departments_response = client.departments.list(limit=10)

        departments_list = []
        if 'content' in departments_response:
            # Преобразование словарей в объекты модели Department
            for dept_data in departments_response['content']:
                department_model = Department(**dept_data)
                departments_list.append(department_model)

        print(f"Получено отделов: {len(departments_list)}")

        # Вывод информации об отделах через модель
        for department in departments_list:
            print(f"Отдел: {department.title} (ID: {department.id})")

        # Если есть отделы, используем первый для примеров
        if departments_list:
            department_id = departments_list[0].id

            # Получение отдела по ID
            department_data = client.departments.get(department_id)
            department_model = Department(**department_data)
            print(f"\nПолучен отдел: {department_model.title}")
            print(f"Удален: {department_model.deleted}")

    except Exception as e:
        print(f"Ошибка при работе с отделами: {e}")

    try:
        # Создание нового отдела с использованием модели
        new_department_model = Department(
            title="Новый отдел"
        )

        # Преобразуем модель в словарь для API запроса
        new_department_data = new_department_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_department_data = client.departments.create(**new_department_data)

        # Преобразуем ответ в модель
        created_department = Department(**created_department_data)
        print(f"Создан новый отдел: {created_department.title} (ID: {created_department.id})")

        # Обновление отдела с использованием модели
        created_department.title = "Обновленный отдел"
        updated_data = created_department.dict(by_alias=True, exclude_none=True)

        updated_department_data = client.departments.update(
            id=created_department.id,
            **updated_data
        )

        updated_department = Department(**updated_department_data)
        print(f"Отдел обновлен: {updated_department.title}")

        # Удаление отдела (через обновление поля deleted)
        updated_department.deleted = True
        delete_data = updated_department.dict(by_alias=True, exclude_none=True)

        deleted_department_data = client.departments.update(
            id=updated_department.id,
            **delete_data
        )

        deleted_department = Department(**deleted_department_data)
        print(f"Отдел удален: {deleted_department.title} (Удален: {deleted_department.deleted})")

    except Exception as e:
        print(f"Ошибка при работе с отделом: {e}")


def boards_examples(client):
    """Примеры работы с досками с использованием модели Board."""
    print("\n=== Примеры работы с досками ===")

    # Получение списка досок
    try:
        boards_response = client.boards.list(limit=10)

        boards_list = []
        if 'content' in boards_response:
            # Преобразование словарей в объекты модели Board
            for board_data in boards_response['content']:
                board_model = Board(**board_data)
                boards_list.append(board_model)

        print(f"Получено досок: {len(boards_list)}")

        # Вывод информации о досках через модель
        for board in boards_list:
            print(f"Доска: {board.title} (ID: {board.id}, Проект: {board.project_id})")

        # Если есть доски, используем первую для примеров
        if boards_list:
            board_id = boards_list[0].id
            project_id = boards_list[0].project_id

            # Получение доски по ID
            board_data = client.boards.get(board_id)
            board_model = Board(**board_data)
            print(f"\nПолучена доска: {board_model.title}")
            print(f"Проект: {board_model.project_id}")
            print(f"Удалена: {board_model.deleted}")

    except Exception as e:
        print(f"Ошибка при работе с досками: {e}")

    # Создание новой доски с использованием модели
    try:
        # Создаем экземпляр модели
        new_board_model = Board(
            title="Новая тестовая доска",
            project_id=project_id
        )

        # Преобразуем модель в словарь для API запроса
        new_board_data = new_board_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_board_data = client.boards.create(**new_board_data)

        # Преобразуем ответ в модель
        created_board = Board(**created_board_data)
        print(f"Создана новая доска: {created_board.title} (ID: {created_board.id})")

        # Обновление доски с использованием модели
        created_board.title = "Обновленная доска"
        updated_data = created_board.dict(by_alias=True, exclude_none=True)

        updated_board_data = client.boards.update(
            id=created_board.id,
            **updated_data
        )

        updated_board = Board(**updated_board_data)
        print(f"Доска обновлена: {updated_board.title}")

        # Удаление доски (через обновление поля deleted)
        updated_board.deleted = True
        delete_data = updated_board.dict(by_alias=True, exclude_none=True)

        deleted_board_data = client.boards.update(
            id=updated_board.id,
            **delete_data
        )

        deleted_board = Board(**deleted_board_data)
        print(f"Доска удалена: {deleted_board.title} (Удалена: {deleted_board.deleted})")

    except Exception as e:
        print(f"Ошибка при работе с доской: {e}")


def columns_examples(client):
    """Примеры работы с колонками с использованием модели Column."""
    print("\n=== Примеры работы с колонками ===")

    # Получение списка колонок
    try:
        # Для получения колонок нужен ID доски
        boards_response = client.boards.list(limit=1)

        boards_list = []
        if 'content' in boards_response:
            for board_data in boards_response['content']:
                board_model = Board(**board_data)
                boards_list.append(board_model)

        if boards_list:
            board_id = boards_list[0].id
            print(f"Используем доску: {boards_list[0].title} (ID: {board_id})")

            columns_response = client.columns.list(board_id=board_id, limit=10)

            columns_list = []
            if 'content' in columns_response:
                # Преобразование словарей в объекты модели Column
                for column_data in columns_response['content']:
                    column_model = Column(**column_data)
                    columns_list.append(column_model)

            print(f"Получено колонок: {len(columns_list)}")

            # Вывод информации о колонках через модель
            for column in columns_list:
                print(f"Колонка: {column.title} (ID: {column.id}, Цвет: {column.color})")

            # Если есть колонки, используем первую для примеров
            if columns_list:
                column_id = columns_list[0].id

                # Получение колонки по ID
                column_data = client.columns.get(column_id)
                column_model = Column(**column_data)
                print(f"\nПолучена колонка: {column_model.title}")
                print(f"Цвет: {column_model.color}")
                print(f"Доска: {column_model.board_id}")
                print(f"Удалена: {column_model.deleted}")
        else:
            print("Нет доступных досок для получения колонок")

    except Exception as e:
        print(f"Ошибка при работе с колонками: {e}")

    # Создание новой колонки с использованием модели
    try:
        # Создаем экземпляр модели
        new_column_model = Column(
            title="Новая колонка",
            color=1,
            board_id=board_id
        )

        # Преобразуем модель в словарь для API запроса
        new_column_data = new_column_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_column_data = client.columns.create(**new_column_data)

        # Преобразуем ответ в модель
        created_column = Column(**created_column_data)
        print(f"Создана новая колонка: {created_column.title} (ID: {created_column.id})")

        # Обновление колонки с использованием модели
        created_column.title = "Обновленная колонка"
        created_column.color = 2
        updated_data = created_column.dict(by_alias=True, exclude_none=True)

        updated_column_data = client.columns.update(
            id=created_column.id,
            **updated_data
        )

        updated_column = Column(**updated_column_data)
        print(f"Колонка обновлена: {updated_column.title} (Цвет: {updated_column.color})")

        # Удаление колонки (через обновление поля deleted)
        updated_column.deleted = True
        delete_data = updated_column.dict(by_alias=True, exclude_none=True)

        deleted_column_data = client.columns.update(
            id=updated_column.id,
            **delete_data
        )

        deleted_column = Column(**deleted_column_data)
        print(f"Колонка удалена: {deleted_column.title} (Удалена: {deleted_column.deleted})")

    except Exception as e:
        print(f"Ошибка при работе с колонкой: {e}")


def tasks_examples(client):
    """Примеры работы с задачами с использованием модели Task."""
    print("\n=== Примеры работы с задачами ===")

    # Получение списка задач
    try:
        tasks_response = client.tasks.list(limit=10)

        tasks_list = []
        if 'content' in tasks_response:
            # Преобразование словарей в объекты модели Task
            for task_data in tasks_response['content']:
                task_model = Task(**task_data)
                tasks_list.append(task_model)

        print(f"Получено задач: {len(tasks_list)}")

        # Вывод информации о задачах через модель
        for task in tasks_list:
            print(f"Задача: {task.title} (ID: {task.id})")
            if task.assigned:
                print(f"  Исполнители: {task.assigned}")
            if task.deadline:
                print(f"  Срок: {task.deadline}")

        # Если есть задачи, используем первую для примеров
        if tasks_list:
            task_id = tasks_list[0].id

            # Получение задачи по ID
            task_data = client.tasks.get(task_id)
            task_model = Task(**task_data)
            print(f"\nПолучена задача: {task_model.title}")
            print(f"Описание: {task_model.description}")
            print(f"Колонка: {task_model.column_id}")
            print(f"Завершена: {task_model.completed}")
            print(f"Архивирована: {task_model.archived}")
            if task_model.stickers:
                print(f"Стикеры: {task_model.stickers}")

    except Exception as e:
        print(f"Ошибка при работе с задачами: {e}")

    # Получение колонки для создания задачи
    try:
        # Для создания задачи нужен ID колонки
        boards_response = client.boards.list(limit=1)

        if 'content' in boards_response and boards_response['content']:
            board_id = boards_response['content'][0]['id']

            columns_response = client.columns.list(board_id=board_id, limit=1)

            if 'content' in columns_response and columns_response['content']:
                column_id = columns_response['content'][0]['id']

                # Создание новой задачи с использованием модели
                new_task_model = Task(
                    title="Тестовая задача",
                    column_id=column_id,
                    description="Описание тестовой задачи",
                    color="task-turquoise"
                )

                # Преобразуем модель в словарь для API запроса
                new_task_data = new_task_model.dict(by_alias=True, exclude_none=True)

                # Отправляем запрос на создание
                created_task_data = client.tasks.create(**new_task_data)

                # Преобразуем ответ в модель
                created_task = Task(**created_task_data)
                print(f"Создана новая задача: {created_task.title} (ID: {created_task.id})")

                # Обновление задачи с использованием модели
                created_task.title = "Обновленная задача"
                created_task.description = "Обновленное описание задачи"
                created_task.color = "task-green"
                updated_data = created_task.dict(by_alias=True, exclude_none=True)

                updated_task_data = client.tasks.update(
                    id=created_task.id,
                    **updated_data
                )

                updated_task = Task(**updated_task_data)
                print(f"Задача обновлена: {updated_task.title} (Цвет: {updated_task.color})")

                # Удаление задачи (через обновление поля deleted)
                updated_task.deleted = True
                delete_data = updated_task.dict(by_alias=True, exclude_none=True)

                deleted_task_data = client.tasks.update(
                    id=updated_task.id,
                    **delete_data
                )

                deleted_task = Task(**deleted_task_data)
                print(f"Задача удалена: {deleted_task.title} (Удалена: {deleted_task.deleted})")
            else:
                print("Нет доступных колонок для создания задачи")
        else:
            print("Нет доступных досок для получения колонок")

    except Exception as e:
        print(f"Ошибка при работе с задачей: {e}")


def string_stickers_examples(client):
    """Примеры работы со строковыми стикерами с использованием модели StringSticker."""
    print("\n=== Примеры работы со строковыми стикерами ===")

    # Получение списка строковых стикеров
    try:
        stickers_response = client.string_stickers.list(limit=10)

        stickers_list = []
        if 'content' in stickers_response:
            # Преобразование словарей в объекты модели StringSticker
            for sticker_data in stickers_response['content']:
                sticker_model = StringSticker(**sticker_data)
                stickers_list.append(sticker_model)

        print(f"Получено строковых стикеров: {len(stickers_list)}")

        # Вывод информации о стикерах через модель
        for sticker in stickers_list:
            print(f"Строковый стикер: {sticker.name} (ID: {sticker.id})")
            if sticker.states:
                print(f"  Количество состояний: {len(sticker.states)}")
            if sticker.icon:
                print(f"  Иконка: {sticker.icon}")

        # Если есть стикеры, используем первый для примеров
        if stickers_list:
            sticker_id = stickers_list[0].id

            # Получение стикера по ID
            sticker_data = client.string_stickers.get(sticker_id)
            sticker_model = StringSticker(**sticker_data)
            print(f"\nПолучен строковый стикер: {sticker_model.name}")
            print(f"Иконка: {sticker_model.icon}")
            if sticker_model.states:
                print(f"Состояния:")
                for state in sticker_model.states:
                    print(f"  - {state.get('name')} (ID: {state.get('id')})")

    except Exception as e:
        print(f"Ошибка при работе со строковыми стикерами: {e}")

    # Создание нового строкового стикера с использованием модели
    try:
        # Создаем экземпляр модели
        new_sticker_model = StringSticker(
            name="Новый строковый стикер",
            icon="icon-flag"
        )

        # Преобразуем модель в словарь для API запроса
        new_sticker_data = new_sticker_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_sticker_data = client.string_stickers.create(**new_sticker_data)

        # Преобразуем ответ в модель
        created_sticker = StringSticker(**created_sticker_data)
        print(f"Создан новый строковый стикер: {created_sticker.name} (ID: {created_sticker.id})")

        # Обновление стикера с использованием модели
        created_sticker.name = "Обновленный строковый стикер"
        created_sticker.icon = "icon-star"
        updated_data = created_sticker.dict(by_alias=True, exclude_none=True)

        updated_sticker_data = client.string_stickers.update(
            id=created_sticker.id,
            **updated_data
        )

        updated_sticker = StringSticker(**updated_sticker_data)
        print(f"Строковый стикер обновлен: {updated_sticker.name} (Иконка: {updated_sticker.icon})")

        # Удаление стикера (через обновление поля deleted)
        updated_sticker.deleted = True
        delete_data = updated_sticker.dict(by_alias=True, exclude_none=True)

        deleted_sticker_data = client.string_stickers.update(
            id=updated_sticker.id,
            **delete_data
        )

        deleted_sticker = StringSticker(**deleted_sticker_data)
        print(f"Строковый стикер удален: {deleted_sticker.name} (Удален: {deleted_sticker.deleted})")

    except Exception as e:
        print(f"Ошибка при работе со строковым стикером: {e}")


def sprint_stickers_examples(client):
    """Примеры работы со стикерами спринта с использованием модели SprintSticker."""
    print("\n=== Примеры работы со стикерами спринта ===")

    # Получение списка стикеров спринта
    try:
        stickers_response = client.sprint_stickers.list(limit=10)

        stickers_list = []
        if 'content' in stickers_response:
            # Преобразование словарей в объекты модели SprintSticker
            for sticker_data in stickers_response['content']:
                sticker_model = SprintSticker(**sticker_data)
                stickers_list.append(sticker_model)
        elif 'items' in stickers_response:
            # Альтернативный формат ответа
            for sticker_data in stickers_response['items']:
                sticker_model = SprintSticker(**sticker_data)
                stickers_list.append(sticker_model)

        print(f"Получено стикеров спринта: {len(stickers_list)}")

        # Вывод информации о стикерах через модель
        for sticker in stickers_list:
            print(f"Стикер спринта: {sticker.name} (ID: {sticker.id})")
            if sticker.states:
                print(f"  Количество состояний: {len(sticker.states)}")

        # Если есть стикеры, используем первый для примеров
        if stickers_list:
            sticker_id = stickers_list[0].id

            # Получение стикера по ID
            sticker_data = client.sprint_stickers.get(sticker_id)
            sticker_model = SprintSticker(**sticker_data)
            print(f"\nПолучен стикер спринта: {sticker_model.name}")
            if sticker_model.states:
                print(f"Состояния:")
                for state in sticker_model.states:
                    print(f"  - {state.get('name')} (ID: {state.get('id')})")

    except Exception as e:
        print(f"Ошибка при работе со стикерами спринта: {e}")

    # Создание нового стикера спринта с использованием модели
    try:
        # Создаем экземпляр модели с минимальными необходимыми состояниями
        new_sticker_model = SprintSticker(
            name="Новый стикер спринта",
            states=[
                {"name": "Состояние 1", "color": "#FF5733"},
                {"name": "Состояние 2", "color": "#33FF57"}
            ]
        )

        # Преобразуем модель в словарь для API запроса
        new_sticker_data = new_sticker_model.dict(by_alias=True, exclude_none=True)

        # Отправляем запрос на создание
        created_sticker_data = client.sprint_stickers.create(**new_sticker_data)

        # Преобразуем ответ в модель
        created_sticker = SprintSticker(**created_sticker_data)
        print(f"Создан новый стикер спринта: {created_sticker.name} (ID: {created_sticker.id})")
        print(f"Созданные состояния:")
        for state in created_sticker.states:
            print(f"  - {state.get('name')} (ID: {state.get('id')})")

        # Обновление стикера с использованием модели
        created_sticker.name = "Обновленный стикер спринта"
        updated_data = created_sticker.dict(by_alias=True, exclude_none=True)

        updated_sticker_data = client.sprint_stickers.update(
            id=created_sticker.id,
            **updated_data
        )

        updated_sticker = SprintSticker(**updated_sticker_data)
        print(f"Стикер спринта обновлен: {updated_sticker.name}")

        # Удаление стикера (через обновление поля deleted)
        updated_sticker.deleted = True
        delete_data = updated_sticker.dict(by_alias=True, exclude_none=True)

        deleted_sticker_data = client.sprint_stickers.update(
            id=updated_sticker.id,
            **delete_data
        )

        deleted_sticker = SprintSticker(**deleted_sticker_data)
        print(f"Стикер спринта удален: {deleted_sticker.name} (Удален: {deleted_sticker.deleted})")

    except Exception as e:
        print(f"Ошибка при работе со стикером спринта: {e}")


if __name__ == "__main__":
    # Создание клиента
    client = YouGileClient()

    # Примеры аутентификации
    auth_examples(client)

    # Примеры работы с сотрудниками
    employees_examples(client)
    #
    # # Примеры работы с проектами
    # projects_examples(client)
    #
    # # Примеры работы с ролями проекта
    # project_roles_examples(client)
    #
    # # Примеры работы с отделами
    # departments_examples(client)
    #
    # # Примеры работы с досками
    # boards_examples(client)
    #
    # # Примеры работы с колонками
    # columns_examples(client)
    #
    # # Примеры работы с задачами
    # tasks_examples(client)
    #
    # # Примеры работы со строковыми стикерами
    # string_stickers_examples(client)
    #
    # # Примеры работы со стикерами спринта
    # sprint_stickers_examples(client)
