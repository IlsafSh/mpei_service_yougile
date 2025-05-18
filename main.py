from schedule_parser.ScheduleParser import MPEIRuzParser
from yougile_api.YouGileRestAPI import YouGileRestAPI


def main():
    ## Пример парсинга расписания для учебной группы Аэ-21-21
    # Создание экземпляра парсера
    parser = MPEIRuzParser(
        headless=False,  # Запуск парсинга в видимом/невидимом режиме
        cleanup_files=False,  # Очистить/Сохранять вспомогательные файлы
    )

    try:
        # Парсинг расписания для группы
        schedule = parser.parse(
            name="Аэ-21-21",
            schedule_type="group",
            save_to_file=True,
            filename="schedule_group_Ae-21-21.json"
        )

        # Обработка результатов
        if schedule:
            print(f"Успешно получено расписание. Количество дней: {len(schedule)}")
        else:
            print("Не удалось получить расписание")
    finally:
        # Закрываем браузер
        parser.close()


    ## Пример обращения к YouGile API
    login = "some@example.com"
    password = "topsecret"

    api = YouGileRestAPI()

    # Авторизация и получение списка компаний
    companies = api.get_companies(login=login, password=password)
    print(f"List of companies: {companies}")
    id_mpei_company = companies[0].get('id') # ID компании
    #id_test_company = companies[1].get('id')
    keys = api.get_keys(login, password, id_mpei_company)
    print(f"List of keys: {keys}")
    token = keys[0].get('key')  # Берём первый ключ авторизации
    print(f"Authorization token: {token}")

    users = api.get_users(token)
    adminId = users[0].get('id')
    print(users)

    projects = api.get_projects(token)
    print(projects)

    tasks = api.get_tasks(token)
    print(tasks)

    revtasks = api.get_tasks_reverse(token)
    print(revtasks)


    ## Пример создания нового проекта в YouGile
    # project_title = "MPEI Schedule Project"
    # users = [{adminId: "admin"}]  # Можно добавить пользователей, если необходимо
    # new_project = yougile.create_project(token, project_title, users[0])
    # project_id = new_project.get('id')
    # print(f"Created project: {new_project}")
    #
    # # Создание доски в проекте
    # board_title = "Schedule Board"
    # stickers = {"deadline": True, "stopwatch": True, "assignee": True, "custom": {}}
    # new_board = yougile.create_board(token, board_title, project_id, stickers)
    # board_id = new_board.get('id')
    # print(f"Created board: {new_board}")
    #
    # # Создание колонки на доске
    # column_title = "Upcoming Tasks"
    # column_color = 10  # #EB3737 - Красный цвет
    # new_column = yougile.create_column(token, column_title, column_color, board_id)
    # column_id = new_column.get('id')
    # print(f"Created column: {new_column}")
    #
    # # Создание задачи в колонке
    # task_title = "First Task"
    # subtasks = []  # Список подзадач
    # assigned = []  # ID пользователей, которым назначена задача
    # deadline = None  # Дедлайн задачи
    # time_tracking = None  # Тайм-трекинг
    # checklists = []  # Чек-листы
    # stickers = {}  # Стикеры
    #
    # new_task = yougile.create_task(
    #     token,
    #     task_title,
    #     column_id,
    #     subtasks,
    #     assigned,
    #     deadline,
    #     time_tracking,
    #     checklists,
    #     stickers,
    #     description="Task created automatically for the project.",
    # )
    # print(f"Created task: {new_task}")

if __name__ == "__main__":
    main()