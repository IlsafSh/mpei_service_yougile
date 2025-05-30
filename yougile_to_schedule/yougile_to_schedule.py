"""
Модуль для обратного переноса расписания из YouGile в JSON формат.
"""

import json
import re
import time
import random
import datetime
from typing import Dict, List, Any, Optional, Tuple


class YouGileToSchedule:
    """
    Класс для обратного переноса расписания из YouGile в JSON формат.
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
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.column_week_map = {}  # Словарь для хранения соответствия ID колонок и номеров недель
        
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
    
    def _map_columns_to_weeks(self, board_id: str) -> Dict[str, int]:
        """
        Создание соответствия между колонками и номерами недель.
        Извлекает номер недели из названия колонки.
        
        Args:
            board_id: ID доски
            
        Returns:
            Dict[str, int]: Словарь соответствия колонок и недель
        """
        # Получаем все колонки доски
        columns_response = self._api_call_with_retry(
            self.client.columns.list,
            board_id=board_id,
            limit=100
        )
        
        columns = columns_response.get('content', [])
        column_week_map = {}
        
        # Создаем соответствие между колонками и неделями
        # Извлекаем номер недели из названия колонки
        for column in columns:
            column_id = column.get('id')
            column_title = column.get('title', '')
            
            # Пытаемся извлечь номер недели из названия колонки
            week_number = 0  # По умолчанию неделя 0
            
            # Проверяем разные форматы названий колонок
            week_patterns = [
                r'неделя\s+(\d+)',  # "Неделя 1", "неделя 2" и т.д.
                r'нед\.\s*(\d+)',   # "Нед. 1", "нед.2" и т.д.
                r'нед\s+(\d+)',     # "Нед 1", "нед 2" и т.д.
                r'н\s*(\d+)',       # "Н 1", "н2" и т.д.
                r'(\d+)\s*неделя',  # "1 неделя", "2 неделя" и т.д.
                r'(\d+)\s*нед',     # "1 нед", "2 нед" и т.д.
                r'(\d+)\s*н',       # "1 н", "2 н" и т.д.
                r'week\s*(\d+)',    # "Week 1", "week 2" и т.д.
                r'w\s*(\d+)',       # "W 1", "w2" и т.д.
                r'(\d+)'            # Просто число, как последний вариант
            ]
            
            # Проверяем название колонки на соответствие шаблонам
            for pattern in week_patterns:
                match = re.search(pattern, column_title.lower())
                if match:
                    try:
                        week_number = int(match.group(1))
                        break
                    except (ValueError, IndexError):
                        pass
            
            column_week_map[column_id] = week_number
            
            # Для отладки
            print(f"Колонка '{column_title}' соответствует неделе {week_number}")
        
        self.column_week_map = column_week_map
        return column_week_map
    
    def _get_tasks_from_board(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Получение всех задач с доски.
        
        Args:
            board_id: ID доски
            
        Returns:
            List[Dict[str, Any]]: Список задач
        """
        all_tasks = []
        
        # Сначала получаем все колонки доски
        columns_response = self._api_call_with_retry(
            self.client.columns.list,
            board_id=board_id,
            limit=100
        )
        
        columns = columns_response.get('content', [])
        
        # Для каждой колонки получаем задачи
        for column in columns:
            column_id = column.get('id')
            offset = 0
            limit = 50  # Количество задач на страницу
            
            while True:
                # Получаем страницу задач для текущей колонки
                tasks_response = self._api_call_with_retry(
                    self.client.tasks.list,
                    column_id=column_id,
                    offset=offset,
                    limit=limit
                )
                
                tasks = tasks_response.get('content', [])
                
                # Если задач больше нет, переходим к следующей колонке
                if not tasks:
                    break
                    
                all_tasks.extend(tasks)
                offset += limit
                
                # Добавляем небольшую задержку между запросами
                time.sleep(random.uniform(0.5, 1.0))
        
        return all_tasks
    
    def _parse_task_description(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг описания задачи для извлечения параметров занятия.
        
        Args:
            task: Задача
            
        Returns:
            Dict[str, Any]: Словарь с параметрами занятия
        """
        title = task.get('title', '')
        description = task.get('description', '')
        column_id = task.get('column_id', '')
        
        # Извлекаем номер недели из колонки
        week = self.column_week_map.get(column_id, 0)
        
        # Извлекаем предмет и время из заголовка
        subject = title
        time_str = ''
        
        # Проверяем формат "Предмет (время)"
        subject_time_match = re.match(r'(.+?)\s*\((.+?)\)', title)
        if subject_time_match:
            subject = subject_time_match.group(1).strip()
            time_str = subject_time_match.group(2).strip()
            
            # Проверяем, является ли извлеченное время действительно временем
            # Если это не время в формате ЧЧ:ММ-ЧЧ:ММ, сохраняем как есть
            if not re.match(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', time_str):
                # Проверяем специальные значения
                if time_str.lower() not in ['по выбору', 'факультатив', 'по расписанию']:
                    # Если это не специальное значение и не формат времени, 
                    # возможно это часть названия предмета
                    subject = title
                    time_str = ''
        
        # Извлекаем параметры из описания
        lesson_type = ''
        room = ''
        teacher = ''
        date_str = ''
        start_time = ''
        end_time = ''
        
        # Поиск предмета в описании, если не найден в заголовке
        if subject == title:
            subject_patterns = [
                r'\*\*Предмет:\*\*\s*(.+?)(?:\n|$)',
                r'\*\*Название:\*\*\s*(.+?)(?:\n|$)',
                r'\*\*Дисциплина:\*\*\s*(.+?)(?:\n|$)'
            ]
            for pattern in subject_patterns:
                subject_match = re.search(pattern, description)
                if subject_match:
                    subject = subject_match.group(1).strip()
                    # Проверяем, есть ли в названии предмета скобки с временем
                    subject_time_match = re.match(r'(.+?)\s*\((.+?)\)', subject)
                    if subject_time_match:
                        potential_subject = subject_time_match.group(1).strip()
                        potential_time = subject_time_match.group(2).strip()
                        # Проверяем, является ли содержимое скобок временем или специальным значением
                        if re.match(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', potential_time) or \
                           potential_time.lower() in ['по выбору', 'факультатив', 'по расписанию']:
                            subject = potential_subject
                            time_str = potential_time
                    break
        
        # Поиск типа занятия
        type_patterns = [
            r'\*\*Тип занятия:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Тип:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Вид занятия:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in type_patterns:
            type_match = re.search(pattern, description)
            if type_match:
                lesson_type = type_match.group(1).strip()
                break
        
        # Поиск аудитории
        room_patterns = [
            r'\*\*Аудитория:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Место:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Кабинет:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Помещение:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in room_patterns:
            room_match = re.search(pattern, description)
            if room_match:
                room = room_match.group(1).strip()
                break
        
        # Поиск преподавателя
        teacher_patterns = [
            r'\*\*Преподаватель:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Учитель:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Лектор:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Ведущий:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in teacher_patterns:
            teacher_match = re.search(pattern, description)
            if teacher_match:
                teacher = teacher_match.group(1).strip()
                break
        
        # Поиск времени начала и окончания
        start_time_patterns = [
            r'\*\*Время начала:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Начало:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in start_time_patterns:
            start_time_match = re.search(pattern, description)
            if start_time_match:
                start_time = start_time_match.group(1).strip()
                break
        
        end_time_patterns = [
            r'\*\*Время окончания:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Окончание:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Конец:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in end_time_patterns:
            end_time_match = re.search(pattern, description)
            if end_time_match:
                end_time = end_time_match.group(1).strip()
                break
        
        # Если найдены время начала и окончания, формируем строку времени
        if start_time and end_time and not time_str:
            time_str = f"{start_time}-{end_time}"
        
        # Поиск даты
        date_patterns = [
            r'\*\*Дата:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*День:\*\*\s*(.+?)(?:\n|$)'
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, description)
            if date_match:
                date_str = date_match.group(1).strip()
                break
        
        # Если время не извлечено из заголовка или из времени начала/окончания, ищем в описании
        if not time_str:
            # Проверяем разные форматы времени в описании
            time_patterns = [
                r'\*\*Время:\*\*\s*(.+?)(?:\n|$)',
                r'\*\*Расписание:\*\*\s*(.+?)(?:\n|$)'
            ]
            
            for pattern in time_patterns:
                time_match = re.search(pattern, description)
                if time_match:
                    time_value = time_match.group(1).strip()
                    
                    # Проверяем формат "XX:XX-YY:YY"
                    if '-' in time_value and re.search(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', time_value):
                        time_str = time_value
                        break
                    # Проверяем специальные значения
                    elif time_value.lower() in ['по выбору', 'факультатив', 'по расписанию']:
                        time_str = time_value.lower()
                        break
            
            # Если время все еще не найдено, проверяем наличие специальных меток в описании
            if not time_str:
                special_time_patterns = [
                    r'по выбору',
                    r'факультатив',
                    r'по расписанию'
                ]
                
                for pattern in special_time_patterns:
                    if re.search(pattern, description.lower()):
                        time_str = pattern
                        break
        
        # Формируем день недели и дату
        day = ''
        if date_str:
            # Пробуем разные форматы даты
            try:
                # Пробуем ISO формат (YYYY-MM-DD)
                date_obj = datetime.date.fromisoformat(date_str)
                day_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][date_obj.weekday()]
                day_of_month = date_obj.day
                month_names = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
                              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
                month_name = month_names[date_obj.month - 1]
                day = f"{day_of_week}, {day_of_month} {month_name}"
            except (ValueError, IndexError):
                # Если не ISO формат, проверяем, может быть это уже в нужном формате
                day_match = re.match(r'([А-Я][а-я]), (\d+) ([а-я]+)', date_str)
                if day_match:
                    day = date_str
                else:
                    # Если не удалось распознать дату, используем текущую
                    try:
                        today = datetime.date.today()
                        day_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][today.weekday()]
                        day_of_month = today.day
                        month_names = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
                                      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
                        month_name = month_names[today.month - 1]
                        day = f"{day_of_week}, {day_of_month} {month_name}"
                        date_str = today.isoformat()
                    except:
                        pass
        
        # Формируем словарь с параметрами занятия
        lesson = {
            'time': time_str,
            'subject': subject,
            'type': lesson_type,
            'room': room,
            'teacher': teacher
        }
        
        return {
            'week': week,
            'day': day,
            'date_str': date_str,
            'lesson': lesson
        }
    
    def _group_tasks_by_day(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Группировка задач по дням.
        
        Args:
            tasks_data: Список данных задач
            
        Returns:
            List[Dict[str, Any]]: Список дней с занятиями
        """
        # Словарь для группировки занятий по дням
        days_dict = {}
        
        for task_data in tasks_data:
            week = task_data['week']
            day = task_data['day']
            date_str = task_data['date_str']
            lesson = task_data['lesson']
            
            # Если день еще не добавлен в словарь, создаем новую запись
            key = f"{date_str}_{day}"  # Используем дату и день как ключ для уникальности
            if key not in days_dict:
                days_dict[key] = {
                    'day': day,
                    'week': week,
                    'date_str': date_str,  # Сохраняем дату для сортировки
                    'lessons': []
                }
            
            # Добавляем занятие в список занятий для этого дня
            days_dict[key]['lessons'].append(lesson)
        
        # Преобразуем словарь в список
        days_list = list(days_dict.values())
        
        # Сортируем дни по дате
        days_list.sort(key=lambda x: x.get('date_str', '') or '')
        
        # Удаляем поле date_str из итогового результата, так как оно не нужно в JSON
        for day_data in days_list:
            if 'date_str' in day_data:
                del day_data['date_str']
        
        return days_list
    
    def export_schedule(self, project_id: str = None, board_id: str = None, output_file: str = None) -> List[Dict[str, Any]]:
        """
        Экспорт расписания из YouGile в JSON формат.
        
        Args:
            project_id: ID проекта (если не указан board_id)
            board_id: ID доски (если не указан project_id)
            output_file: Путь к файлу для сохранения расписания
            
        Returns:
            List[Dict[str, Any]]: Список дней с занятиями
        """
        if not board_id and not project_id:
            raise ValueError("Необходимо указать либо project_id, либо board_id")
        
        # Если указан только project_id, получаем доски проекта
        if not board_id:
            print(f"Получение досок из проекта {project_id}...")
            boards_response = self._api_call_with_retry(
                self.client.boards.list,
                project_id=project_id,
                limit=100
            )
            
            boards = boards_response.get('content', [])
            if not boards:
                raise ValueError(f"В проекте {project_id} не найдено досок")
            
            # Используем первую доску
            board_id = boards[0]['id']
            print(f"Используем доску {board_id}")
        
        # Создаем соответствие между колонками и неделями
        print(f"Получение колонок из доски {board_id}...")
        self._map_columns_to_weeks(board_id)
        
        # Получаем все задачи с доски
        print(f"Получение задач из доски {board_id}...")
        tasks = self._get_tasks_from_board(board_id)
        print(f"Получено задач: {len(tasks)}")
        
        # Парсим описания задач
        tasks_data = []
        for task in tasks:
            task_data = self._parse_task_description(task)
            tasks_data.append(task_data)
        
        # Группируем задачи по дням и сортируем по дате
        days = self._group_tasks_by_day(tasks_data)
        
        # Сохраняем расписание в файл, если указан путь
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(days, f, ensure_ascii=False, indent=4)
            print(f"Расписание сохранено в файл {output_file}")
        
        return days
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        Получение списка доступных проектов.
        
        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        projects_response = self._api_call_with_retry(
            self.client.projects.list,
            limit=100
        )
        
        projects = projects_response.get('content', [])
        return projects
