from ScheduleParser import ScheduleParser
from YouGileRestAPI import YouGileRestAPI

def main():
    group = 'Аэ-21-21'
    url = f"https://bars.mpei.ru/bars_web/Open/RUZ/Timetable?rt=3&name={group}"

    # Создание экземпляра парсера
    parser = ScheduleParser(url)
    # Парсинг расписания
    schedule = parser.parse()
    # Вывод расписания
    parser.display_schedule()


    login = "some@example.com"
    password = "topsecret"

    yougile = YouGileRestAPI()

    # Авторизация и получение списка компаний
    companies = yougile.get_companies(login, password)
    print(f"List of companies: {companies}")

    id_mpei_company = companies[0].get('id') # ID компании
    #id_test_company = companies[1].get('id')
    keys = yougile.get_keys(login, password, id_mpei_company)
    print(f"List of keys: {keys}")
    token = keys[0].get('key')  # Берём первый ключ авторизации
    print(f"Authorization token: {token}")

    users = yougile.get_users(token)
    adminId = users[0].get('id')

    # Создание нового проекта
    project_title = "MPEI Schedule Project"
    users = [{adminId: "admin"}]  # Можно добавить пользователей, если необходимо
    new_project = yougile.create_project(token, project_title, users[0])
    project_id = new_project.get('id')
    print(f"Created project: {new_project}")

    # Создание доски в проекте
    board_title = "Schedule Board"
    stickers = {"deadline": True, "stopwatch": True, "assignee": True, "custom": {}}
    new_board = yougile.create_board(token, board_title, project_id, stickers)
    board_id = new_board.get('id')
    print(f"Created board: {new_board}")

    # Создание колонки на доске
    column_title = "Upcoming Tasks"
    column_color = 10  # #EB3737 - Красный цвет
    new_column = yougile.create_column(token, column_title, column_color, board_id)
    column_id = new_column.get('id')
    print(f"Created column: {new_column}")

    # Создание задачи в колонке
    task_title = "First Task"
    subtasks = []  # Список подзадач
    assigned = []  # ID пользователей, которым назначена задача
    deadline = None  # Дедлайн задачи
    time_tracking = None  # Тайм-трекинг
    checklists = []  # Чек-листы
    stickers = {}  # Стикеры

    new_task = yougile.create_task(
        token,
        task_title,
        column_id,
        subtasks,
        assigned,
        deadline,
        time_tracking,
        checklists,
        stickers,
        description="Task created automatically for the project.",
    )
    print(f"Created task: {new_task}")

if __name__ == "__main__":
    main()