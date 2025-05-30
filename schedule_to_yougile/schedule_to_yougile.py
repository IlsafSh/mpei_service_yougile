"""
Модуль для переноса учебного расписания из JSON формата в СУП YouGile.

Этот модуль обеспечивает функциональность для:
- Создания нового проекта в YouGile с участником-админом
- Создания колонок для каждой учебной недели (от 0 до 16)
- Добавления задач с параметрами занятий в описании
- Настройки корректного отображения времени начала и окончания занятий
"""

import json
import datetime
import time
import random
from typing import Dict, List, Any, Optional, Tuple


class ScheduleToYouGile:
    """
    Класс для переноса учебного расписания из JSON формата в СУП YouGile.
    """

    def __init__(self, client, max_retries=5, base_delay=2, max_delay=30):
        """
        Инициализация класса.

        Args:
            client: Экземпляр клиента YouGile API
            max_retries: Максимальное количество повторных попыток при ошибке API
            base_delay: Базовая задержка между запросами в секундах
            max_delay: Максимальная задержка между запросами в секундах
        """
        self.client = client
        self.project_id = None
        self.board_id = None
        self.column_ids = {}  # Словарь для хранения ID колонок по номерам недель
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
    def _api_call_with_retry(self, api_method, *args, **kwargs):
        """
        Выполнение API-запроса с автоматическими повторами при ошибке Too Many Requests.
        
        Args:
            api_method: Метод API для вызова
            *args: Позиционные аргументы для метода API
            **kwargs: Именованные аргументы для метода API
            
        Returns:
            Результат выполнения API-запроса
            
        Raises:
            Exception: Если все попытки выполнения запроса завершились неудачно
        """
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                # Добавляем небольшую случайную задержку перед каждым запросом
                if retries > 0:
                    # Экспоненциальная задержка с случайным компонентом
                    delay = min(self.base_delay * (2 ** retries) + random.uniform(0, 1), self.max_delay)
                    print(f"Повторная попытка {retries}/{self.max_retries} через {delay:.2f} секунд...")
                    time.sleep(delay)
                
                return api_method(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                error_message = str(e)
                
                # Проверяем, является ли ошибка "Too Many Requests"
                if "Too Many Requests" in error_message or "429" in error_message:
                    retries += 1
                    print(f"Получена ошибка API: {error_message}")
                    if retries <= self.max_retries:
                        continue
                else:
                    # Если это другая ошибка, сразу выбрасываем исключение
                    raise
        
        # Если все попытки не удались, выбрасываем последнее исключение
        raise last_exception

    def create_project(self, title: str, admin_id: str) -> str:
        """
        Создание нового проекта с участником-админом.

        Args:
            title: Название проекта
            admin_id: ID администратора проекта

        Returns:
            str: ID созданного проекта
        """
        # Создаем проект с указанным админом
        users = {admin_id: "admin"}
        
        # Используем метод с повторами для создания проекта
        project = self._api_call_with_retry(
            self.client.projects.create,
            title=title,
            users=users
        )
        
        self.project_id = project.get('id')
        
        # Добавляем небольшую задержку между запросами
        time.sleep(random.uniform(0.5, 1.5))
        
        # Создаем доску для проекта с повторами
        board = self._api_call_with_retry(
            self.client.boards.create,
            title=title,
            project_id=self.project_id
        )
        
        self.board_id = board.get('id')
        
        return self.project_id

    def create_week_columns(self, max_week: int = 16) -> Dict[int, str]:
        """
        Создание колонок для каждой учебной недели.

        Args:
            max_week: Максимальный номер недели (по умолчанию 16)

        Returns:
            Dict[int, str]: Словарь с ID колонок по номерам недель
        """
        if not self.board_id:
            raise ValueError("Сначала необходимо создать проект и доску")
        
        # Создаем колонки для каждой недели
        for week in range(max_week + 1):
            # Используем метод с повторами для создания колонки
            column = self._api_call_with_retry(
                self.client.columns.create,
                title=f"Неделя {week}",
                board_id=self.board_id,
                color=week % 16 + 1  # Используем разные цвета для колонок
            )
            self.column_ids[week] = column.get('id')
            
            # Добавляем небольшую задержку между запросами
            time.sleep(random.uniform(0.5, 1.0))
        
        return self.column_ids

    def _parse_time(self, time_str: str) -> Tuple[datetime.time, datetime.time]:
        """
        Парсинг строки времени занятия в формате "HH:MM-HH:MM".

        Args:
            time_str: Строка времени в формате "HH:MM-HH:MM"

        Returns:
            Tuple[datetime.time, datetime.time]: Кортеж с временем начала и окончания
        """
        start_time_str, end_time_str = time_str.split('-')
        
        start_hour, start_minute = map(int, start_time_str.split(':'))
        end_hour, end_minute = map(int, end_time_str.split(':'))
        
        start_time = datetime.time(start_hour, start_minute)
        end_time = datetime.time(end_hour, end_minute)
        
        return start_time, end_time

    def _format_date(self, day_str: str) -> str:
        """
        Форматирование строки даты.

        Args:
            day_str: Строка даты в формате "Дн, DD месяца"

        Returns:
            str: Отформатированная дата в формате "YYYY-MM-DD"
        """
        # Получаем текущий год
        current_year = datetime.datetime.now().year
        
        # Парсим день и месяц из строки
        day_parts = day_str.split(', ')
        if len(day_parts) < 2:
            return None
        
        date_parts = day_parts[1].split(' ')
        if len(date_parts) < 2:
            return None
        
        day = int(date_parts[0])
        month_str = date_parts[1].lower()
        
        # Словарь соответствия названий месяцев их номерам
        month_map = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
        
        month = month_map.get(month_str, 1)  # По умолчанию январь, если месяц не распознан
        
        # Формируем дату
        date_obj = datetime.date(current_year, month, day)
        return date_obj.isoformat()

    def _create_task_description(self, lesson: Dict[str, str]) -> str:
        """
        Создание описания задачи на основе параметров занятия.

        Args:
            lesson: Словарь с параметрами занятия

        Returns:
            str: Описание задачи
        """
        description = f"**Предмет:** {lesson.get('subject', 'Не указан')}\n"
        description += f"**Тип занятия:** {lesson.get('type', 'Не указан')}\n"
        description += f"**Аудитория:** {lesson.get('room', 'Не указана')}\n"
        
        teacher = lesson.get('teacher', '')
        if teacher:
            description += f"**Преподаватель:** {teacher}\n"
        
        return description

    def create_tasks_from_schedule(self, schedule_data: List[Dict[str, Any]]) -> List[str]:
        """
        Создание задач на основе данных расписания.

        Args:
            schedule_data: Список с данными расписания

        Returns:
            List[str]: Список ID созданных задач
        """
        if not self.board_id or not self.column_ids:
            raise ValueError("Сначала необходимо создать проект, доску и колонки")
        
        task_ids = []
        
        for day_schedule in schedule_data:
            day = day_schedule.get('day', '')
            week = day_schedule.get('week', 0)
            lessons = day_schedule.get('lessons', [])
            
            # Получаем ID колонки для текущей недели
            column_id = self.column_ids.get(week)
            if not column_id:
                continue
            
            # Форматируем дату
            date_str = self._format_date(day)
            
            # Создаем задачи для каждого занятия
            for lesson in lessons:
                subject = lesson.get('subject', 'Занятие')
                time_str = lesson.get('time', '')
                
                # Создаем заголовок задачи
                title = f"{subject} ({time_str})"
                
                # Создаем описание задачи
                description = self._create_task_description(lesson)
                
                # Парсим время начала и окончания
                start_time, end_time = self._parse_time(time_str)
                
                # Формируем дату и время начала и окончания
                if date_str:
                    start_datetime = f"{date_str}T{start_time.strftime('%H:%M:%S')}"
                    end_datetime = f"{date_str}T{end_time.strftime('%H:%M:%S')}"
                    
                    # Добавляем информацию о времени в описание, так как API не поддерживает прямую передачу start_date/due_date
                    time_info = f"\n\n**Время начала:** {start_time.strftime('%H:%M')}\n"
                    time_info += f"**Время окончания:** {end_time.strftime('%H:%M')}\n"
                    time_info += f"**Дата:** {date_str}\n"
                    
                    # Используем метод с повторами для создания задачи
                    task = self._api_call_with_retry(
                        self.client.tasks.create,
                        title=title,
                        column_id=column_id,
                        description=description + time_info
                    )
                    
                    task_ids.append(task.get('id'))
                    
                    # Добавляем небольшую задержку между запросами
                    time.sleep(random.uniform(0.5, 1.5))
        
        return task_ids

    def transfer_schedule(self, schedule_file_path: str, project_title: str, admin_id: str) -> Dict[str, Any]:
        """
        Перенос расписания из JSON файла в YouGile.

        Args:
            schedule_file_path: Путь к файлу с расписанием в формате JSON
            project_title: Название проекта
            admin_id: ID администратора проекта

        Returns:
            Dict[str, Any]: Словарь с результатами переноса
        """
        # Загружаем данные расписания из файла
        with open(schedule_file_path, 'r', encoding='utf-8') as file:
            schedule_data = json.load(file)
        
        # Создаем проект
        project_id = self.create_project(project_title, admin_id)
        
        # Определяем максимальный номер недели в расписании
        max_week = 0
        for day_schedule in schedule_data:
            week = day_schedule.get('week', 0)
            max_week = max(max_week, week)
        
        # Создаем колонки для недель
        column_ids = self.create_week_columns(max_week)
        
        # Создаем задачи на основе расписания
        task_ids = self.create_tasks_from_schedule(schedule_data)
        
        # Формируем результат
        result = {
            'project_id': project_id,
            'board_id': self.board_id,
            'column_ids': column_ids,
            'task_count': len(task_ids),
            'max_week': max_week
        }
        
        return result
