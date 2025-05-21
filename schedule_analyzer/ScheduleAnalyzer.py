import datetime
import copy
from typing import List, Dict, Tuple, Optional, Set, Union, Any
import holidays


class ScheduleAnalyzer:
    """
    Класс для анализа расписаний и поиска свободных окон.

    Поддерживает следующие алгоритмы:
    1. Поиск ближайшего окна заданной ширины
    2. Поиск ближайшего окна заданной ширины и длины
    3. Поиск окна заданного объема с минимизацией количества дней
    4. Поиск окна, одновременно доступного у нескольких людей

    Учитывает ограничения:
    - Раннее время начала (по умолчанию с 7 утра)
    - Позднее время завершения (по умолчанию до 23 часов)
    - Дедлайн (до определенной даты)
    - Учет выходных и праздничных дней
    """

    # Дни недели
    WEEKDAYS = {
        'Пн': 0, 'Вт': 1, 'Ср': 2, 'Чт': 3, 'Пт': 4, 'Сб': 5, 'Вс': 6
    }

    # Месяцы для преобразования дат
    MONTHS = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
        'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }

    def __init__(self, schedules: List[Dict] = None, year: int = None, country: str = 'RU',
                 custom_holidays: Set[Tuple[int, int]] = None):
        """
        Инициализация анализатора расписаний.

        Args:
            schedules (List[Dict], optional): Список расписаний для анализа.
            year (int, optional): Текущий год для корректной обработки дат.
                                 Если не указан, используется текущий год.
            country (str, optional): Код страны для определения праздников. По умолчанию 'RU'.
            custom_holidays (Set[Tuple[int, int]], optional): Пользовательский набор праздничных дней
                                                           в формате {(день, месяц), ...}.
        """
        self.schedules = schedules or []
        self.year = year or datetime.datetime.now().year

        # Инициализация праздников
        self.country = country
        self.holiday_calendar = holidays.country_holidays(country, years=self.year)

        # Пользовательские праздники
        self.custom_holidays = custom_holidays or set()

        # Кэш для хранения обработанных расписаний
        self._processed_schedules = {}

        # Кэш для хранения занятых временных интервалов
        self._busy_intervals = {}

    def add_schedule(self, schedule: List[Dict]) -> None:
        """
        Добавление расписания для анализа.

        Args:
            schedule (List[Dict]): Расписание в формате JSON.
        """
        if schedule:
            self.schedules.append(schedule)
            # Сбрасываем кэш при добавлении нового расписания
            self._processed_schedules = {}
            self._busy_intervals = {}

    def set_schedules(self, schedules: List[List[Dict]]) -> None:
        """
        Установка списка расписаний для анализа.

        Args:
            schedules (List[List[Dict]]): Список расписаний в формате JSON.
        """
        self.schedules = schedules
        # Сбрасываем кэш при установке новых расписаний
        self._processed_schedules = {}
        self._busy_intervals = {}

    def set_holiday_calendar(self, country: str = 'RU', years: Union[int, List[int]] = None) -> None:
        """
        Установка календаря праздников.

        Args:
            country (str, optional): Код страны для определения праздников. По умолчанию 'RU'.
            years (Union[int, List[int]], optional): Год или список лет для праздников.
                                                  Если не указан, используется текущий год.
        """
        if years is None:
            years = self.year

        self.country = country
        self.holiday_calendar = holidays.country_holidays(country, years=years)

    def add_custom_holiday(self, day: int, month: int) -> None:
        """
        Добавление пользовательского праздничного дня.

        Args:
            day (int): День месяца.
            month (int): Номер месяца.
        """
        self.custom_holidays.add((day, month))

    def set_custom_holidays(self, custom_holidays: Set[Tuple[int, int]]) -> None:
        """
        Установка пользовательского набора праздничных дней.

        Args:
            custom_holidays (Set[Tuple[int, int]]): Набор праздничных дней в формате {(день, месяц), ...}.
        """
        self.custom_holidays = custom_holidays

    def _parse_date(self, date_str: str) -> datetime.date:
        """
        Преобразование строки даты в объект datetime.date.

        Args:
            date_str (str): Строка с датой в формате "Пн, 17 февраля".

        Returns:
            datetime.date: Объект даты.
        """
        # Извлекаем день и месяц из строки
        parts = date_str.split(', ')
        if len(parts) != 2:
            raise ValueError(f"Неверный формат даты: {date_str}")

        day_month = parts[1].split()
        if len(day_month) != 2:
            raise ValueError(f"Неверный формат дня и месяца: {parts[1]}")

        day = int(day_month[0])
        month_name = day_month[1].lower()

        if month_name not in self.MONTHS:
            raise ValueError(f"Неизвестный месяц: {month_name}")

        month = self.MONTHS[month_name]

        # Создаем объект даты с текущим годом
        return datetime.date(self.year, month, day)

    def _parse_time(self, time_str: str) -> Tuple[datetime.time, datetime.time]:
        """
        Преобразование строки времени в объекты datetime.time.

        Args:
            time_str (str): Строка с временем в формате "13:45-15:20".

        Returns:
            Tuple[datetime.time, datetime.time]: Кортеж из времени начала и окончания.
        """
        # Разделяем время начала и окончания
        start_str, end_str = time_str.split('-')

        # Преобразуем строки в объекты datetime.time
        start_hour, start_minute = map(int, start_str.split(':'))
        end_hour, end_minute = map(int, end_str.split(':'))

        start_time = datetime.time(start_hour, start_minute)
        end_time = datetime.time(end_hour, end_minute)

        return start_time, end_time

    def _is_holiday(self, date: datetime.date) -> bool:
        """
        Проверка, является ли дата праздничным днем.

        Args:
            date (datetime.date): Проверяемая дата.

        Returns:
            bool: True, если дата является праздничным днем, иначе False.
        """
        # Проверяем в библиотеке holidays
        if date in self.holiday_calendar:
            return True

        # Проверяем в пользовательских праздниках
        return (date.day, date.month) in self.custom_holidays

    def _is_weekend(self, date: datetime.date) -> bool:
        """
        Проверка, является ли дата выходным днем (суббота или воскресенье).

        Args:
            date (datetime.date): Проверяемая дата.

        Returns:
            bool: True, если дата является выходным днем, иначе False.
        """
        return date.weekday() >= 5  # 5 - суббота, 6 - воскресенье

    def _get_busy_intervals(self, schedule_index: int = 0) -> Dict[
        datetime.date, List[Tuple[datetime.time, datetime.time]]]:
        """
        Получение занятых временных интервалов из расписания.

        Args:
            schedule_index (int, optional): Индекс расписания в списке. По умолчанию 0.

        Returns:
            Dict[datetime.date, List[Tuple[datetime.time, datetime.time]]]:
                Словарь с датами и списками занятых интервалов.
        """
        # Проверяем наличие расписания
        if not self.schedules or schedule_index >= len(self.schedules):
            return {}

        # Проверяем наличие кэша
        if schedule_index in self._busy_intervals:
            return self._busy_intervals[schedule_index]

        schedule = self.schedules[schedule_index]
        busy_intervals = {}

        # Обрабатываем каждый день в расписании
        for day_data in schedule:
            try:
                # Получаем дату
                date = self._parse_date(day_data['day'])

                # Инициализируем список занятых интервалов для этой даты
                if date not in busy_intervals:
                    busy_intervals[date] = []

                # Добавляем занятые интервалы из уроков
                for lesson in day_data.get('lessons', []):
                    time_str = lesson.get('time')
                    if time_str:
                        start_time, end_time = self._parse_time(time_str)
                        busy_intervals[date].append((start_time, end_time))

                # Сортируем интервалы по времени начала
                busy_intervals[date].sort(key=lambda x: x[0])

            except (ValueError, KeyError) as e:
                # Пропускаем дни с некорректными данными
                continue

        # Сохраняем в кэш
        self._busy_intervals[schedule_index] = busy_intervals

        return busy_intervals

    def _get_free_intervals(self, date: datetime.date, schedule_index: int = 0,
                            min_start_hour: int = 7, max_end_hour: int = 23) -> List[
        Tuple[datetime.time, datetime.time]]:
        """
        Получение свободных временных интервалов для указанной даты.

        Args:
            date (datetime.date): Дата для анализа.
            schedule_index (int, optional): Индекс расписания в списке. По умолчанию 0.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            List[Tuple[datetime.time, datetime.time]]: Список свободных интервалов.
        """
        # Получаем занятые интервалы
        busy_intervals = self._get_busy_intervals(schedule_index)

        # Если для этой даты нет данных, считаем весь день свободным
        if date not in busy_intervals:
            return [(datetime.time(min_start_hour, 0), datetime.time(max_end_hour, 0))]

        # Создаем список свободных интервалов
        free_intervals = []

        # Начальное время - минимальное время начала
        current_time = datetime.time(min_start_hour, 0)

        # Обрабатываем каждый занятый интервал
        for start_time, end_time in busy_intervals[date]:
            # Если текущее время меньше времени начала занятия,
            # добавляем свободный интервал
            if current_time < start_time:
                free_intervals.append((current_time, start_time))

            # Обновляем текущее время
            if current_time < end_time:
                current_time = end_time

        # Добавляем свободный интервал после последнего занятия до конца дня
        if current_time < datetime.time(max_end_hour, 0):
            free_intervals.append((current_time, datetime.time(max_end_hour, 0)))

        return free_intervals

    def _get_free_intervals_for_multiple_schedules(self, date: datetime.date, schedule_indices: List[int] = None,
                                                   min_start_hour: int = 7, max_end_hour: int = 23) -> List[
        Tuple[datetime.time, datetime.time]]:
        """
        Получение свободных временных интервалов, общих для нескольких расписаний.

        Args:
            date (datetime.date): Дата для анализа.
            schedule_indices (List[int], optional): Список индексов расписаний.
                                                  Если None, используются все расписания.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            List[Tuple[datetime.time, datetime.time]]: Список общих свободных интервалов.
        """
        if not self.schedules:
            return []

        # Если индексы не указаны, используем все расписания
        if schedule_indices is None:
            schedule_indices = list(range(len(self.schedules)))

        # Получаем свободные интервалы для первого расписания
        common_free_intervals = self._get_free_intervals(date, schedule_indices[0], min_start_hour, max_end_hour)

        # Пересекаем со свободными интервалами остальных расписаний
        for idx in schedule_indices[1:]:
            free_intervals = self._get_free_intervals(date, idx, min_start_hour, max_end_hour)

            # Находим пересечения интервалов
            new_common_intervals = []

            for common_start, common_end in common_free_intervals:
                for free_start, free_end in free_intervals:
                    # Находим пересечение
                    intersection_start = max(common_start, free_start)
                    intersection_end = min(common_end, free_end)

                    # Если пересечение существует, добавляем его
                    if intersection_start < intersection_end:
                        new_common_intervals.append((intersection_start, intersection_end))

            # Обновляем общие интервалы
            common_free_intervals = new_common_intervals

            # Если общих интервалов не осталось, прерываем цикл
            if not common_free_intervals:
                break

        return common_free_intervals

    def _interval_duration_minutes(self, start_time: datetime.time, end_time: datetime.time) -> int:
        """
        Вычисление продолжительности временного интервала в минутах.

        Args:
            start_time (datetime.time): Время начала.
            end_time (datetime.time): Время окончания.

        Returns:
            int: Продолжительность в минутах.
        """
        # Преобразуем время в минуты
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        return end_minutes - start_minutes

    def _is_valid_date(self, date: datetime.date, include_weekends: bool = False,
                       include_holidays: bool = False, deadline: datetime.date = None) -> bool:
        """
        Проверка, является ли дата допустимой для поиска окон.

        Args:
            date (datetime.date): Проверяемая дата.
            include_weekends (bool, optional): Учитывать ли выходные дни. По умолчанию False.
            include_holidays (bool, optional): Учитывать ли праздничные дни. По умолчанию False.
            deadline (datetime.date, optional): Крайний срок. По умолчанию None.

        Returns:
            bool: True, если дата допустима, иначе False.
        """
        # Проверяем дедлайн
        if deadline and date > deadline:
            return False

        # Проверяем выходные
        if not include_weekends and self._is_weekend(date):
            return False

        # Проверяем праздники
        if not include_holidays and self._is_holiday(date):
            return False

        return True

    def find_nearest_window_by_width(self,
                                     width_minutes: int,
                                     start_date: datetime.date = None,
                                     schedule_index: int = 0,
                                     include_weekends: bool = False,
                                     include_holidays: bool = False,
                                     deadline: datetime.date = None,
                                     max_days_to_check: int = 30,
                                     min_start_hour: int = 7,
                                     max_end_hour: int = 23) -> Optional[Dict]:
        """
        Алгоритм 1: Поиск ближайшего окна заданной ширины.

        Args:
            width_minutes (int): Требуемая ширина окна в минутах.
            start_date (datetime.date, optional): Дата начала поиска.
                                               Если None, используется текущая дата.
            schedule_index (int, optional): Индекс расписания в списке. По умолчанию 0.
            include_weekends (bool, optional): Учитывать ли выходные дни. По умолчанию False.
            include_holidays (bool, optional): Учитывать ли праздничные дни. По умолчанию False.
            deadline (datetime.date, optional): Крайний срок. По умолчанию None.
            max_days_to_check (int, optional): Максимальное количество дней для проверки. По умолчанию 30.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            Optional[Dict]: Информация о найденном окне или None, если окно не найдено.
        """
        # Проверяем наличие расписания
        if not self.schedules or schedule_index >= len(self.schedules):
            return None

        # Если дата начала не указана, используем текущую дату
        if start_date is None:
            start_date = datetime.date.today()

        # Перебираем даты, начиная с указанной
        current_date = start_date
        days_checked = 0

        while days_checked < max_days_to_check:
            # Проверяем, является ли дата допустимой
            if self._is_valid_date(current_date, include_weekends, include_holidays, deadline):
                # Получаем свободные интервалы для этой даты
                free_intervals = self._get_free_intervals(current_date, schedule_index, min_start_hour, max_end_hour)

                # Ищем интервал подходящей ширины
                for start_time, end_time in free_intervals:
                    duration = self._interval_duration_minutes(start_time, end_time)

                    if duration >= width_minutes:
                        # Нашли подходящее окно
                        return {
                            'date': current_date,
                            'start_time': start_time,
                            'end_time': datetime.time(
                                (start_time.hour * 60 + start_time.minute + width_minutes) // 60,
                                (start_time.hour * 60 + start_time.minute + width_minutes) % 60
                            ),
                            'duration_minutes': width_minutes
                        }

            # Переходим к следующей дате
            current_date += datetime.timedelta(days=1)
            days_checked += 1

        # Окно не найдено
        return None

    def find_nearest_window_by_width_and_length(self,
                                                width_minutes: int,
                                                days_count: int,
                                                start_date: datetime.date = None,
                                                schedule_index: int = 0,
                                                include_weekends: bool = False,
                                                include_holidays: bool = False,
                                                deadline: datetime.date = None,
                                                max_days_to_check: int = 30,
                                                min_start_hour: int = 7,
                                                max_end_hour: int = 23) -> Optional[Dict]:
        """
        Алгоритм 2: Поиск ближайшего окна заданной ширины и длины (количества дней).

        Args:
            width_minutes (int): Требуемая ширина окна в минутах.
            days_count (int): Требуемое количество дней.
            start_date (datetime.date, optional): Дата начала поиска.
                                               Если None, используется текущая дата.
            schedule_index (int, optional): Индекс расписания в списке. По умолчанию 0.
            include_weekends (bool, optional): Учитывать ли выходные дни. По умолчанию False.
            include_holidays (bool, optional): Учитывать ли праздничные дни. По умолчанию False.
            deadline (datetime.date, optional): Крайний срок. По умолчанию None.
            max_days_to_check (int, optional): Максимальное количество дней для проверки. По умолчанию 30.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            Optional[Dict]: Информация о найденном окне или None, если окно не найдено.
        """
        # Проверяем наличие расписания
        if not self.schedules or schedule_index >= len(self.schedules):
            return None

        # Если дата начала не указана, используем текущую дату
        if start_date is None:
            start_date = datetime.date.today()

        # Перебираем даты, начиная с указанной
        current_date = start_date
        days_checked = 0

        while days_checked < max_days_to_check:
            # Проверяем, является ли дата допустимой
            if self._is_valid_date(current_date, include_weekends, include_holidays, deadline):
                # Проверяем, можно ли найти окно, начиная с текущей даты
                consecutive_days = 0
                found_windows = []

                # Проверяем последовательные дни
                for day_offset in range(days_count):
                    check_date = current_date + datetime.timedelta(days=day_offset)

                    # Проверяем, является ли дата допустимой
                    if not self._is_valid_date(check_date, include_weekends, include_holidays, deadline):
                        break

                    # Получаем свободные интервалы для этой даты
                    free_intervals = self._get_free_intervals(check_date, schedule_index, min_start_hour, max_end_hour)

                    # Ищем интервал подходящей ширины
                    window_found = False
                    for start_time, end_time in free_intervals:
                        duration = self._interval_duration_minutes(start_time, end_time)

                        if duration >= width_minutes:
                            # Нашли подходящее окно для этого дня
                            found_windows.append({
                                'date': check_date,
                                'start_time': start_time,
                                'end_time': datetime.time(
                                    (start_time.hour * 60 + start_time.minute + width_minutes) // 60,
                                    (start_time.hour * 60 + start_time.minute + width_minutes) % 60
                                ),
                                'duration_minutes': width_minutes
                            })
                            consecutive_days += 1
                            window_found = True
                            break

                    if not window_found:
                        break

                # Если нашли нужное количество последовательных дней, возвращаем результат
                if consecutive_days == days_count:
                    return {
                        'start_date': current_date,
                        'end_date': current_date + datetime.timedelta(days=days_count - 1),
                        'days_count': days_count,
                        'width_minutes': width_minutes,
                        'windows': found_windows
                    }

            # Переходим к следующей дате
            current_date += datetime.timedelta(days=1)
            days_checked += 1

        # Окно не найдено
        return None

    def find_window_by_volume(self,
                              total_minutes: int,
                              min_width_minutes: int = 60,
                              start_date: datetime.date = None,
                              schedule_index: int = 0,
                              include_weekends: bool = False,
                              include_holidays: bool = False,
                              deadline: datetime.date = None,
                              max_days_to_check: int = 30,
                              min_start_hour: int = 7,
                              max_end_hour: int = 23) -> Optional[Dict]:
        """
        Алгоритм 3: Поиск окна заданного объема с минимизацией количества дней.

        Args:
            total_minutes (int): Общий требуемый объем в минутах.
            min_width_minutes (int, optional): Минимальная ширина окна в минутах. По умолчанию 60.
            start_date (datetime.date, optional): Дата начала поиска.
                                               Если None, используется текущая дата.
            schedule_index (int, optional): Индекс расписания в списке. По умолчанию 0.
            include_weekends (bool, optional): Учитывать ли выходные дни. По умолчанию False.
            include_holidays (bool, optional): Учитывать ли праздничные дни. По умолчанию False.
            deadline (datetime.date, optional): Крайний срок. По умолчанию None.
            max_days_to_check (int, optional): Максимальное количество дней для проверки. По умолчанию 30.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            Optional[Dict]: Информация о найденном окне или None, если окно не найдено.
        """
        # Проверяем наличие расписания
        if not self.schedules or schedule_index >= len(self.schedules):
            return None

        # Если дата начала не указана, используем текущую дату
        if start_date is None:
            start_date = datetime.date.today()

        # Перебираем даты, начиная с указанной
        current_date = start_date
        days_checked = 0

        # Накапливаем окна до достижения требуемого объема
        accumulated_minutes = 0
        found_windows = []

        while days_checked < max_days_to_check and accumulated_minutes < total_minutes:
            # Проверяем, является ли дата допустимой
            if self._is_valid_date(current_date, include_weekends, include_holidays, deadline):
                # Получаем свободные интервалы для этой даты
                free_intervals = self._get_free_intervals(current_date, schedule_index, min_start_hour, max_end_hour)

                # Сортируем интервалы по длительности (от большего к меньшему)
                free_intervals.sort(key=lambda x: self._interval_duration_minutes(x[0], x[1]), reverse=True)

                day_windows = []

                # Ищем интервалы подходящей ширины
                for start_time, end_time in free_intervals:
                    duration = self._interval_duration_minutes(start_time, end_time)

                    if duration >= min_width_minutes:
                        # Определяем, сколько минут можно взять из этого интервала
                        minutes_to_take = min(duration, total_minutes - accumulated_minutes)

                        if minutes_to_take >= min_width_minutes:
                            # Нашли подходящее окно
                            window = {
                                'date': current_date,
                                'start_time': start_time,
                                'end_time': datetime.time(
                                    (start_time.hour * 60 + start_time.minute + minutes_to_take) // 60,
                                    (start_time.hour * 60 + start_time.minute + minutes_to_take) % 60
                                ),
                                'duration_minutes': minutes_to_take
                            }

                            day_windows.append(window)
                            accumulated_minutes += minutes_to_take

                            # Если достигли требуемого объема, прерываем цикл
                            if accumulated_minutes >= total_minutes:
                                break

                # Добавляем окна этого дня к общему списку
                found_windows.extend(day_windows)

            # Переходим к следующей дате
            current_date += datetime.timedelta(days=1)
            days_checked += 1

        # Если накопили требуемый объем, возвращаем результат
        if accumulated_minutes >= total_minutes:
            return {
                'total_minutes': accumulated_minutes,
                'days_count': len(set(window['date'] for window in found_windows)),
                'windows': found_windows
            }

        # Окно не найдено
        return None

    def find_common_window_for_multiple_schedules(self,
                                                  width_minutes: int,
                                                  schedule_indices: List[int] = None,
                                                  start_date: datetime.date = None,
                                                  include_weekends: bool = False,
                                                  include_holidays: bool = False,
                                                  deadline: datetime.date = None,
                                                  max_days_to_check: int = 30,
                                                  min_start_hour: int = 7,
                                                  max_end_hour: int = 23) -> Optional[Dict]:
        """
        Алгоритм 4: Поиск окна заданной ширины, одновременно доступного у нескольких людей.

        Args:
            width_minutes (int): Требуемая ширина окна в минутах.
            schedule_indices (List[int], optional): Список индексов расписаний.
                                                  Если None, используются все расписания.
            start_date (datetime.date, optional): Дата начала поиска.
                                               Если None, используется текущая дата.
            include_weekends (bool, optional): Учитывать ли выходные дни. По умолчанию False.
            include_holidays (bool, optional): Учитывать ли праздничные дни. По умолчанию False.
            deadline (datetime.date, optional): Крайний срок. По умолчанию None.
            max_days_to_check (int, optional): Максимальное количество дней для проверки. По умолчанию 30.
            min_start_hour (int, optional): Минимальное время начала (час). По умолчанию 7.
            max_end_hour (int, optional): Максимальное время окончания (час). По умолчанию 23.

        Returns:
            Optional[Dict]: Информация о найденном окне или None, если окно не найдено.
        """
        # Проверяем наличие расписаний
        if not self.schedules:
            return None

        # Если индексы не указаны, используем все расписания
        if schedule_indices is None:
            schedule_indices = list(range(len(self.schedules)))

        # Если дата начала не указана, используем текущую дату
        if start_date is None:
            start_date = datetime.date.today()

        # Перебираем даты, начиная с указанной
        current_date = start_date
        days_checked = 0

        while days_checked < max_days_to_check:
            # Проверяем, является ли дата допустимой
            if self._is_valid_date(current_date, include_weekends, include_holidays, deadline):
                # Получаем общие свободные интервалы для всех расписаний
                common_free_intervals = self._get_free_intervals_for_multiple_schedules(
                    current_date, schedule_indices, min_start_hour, max_end_hour
                )

                # Ищем интервал подходящей ширины
                for start_time, end_time in common_free_intervals:
                    duration = self._interval_duration_minutes(start_time, end_time)

                    if duration >= width_minutes:
                        # Нашли подходящее окно
                        return {
                            'date': current_date,
                            'start_time': start_time,
                            'end_time': datetime.time(
                                (start_time.hour * 60 + start_time.minute + width_minutes) // 60,
                                (start_time.hour * 60 + start_time.minute + width_minutes) % 60
                            ),
                            'duration_minutes': width_minutes,
                            'participants_count': len(schedule_indices)
                        }

            # Переходим к следующей дате
            current_date += datetime.timedelta(days=1)
            days_checked += 1

        # Окно не найдено
        return None
