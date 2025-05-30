"""
Тестирование модуля переноса расписания в YouGile.
"""

import os
import sys
import json
from yougile_api_wrapper.yougile_api import YouGileClient
from schedule_to_yougile import ScheduleToYouGile

def test_schedule_transfer():
    """
    Тестирование переноса расписания в YouGile.
    """
    # Параметры для тестирования
    login = "parov.duvel@mail.ru"  # Замените на реальные данные
    password = "pavel123"  # Замените на реальные данные
    schedule_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/json_schedules/schedule_group_Ae-21-21.json")
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

if __name__ == "__main__":
    test_schedule_transfer()
