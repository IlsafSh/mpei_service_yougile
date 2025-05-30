"""
------------------------------------------------------------
ScheduleAnalyzer - Обновленный пример использования
------------------------------------------------------------
Примеры использования алгоритмов анализа расписания
------------------------------------------------------------
"""

from schedule_analyzer.ScheduleAnalyzer import ScheduleAnalyzer
import json
import datetime

# Загрузка расписаний из JSON-файлов
def load_schedule(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    ## Пример обработки расписания
    # Загружаем расписания
    schedule1 = load_schedule('../data/json_schedules/schedule_group_ER-03-23.json')
    schedule2 = load_schedule('../data/json_schedules/schedule_group_ER-03-24.json')

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


if __name__ == "__main__":
    main()