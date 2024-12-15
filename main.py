from ScheduleParser import ScheduleParser

def main():
    group = 'Аэ-21-21'
    url = f"https://bars.mpei.ru/bars_web/Open/RUZ/Timetable?rt=3&name={group}"

    # Создание экземпляра парсера
    parser = ScheduleParser(url)
    # Парсинг расписания
    schedule = parser.parse()
    # Вывод расписания
    parser.display_schedule()

if __name__ == "__main__":
    main()