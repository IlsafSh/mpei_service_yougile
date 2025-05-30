"""
Тестирование модуля обратного переноса расписания из YouGile в JSON формат.
"""

import os
import sys
import json

# Добавляем абсолютный путь к корню проекта для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from yougile_api_wrapper.yougile_api import YouGileClient

from yougile_to_schedule import YouGileToSchedule

def test_schedule_export():
    """
    Тестирование экспорта расписания из YouGile в JSON формат.
    """
    # Параметры для тестирования
    api_key = "GFirZ4HXKFfw2KXg8ux+ewOXOMXf5vvXDaJnV-37POdMDoW-m6OyPo2rHW6DXyj9"  # Токен из примера пользователя
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/json_schedules/exported_schedule.json")
    
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

if __name__ == "__main__":
    test_schedule_export()
