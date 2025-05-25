"""
------------------------------------------------------------
MPEIRuzParser - Обновленный пример использования
------------------------------------------------------------
Пример использования класса для парсинга расписания
------------------------------------------------------------
"""

from schedule_parser.ScheduleParser import MPEIRuzParser
import logging
import sys
import json

# Загрузка расписаний из JSON-файлов
def load_schedule(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    ## Пример парсинга расписания для учебной группы Аэ-21-21
    # Создание экземпляра парсера
    parser = MPEIRuzParser(
        headless=True,  # Запуск парсинга в видимом/невидимом режиме
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

if __name__ == "__main__":
    main()