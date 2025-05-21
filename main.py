from schedule_parser.ScheduleParser import MPEIRuzParser
from schedule_analyzer.ScheduleAnalyzer import ScheduleAnalyzer
from yougile_api.YouGileRestAPI import YouGileRestAPI
import datetime
import json

# Загрузка расписаний из JSON-файлов
def load_schedule(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    ## Пример парсинга расписания для учебной группы Аэ-21-21
    # Создание экземпляра парсера
    parser = MPEIRuzParser(
        headless=False,  # Запуск парсинга в видимом/невидимом режиме
        cleanup_files=True,  # Очистить/Сохранять вспомогательные файлы
    )

    try:
        # Парсинг расписания для группы
        schedule = parser.parse(
            name="Аэ-21-21",
            schedule_type="group",
            save_to_file=True,
            filename="data/json_schedules/schedule_group_Ae-21-21.json"
        )

        # Обработка результатов
        if schedule:
            print(f"Успешно получено расписание. Количество дней: {len(schedule)}")
        else:
            print("Не удалось получить расписание")
    finally:
        # Закрываем браузер
        parser.close()


    ## Пример обработки расписания
    # Загружаем расписания
    schedule1 = load_schedule('data/json_schedules/schedule_group_ER-03-23.json')
    schedule2 = load_schedule('data/json_schedules/schedule_group_ER-03-24.json')

    # Создаем анализатор расписаний
    analyzer = ScheduleAnalyzer([schedule1, schedule2], year=2025)

    # Алгоритм 1: Поиск ближайшего окна заданной ширины
    # Поиск окна шириной 2 часа
    window = analyzer.find_nearest_window_by_width(
        width_minutes=120,  # Ширина окна в минутах
        start_date=datetime.date.today(),  # Дата начала поиска
        schedule_index=0,  # Индекс расписания
        include_weekends=False,  # Учитывать ли выходные
        include_holidays=False,  # Учитывать ли праздники
        deadline=datetime.date(2025, 5, 31),  # Крайний срок
        min_start_hour=9,  # Минимальное время начала (час)
        max_end_hour=20  # Максимальное время окончания (час)
    )

    if window:
        print(f"Окно найдено: {window['date']}, {window['start_time']} - {window['end_time']}")

    else:
        print("Окно не найдено")

    # Алгоритм 2: Поиск ближайшего окна заданной ширины и длины
    # Поиск окна шириной 2 часа (120 минут) на протяжении 2 дней
    window = analyzer.find_nearest_window_by_width_and_length(
        width_minutes=120,
        days_count=2,
        start_date=datetime.date(2025, 4, 21),  # Дата начала поиска (опционально)
        schedule_index=0,  # Индекс расписания в списке (опционально)
        include_weekends=True,  # Учитывать ли выходные дни (опционально)
        include_holidays=False,  # Учитывать ли праздничные дни (опционально)
        deadline=datetime.date(2025, 5, 2),  # Крайний срок (опционально)
        max_days_to_check=30,  # Максимальное количество дней для проверки (опционально)
        min_start_hour=9,  # Минимальное время начала (час)
        max_end_hour=20  # Максимальное время окончания (час)
    )

    if window:
        print(f"Найдено окно:")
        print(f"Дата начала: {window['start_date']}")
        print(f"Дата окончания: {window['end_date']}")
        print(f"Количество дней: {window['days_count']}")
        print(f"Ширина окна: {window['width_minutes']} минут")
        print("Детали по дням:")
        for i, day_window in enumerate(window['windows']):
            print(f"  День {i + 1}: {day_window['date']}, {day_window['start_time']} - {day_window['end_time']}")
    else:
        print("Окно не найдено")

    # Алгоритм 3: Поиск окна заданного объема
    # Поиск окна общим объемом 10 часов (600 минут)
    window = analyzer.find_window_by_volume(
        total_minutes=600,
        min_width_minutes=90,  # Минимальная ширина окна (опционально)
        start_date=datetime.date(2025, 4, 21),  # Дата начала поиска (опционально)
        schedule_index=0,  # Индекс расписания в списке (опционально)
        include_weekends=True,  # Учитывать ли выходные дни (опционально)
        include_holidays=False,  # Учитывать ли праздничные дни (опционально)
        deadline=datetime.date(2025, 5, 2),  # Крайний срок (опционально)
        max_days_to_check=30,  # Максимальное количество дней для проверки (опционально)
        min_start_hour=9,  # Минимальное время начала (час)
        max_end_hour=20  # Максимальное время окончания (час)
    )

    if window:
        print(f"Найдено окно:")
        print(f"Общий объем: {window['total_minutes']} минут")
        print(f"Количество дней: {window['days_count']}")
        print("Детали по окнам:")
        for i, day_window in enumerate(window['windows']):
            print(
                f"  Окно {i + 1}: {day_window['date']}, {day_window['start_time']} - {day_window['end_time']}, {day_window['duration_minutes']} минут")
    else:
        print("Окно не найдено")

    # Алгоритм 4: Поиск окна, одновременно доступного у нескольких людей
    # Поиск общего окна шириной 2 часа (120 минут)
    window = analyzer.find_common_window_for_multiple_schedules(
        width_minutes=120,
        schedule_indices=[0, 1],  # Индексы расписаний (опционально)
        start_date=datetime.date(2025, 4, 21),  # Дата начала поиска (опционально)
        include_weekends=True,  # Учитывать ли выходные дни (опционально)
        include_holidays=False,  # Учитывать ли праздничные дни (опционально)
        deadline=datetime.date(2025, 5, 2),  # Крайний срок (опционально)
        max_days_to_check=30,  # Максимальное количество дней для проверки (опционально)
        min_start_hour=9,  # Минимальное время начала (час)
        max_end_hour=20  # Максимальное время окончания (час)
    )

    if window:
        print(f"Найдено общее окно:")
        print(f"Дата: {window['date']}")
        print(f"Время начала: {window['start_time']}")
        print(f"Время окончания: {window['end_time']}")
        print(f"Продолжительность: {window['duration_minutes']} минут")
        print(f"Количество участников: {window['participants_count']}")
    else:
        print("Общее окно не найдено")

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