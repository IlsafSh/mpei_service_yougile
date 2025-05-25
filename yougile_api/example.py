"""
------------------------------------------------------------
YouGile API Client - Обновленный пример использования
------------------------------------------------------------
Примеры использования библиотеки для работы с REST API YouGile v2.0

Документация API: https://ru.yougile.com/api-v2#/
------------------------------------------------------------
"""

from yougile_api import YouGileRestAPI


def main():
    ## Пример обращения к YouGile API
    login = "some@example.com"
    password = "topsecret"

    api = YouGileRestAPI()

    try:
        # Авторизация и получение списка компаний
        companies = api.get_companies(login=login, password=password)
        print(f"List of companies: {companies}")
        id_mpei_company = companies[0].get('id')  # ID компании

        keys = api.get_keys(login, password, id_mpei_company)
        print(f"List of keys: {keys}")
        token = keys[0].get('key')  # Берём первый ключ авторизации
        print(f"Authorization token: {token}")

        # Получение списка пользователей
        users = api.get_users(token)
        adminId = users[0].get('id')
        print(users)

        # Получение списка проектов
        projects = api.get_projects(token)
        print(projects)

        # Получение списка задач
        tasks = api.get_tasks(token)
        print(tasks)

        # Пример создания нового проекта в YouGile
        project_title = "MPEI Schedule Project"
        users_dict = {adminId: "admin"}  # Словарь с ID пользователей и их ролями
        new_project = api.create_project(token, project_title, users_dict)
        project_id = new_project.get('id')
        print(f"Created project: {new_project}")

        # Создание доски в проекте
        board_title = "Schedule Board"
        stickers = {"deadline": True, "stopwatch": True, "assignee": True, "custom": {}}
        new_board = api.create_board(token, board_title, project_id, stickers)
        board_id = new_board.get('id')
        print(f"Created board: {new_board}")

        # Создание колонки на доске
        column_title = "Upcoming Tasks"
        column_color = 10  # #EB3737 - Красный цвет (числовое значение)
        new_column = api.create_column(token, column_title, column_color, board_id)
        column_id = new_column.get('id')
        print(f"Created column: {new_column}")

        # Создание задачи в колонке
        task_title = "First Task"
        subtasks = []  # Список ID подзадач (строковые значения)
        assigned = []  # Список ID пользователей (строковые значения)

        new_task = api.create_task(
            token,
            title=task_title,
            columnId=column_id,
            description="Task created automatically for the project.",
            archived=False,
            completed=False,
            subtasks=subtasks,
            assigned=assigned,
            deadline=None,
            timeTracking=None,
            checklists=[],
            stickers={},
        )
        print(f"Created task: {new_task}")

        # Обновление задачи
        task_id = new_task.get('id')
        updated_task = api.change_task(
            token,
            taskId=task_id,
            title="Обновленная задача - Изменена через API",
            description="Это описание было добавлено через API с использованием pydantic",
            completed=True
        )
        print(f"Updated task: {updated_task}")

    except Exception as e:
        print(f"Ошибка API: {e}")


if __name__ == "__main__":
    main()
