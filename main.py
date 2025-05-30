"""
Пример последовательного использования модулей:
1. schedule_parser - парсинг расписания учебной группы Аэ-21-21
2. schedule_to_yougile - перенос расписания в YouGile
3. yougile_to_schedule - получение расписания из YouGile
4. schedule_analyzer - поиск окон с помощью четырех реализованных алгоритмов
"""

import os
import sys
import json
import datetime
from typing import Dict, List, Any

# Импорт модулей проекта
from schedule_parser.ScheduleParser import MPEIRuzParser
from schedule_to_yougile.schedule_to_yougile import ScheduleToYouGile
from yougile_to_schedule.yougile_to_schedule import YouGileToSchedule
from schedule_analyzer.ScheduleAnalyzer import ScheduleAnalyzer
from yougile_api_wrapper.yougile_api import YouGileClient

# Загрузка расписаний из JSON-файлов
def load_schedule(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """
    Основная функция, демонстрирующая последовательное использование всех модулей.
    """
    # Определение путей к файлам
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_root, "data")
    json_schedules_dir = os.path.join(data_dir, "json_schedules")

    # Создаем директории, если они не существуют
    os.makedirs(json_schedules_dir, exist_ok=True)

    # Путь к файлу с расписанием
    schedule_file = os.path.join(json_schedules_dir, "schedule_group_Ae-21-21.json")

    # Шаг 1: Парсинг расписания с помощью schedule_parser
    print("Шаг 1: Парсинг расписания группы Аэ-21-21")

    # Инициализация парсера
    parser = MPEIRuzParser(headless=True, max_weeks=16)

    try:
        # Парсинг расписания группы Аэ-21-21
        schedule = parser.parse("Аэ-21-21", MPEIRuzParser.TYPE_GROUP, save_to_file=True, filename=schedule_file)
        print(f"Расписание успешно получено и сохранено в {schedule_file}")
        print(f"Количество дней в расписании: {len(schedule)}")
    except Exception as e:
        print(f"Ошибка при парсинге расписания: {e}")
    finally:
        # Закрываем парсер
        parser.close()

    # Шаг 2: Перенос расписания в YouGile с помощью schedule_to_yougile
    print("\nШаг 2: Перенос расписания в YouGile")

    # Параметры для тестирования
    login = "parov.duvel@mail.ru"  # Замените на реальные данные
    password = "pavel123"  # Замените на реальные данные
    schedule_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "data/json_schedules/schedule_group_Ae-21-21.json")
    project_title = "Расписание группы Ae-21-21 (тест)"

    # Инициализация клиента YouGile
    client = YouGileClient()

    # Аутентификация
    print("Аутентификация...")
    companies_response = client.auth.get_companies(login=login, password=password)

    if not companies_response or 'content' not in companies_response:
        print("Ошибка аутентификации: не удалось получить список компаний")
        return

    companies = companies_response['content']
    if not companies:
        print("Ошибка аутентификации: список компаний пуст")
        return

    id_company = companies[0].get('id')
    keys_response = client.auth.get_keys(login, password, id_company)

    if not keys_response:
        print("Ошибка аутентификации: не удалось получить ключи")
        return

    token = keys_response[0].get('key')
    if not token:
        print("Ошибка аутентификации: не удалось получить токен")
        return

    client.set_token(token)
    print(f"Аутентификация успешна. Токен: {token}")

    # Получение ID администратора (текущего пользователя)
    print("Получение данных пользователя...")
    employees_response = client.employees.list(limit=1)

    if not employees_response or 'content' not in employees_response:
        print("Ошибка: не удалось получить список сотрудников")
        return

    employees = employees_response['content']
    if not employees:
        print("Ошибка: список сотрудников пуст")
        return

    admin_id = employees[0].get('id')
    print(f"ID администратора: {admin_id}")

    # Инициализация модуля переноса расписания
    schedule_to_yougile = ScheduleToYouGile(client)

    # Перенос расписания
    print(f"Перенос расписания из файла {schedule_file}...")
    try:
        result = schedule_to_yougile.transfer_schedule(schedule_file, project_title, admin_id)
        print("Результат переноса расписания:")
        print(json.dumps(result, indent=2))
        print(f"Проект создан с ID: {result.get('project_id')}")
        print(f"Доска создана с ID: {result.get('board_id')}")
        print(f"Создано колонок: {len(result.get('column_ids', {}))}")
        print(f"Создано задач: {result.get('task_count', 0)}")
        print("Тестирование успешно завершено!")
    except Exception as e:
        print(f"Ошибка при переносе расписания: {e}")

    # Шаг 3: Получение расписания из YouGile с помощью yougile_to_schedule
    print("\nШаг 3: Получение расписания из YouGile")

    # Параметры для тестирования
    api_key = "GFirZ4HXKFfw2KXg8ux+ewOXOMXf5vvXDaJnV-37POdMDoW-m6OyPo2rHW6DXyj9"  # Токен из примера пользователя
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mpei_service_yougile/data/json_schedules/exported_schedule.json")

    try:
        # Аутентификация
        print("Аутентификация...")
        client = YouGileClient()

        # Используем API ключ для аутентификации
        client.set_token(api_key)
        print(f"Аутентификация успешна. Токен: {api_key}")

        # Создаем экземпляр класса для экспорта расписания
        yougile_to_schedule = YouGileToSchedule(client)

        # Получаем список проектов
        print("Получение списка проектов...")
        projects = yougile_to_schedule.list_projects()

        print("\nДоступные проекты:")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.get('title')} (ID: {project.get('id')})")

        # Выбираем проект с расписанием
        project_id = None
        for project in projects:
            if "расписание" in project.get('title', '').lower():
                project_id = project.get('id')
                print(f"\nИспользуем проект: {project.get('title')} (ID: {project_id})")
                break

        if not project_id:
            # Если проект с "расписание" в названии не найден, используем первый проект
            project_id = projects[0].get('id')
            print(f"\nИспользуем проект: {projects[0].get('title')} (ID: {project_id})")

        # Экспорт расписания
        schedule = yougile_to_schedule.export_schedule(project_id=project_id, output_file=output_file)

        # Вывод результатов
        print("\nЭкспорт расписания завершен")
        print(f"Количество дней в расписании: {len(schedule)}")
        print(f"Расписание сохранено в файл: {output_file}")

        # Выводим пример первого дня расписания
        if schedule:
            first_day = schedule[0]
            print(f"\nПример первого дня расписания:")
            print(f"День: {first_day.get('day')}")
            print(f"Неделя: {first_day.get('week')}")
            print(f"Количество занятий: {len(first_day.get('lessons', []))}")

            # Выводим пример первого занятия
            if first_day.get('lessons'):
                first_lesson = first_day['lessons'][0]
                print(f"\nПример первого занятия:")
                print(f"Предмет: {first_lesson.get('subject')}")
                print(f"Время: {first_lesson.get('time')}")
                print(f"Тип: {first_lesson.get('type')}")
                print(f"Аудитория: {first_lesson.get('room')}")
                print(f"Преподаватель: {first_lesson.get('teacher')}")

    except Exception as e:
        print(f"Ошибка при экспорте расписания: {e}")

    # Шаг 4: Анализ расписания с помощью schedule_analyzer
    print("\nШаг 4: Анализ расписания на окна")

    try:
        # Загружаем расписания
        schedule1 = load_schedule(output_file)
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

    except Exception as e:
        print(f"Ошибка при анализе расписания: {e}")

    print("\nПример последовательного использования всех модулей завершен")