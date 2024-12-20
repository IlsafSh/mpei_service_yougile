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
    id_mpei_company = "id_mpei_company"

    yougile = YouGileRestAPI()

    keys = yougile.get_keys(login, password, id_mpei_company)
    print(keys)
    projects = yougile.get_projects(keys[0].get('key'))
    print(projects)
    print(yougile.get_boards(keys[0].get('key')))
    print(yougile.get_columns(keys[0].get('key')))
    print(yougile.get_tasks(keys[0].get('key')))

if __name__ == "__main__":
    main()