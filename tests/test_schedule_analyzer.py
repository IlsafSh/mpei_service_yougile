import unittest
from unittest.mock import patch, MagicMock, Mock, mock_open
import os
import json
import datetime
from schedule_analyzer.ScheduleAnalyzer import ScheduleAnalyzer


class TestScheduleAnalyzer(unittest.TestCase):
    """
    Комплексные тесты для класса ScheduleAnalyzer из модуля schedule_analyzer.

    Тесты покрывают следующие сценарии:
    1. Инициализация анализатора расписаний
    2. Работа с параметрами времени начала/окончания
    3. Работа с праздничными днями через библиотеку holidays
    4. Поиск окон с различными ограничениями
    5. Обработка граничных случаев
    6. Работа с несколькими расписаниями
    """

    def setUp(self):
        """
        Подготовка окружения для тестов.
        Создаем тестовые данные расписаний.
        """
        # Подготавливаем тестовые данные расписания
        self.test_schedule1 = [
            {
                "day": "Пн, 17 февраля",
                "lessons": [
                    {
                        "time": "09:20-10:55",
                        "subject": "Математика",
                        "type": "Лекция",
                        "teacher": "Иванов И.И.",
                        "room": "А-100"
                    },
                    {
                        "time": "11:10-12:45",
                        "subject": "Физика",
                        "type": "Практика",
                        "teacher": "Петров П.П.",
                        "room": "Б-200"
                    }
                ]
            },
            {
                "day": "Вт, 18 февраля",
                "lessons": [
                    {
                        "time": "13:45-15:20",
                        "subject": "Информатика",
                        "type": "Лабораторная",
                        "teacher": "Сидоров С.С.",
                        "room": "В-300"
                    }
                ]
            },
            {
                "day": "Ср, 19 февраля",
                "lessons": []
            },
            {
                "day": "Чт, 20 февраля",
                "lessons": [
                    {
                        "time": "09:20-10:55",
                        "subject": "Английский язык",
                        "type": "Практика",
                        "teacher": "Смирнова А.А.",
                        "room": "Г-400"
                    },
                    {
                        "time": "15:35-17:10",
                        "subject": "Программирование",
                        "type": "Лабораторная",
                        "teacher": "Козлов К.К.",
                        "room": "Д-500"
                    }
                ]
            },
            {
                "day": "Пт, 21 февраля",
                "lessons": [
                    {
                        "time": "11:10-12:45",
                        "subject": "История",
                        "type": "Лекция",
                        "teacher": "Николаев Н.Н.",
                        "room": "Е-600"
                    }
                ]
            },
            {
                "day": "Сб, 22 февраля",
                "lessons": []
            },
            {
                "day": "Вс, 23 февраля",
                "lessons": []
            }
        ]

        # Второе расписание для тестирования алгоритма поиска общих окон
        self.test_schedule2 = [
            {
                "day": "Пн, 17 февраля",
                "lessons": [
                    {
                        "time": "09:20-12:45",
                        "subject": "Базы данных",
                        "type": "Лекция",
                        "teacher": "Морозов М.М.",
                        "room": "Ж-700"
                    }
                ]
            },
            {
                "day": "Вт, 18 февраля",
                "lessons": [
                    {
                        "time": "11:10-12:45",
                        "subject": "Сети",
                        "type": "Практика",
                        "teacher": "Зайцев З.З.",
                        "room": "И-800"
                    }
                ]
            },
            {
                "day": "Ср, 19 февраля",
                "lessons": [
                    {
                        "time": "13:45-17:10",
                        "subject": "Проектирование",
                        "type": "Лабораторная",
                        "teacher": "Волков В.В.",
                        "room": "К-900"
                    }
                ]
            },
            {
                "day": "Чт, 20 февраля",
                "lessons": []
            },
            {
                "day": "Пт, 21 февраля",
                "lessons": [
                    {
                        "time": "09:20-10:55",
                        "subject": "Экономика",
                        "type": "Лекция",
                        "teacher": "Соколов С.С.",
                        "room": "Л-1000"
                    }
                ]
            },
            {
                "day": "Сб, 22 февраля",
                "lessons": []
            },
            {
                "day": "Вс, 23 февраля",
                "lessons": []
            }
        ]

        # Создаем тестовый год
        self.test_year = 2025

        # Создаем тестовые праздничные дни
        self.test_custom_holidays = {(23, 2), (8, 3)}

    def test_init(self):
        """
        Тест инициализации анализатора расписаний.
        """
        # Создаем экземпляр анализатора с базовыми параметрами
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Проверяем, что параметры установлены правильно
        self.assertEqual(analyzer.year, self.test_year)
        self.assertEqual(analyzer.country, 'RU')
        self.assertEqual(len(analyzer.schedules), 1)
        self.assertEqual(analyzer.custom_holidays, set())

        # Создаем экземпляр анализатора с пользовательскими праздниками
        analyzer = ScheduleAnalyzer(
            [self.test_schedule1],
            year=self.test_year,
            country='US',
            custom_holidays=self.test_custom_holidays
        )

        # Проверяем, что параметры установлены правильно
        self.assertEqual(analyzer.year, self.test_year)
        self.assertEqual(analyzer.country, 'US')
        self.assertEqual(len(analyzer.schedules), 1)
        self.assertEqual(analyzer.custom_holidays, self.test_custom_holidays)

    def test_add_schedule(self):
        """
        Тест добавления расписания.
        """
        # Создаем экземпляр анализатора без расписаний
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Проверяем, что список расписаний пуст
        self.assertEqual(len(analyzer.schedules), 0)

        # Добавляем расписание
        analyzer.add_schedule(self.test_schedule1)

        # Проверяем, что расписание добавлено
        self.assertEqual(len(analyzer.schedules), 1)

        # Добавляем еще одно расписание
        analyzer.add_schedule(self.test_schedule2)

        # Проверяем, что расписание добавлено
        self.assertEqual(len(analyzer.schedules), 2)

    def test_set_schedules(self):
        """
        Тест установки списка расписаний.
        """
        # Создаем экземпляр анализатора без расписаний
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Устанавливаем список расписаний
        analyzer.set_schedules([self.test_schedule1, self.test_schedule2])

        # Проверяем, что список расписаний установлен
        self.assertEqual(len(analyzer.schedules), 2)

    def test_set_holiday_calendar(self):
        """
        Тест установки календаря праздников.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Проверяем, что календарь праздников установлен для России
        self.assertEqual(analyzer.country, 'RU')

        # Устанавливаем календарь праздников для США
        analyzer.set_holiday_calendar(country='US')

        # Проверяем, что календарь праздников изменен
        self.assertEqual(analyzer.country, 'US')

        # Проверяем, что календарь праздников содержит праздники США
        self.assertIn(datetime.date(self.test_year, 7, 4), analyzer.holiday_calendar)  # День независимости США

    def test_add_custom_holiday(self):
        """
        Тест добавления пользовательского праздничного дня.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Проверяем, что список пользовательских праздников пуст
        self.assertEqual(len(analyzer.custom_holidays), 0)

        # Добавляем пользовательский праздник
        analyzer.add_custom_holiday(1, 5)  # 1 мая

        # Проверяем, что праздник добавлен
        self.assertEqual(len(analyzer.custom_holidays), 1)
        self.assertIn((1, 5), analyzer.custom_holidays)

        # Добавляем еще один праздник
        analyzer.add_custom_holiday(9, 5)  # 9 мая

        # Проверяем, что праздник добавлен
        self.assertEqual(len(analyzer.custom_holidays), 2)
        self.assertIn((9, 5), analyzer.custom_holidays)

    def test_set_custom_holidays(self):
        """
        Тест установки пользовательского набора праздничных дней.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Устанавливаем пользовательский набор праздников
        analyzer.set_custom_holidays(self.test_custom_holidays)

        # Проверяем, что набор праздников установлен
        self.assertEqual(analyzer.custom_holidays, self.test_custom_holidays)

    def test_is_holiday(self):
        """
        Тест проверки, является ли дата праздничным днем.
        """
        # Создаем экземпляр анализатора с пользовательскими праздниками
        analyzer = ScheduleAnalyzer(
            year=self.test_year,
            custom_holidays=self.test_custom_holidays
        )

        # Проверяем пользовательский праздник
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 2, 23)))

        # Проверяем праздник из библиотеки holidays
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 1, 1)))  # Новый год

        # Проверяем обычный день
        self.assertFalse(analyzer._is_holiday(datetime.date(self.test_year, 2, 15)))

    def test_is_weekend(self):
        """
        Тест проверки, является ли дата выходным днем.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer(year=self.test_year)

        # Проверяем субботу
        self.assertTrue(analyzer._is_weekend(datetime.date(2025, 2, 22)))

        # Проверяем воскресенье
        self.assertTrue(analyzer._is_weekend(datetime.date(2025, 2, 23)))

        # Проверяем будний день
        self.assertFalse(analyzer._is_weekend(datetime.date(2025, 2, 21)))

    def test_is_valid_date(self):
        """
        Тест проверки, является ли дата допустимой для поиска окон.
        """
        # Создаем экземпляр анализатора с пользовательскими праздниками
        analyzer = ScheduleAnalyzer(
            year=self.test_year,
            custom_holidays=self.test_custom_holidays
        )

        # Проверяем будний день без ограничений
        self.assertTrue(analyzer._is_valid_date(
            datetime.date(2025, 2, 17),  # Понедельник
            include_weekends=False,
            include_holidays=False
        ))

        # Проверяем выходной день без учета выходных
        self.assertFalse(analyzer._is_valid_date(
            datetime.date(2025, 2, 22),  # Суббота
            include_weekends=False,
            include_holidays=False
        ))

        # Проверяем выходной день с учетом выходных
        self.assertTrue(analyzer._is_valid_date(
            datetime.date(2025, 2, 22),  # Суббота
            include_weekends=True,
            include_holidays=False
        ))

        # Проверяем праздничный день без учета праздников
        self.assertFalse(analyzer._is_valid_date(
            datetime.date(2025, 2, 23),  # 23 февраля
            include_weekends=True,
            include_holidays=False
        ))

        # Проверяем праздничный день с учетом праздников
        self.assertTrue(analyzer._is_valid_date(
            datetime.date(2025, 2, 23),  # 23 февраля
            include_weekends=True,
            include_holidays=True
        ))

        # Проверяем дату после дедлайна
        self.assertFalse(analyzer._is_valid_date(
            datetime.date(2025, 3, 1),
            include_weekends=True,
            include_holidays=True,
            deadline=datetime.date(2025, 2, 28)
        ))

    def test_get_free_intervals(self):
        """
        Тест получения свободных временных интервалов.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Получаем свободные интервалы для понедельника
        free_intervals = analyzer._get_free_intervals(
            datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            min_start_hour=7,
            max_end_hour=23
        )

        # Проверяем, что есть свободные интервалы
        self.assertGreater(len(free_intervals), 0)

        # Проверяем, что первый интервал начинается в 7:00
        self.assertEqual(free_intervals[0][0], datetime.time(7, 0))

        # Проверяем, что последний интервал заканчивается в 23:00
        self.assertEqual(free_intervals[-1][1], datetime.time(23, 0))

        # Получаем свободные интервалы с ограниченным временем
        free_intervals = analyzer._get_free_intervals(
            datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            min_start_hour=8,
            max_end_hour=18
        )

        # Проверяем, что первый интервал начинается в 8:00
        self.assertEqual(free_intervals[0][0], datetime.time(8, 0))

        # Проверяем, что последний интервал заканчивается в 18:00
        self.assertEqual(free_intervals[-1][1], datetime.time(18, 0))

    def test_get_free_intervals_for_multiple_schedules(self):
        """
        Тест получения свободных временных интервалов для нескольких расписаний.
        """
        # Создаем экземпляр анализатора с двумя расписаниями
        analyzer = ScheduleAnalyzer([self.test_schedule1, self.test_schedule2], year=self.test_year)

        # Получаем общие свободные интервалы для понедельника
        common_free_intervals = analyzer._get_free_intervals_for_multiple_schedules(
            datetime.date(2025, 2, 17),  # Понедельник
            schedule_indices=[0, 1],
            min_start_hour=7,
            max_end_hour=23
        )

        # Проверяем, что есть общие свободные интервалы
        self.assertGreater(len(common_free_intervals), 0)

        # Получаем общие свободные интервалы с ограниченным временем
        common_free_intervals = analyzer._get_free_intervals_for_multiple_schedules(
            datetime.date(2025, 2, 17),  # Понедельник
            schedule_indices=[0, 1],
            min_start_hour=8,
            max_end_hour=18
        )

        # Проверяем, что есть общие свободные интервалы
        self.assertGreater(len(common_free_intervals), 0)

    def test_find_nearest_window_by_width(self):
        """
        Тест алгоритма поиска ближайшего окна заданной ширины.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Ищем окно шириной 2 часа
        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что ширина окна соответствует требуемой
        self.assertEqual(window['duration_minutes'], 120)

        # Ищем окно с ограниченным временем начала и окончания
        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False,
            min_start_hour=10,
            max_end_hour=16
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что время начала не раньше 10:00
        self.assertGreaterEqual(window['start_time'].hour, 10)

        # Проверяем, что время окончания не позже 16:00
        self.assertLessEqual(window['end_time'].hour, 16)

    def test_find_nearest_window_by_width_and_length(self):
        """
        Тест алгоритма поиска ближайшего окна заданной ширины и длины.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Ищем окно шириной 2 часа на протяжении 2 дней
        window = analyzer.find_nearest_window_by_width_and_length(
            width_minutes=120,
            days_count=2,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что количество дней соответствует требуемому
        self.assertEqual(window['days_count'], 2)

        # Проверяем, что ширина окна соответствует требуемой
        self.assertEqual(window['width_minutes'], 120)

        # Ищем окно с ограниченным временем начала и окончания
        window = analyzer.find_nearest_window_by_width_and_length(
            width_minutes=120,
            days_count=2,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False,
            min_start_hour=10,
            max_end_hour=16
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что для каждого дня время начала не раньше 10:00
        for day_window in window['windows']:
            self.assertGreaterEqual(day_window['start_time'].hour, 10)

        # Проверяем, что для каждого дня время окончания не позже 16:00
        for day_window in window['windows']:
            self.assertLessEqual(day_window['end_time'].hour, 16)

    def test_find_window_by_volume(self):
        """
        Тест алгоритма поиска окна заданного объема.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Ищем окно общим объемом 5 часов
        window = analyzer.find_window_by_volume(
            total_minutes=300,
            min_width_minutes=60,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что общий объем соответствует требуемому или больше
        self.assertGreaterEqual(window['total_minutes'], 300)

        # Ищем окно с ограниченным временем начала и окончания
        window = analyzer.find_window_by_volume(
            total_minutes=300,
            min_width_minutes=60,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            include_weekends=False,
            include_holidays=False,
            min_start_hour=10,
            max_end_hour=16
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что для каждого окна время начала не раньше 10:00
        for day_window in window['windows']:
            self.assertGreaterEqual(day_window['start_time'].hour, 10)

        # Проверяем, что для каждого окна время окончания не позже 16:00
        for day_window in window['windows']:
            self.assertLessEqual(day_window['end_time'].hour, 16)

    def test_find_common_window_for_multiple_schedules(self):
        """
        Тест алгоритма поиска окна, одновременно доступного у нескольких людей.
        """
        # Создаем экземпляр анализатора с двумя расписаниями
        analyzer = ScheduleAnalyzer([self.test_schedule1, self.test_schedule2], year=self.test_year)

        # Ищем общее окно шириной 2 часа
        window = analyzer.find_common_window_for_multiple_schedules(
            width_minutes=120,
            schedule_indices=[0, 1],
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            include_weekends=False,
            include_holidays=False
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что ширина окна соответствует требуемой
        self.assertEqual(window['duration_minutes'], 120)

        # Проверяем, что количество участников соответствует требуемому
        self.assertEqual(window['participants_count'], 2)

        # Ищем общее окно с ограниченным временем начала и окончания
        window = analyzer.find_common_window_for_multiple_schedules(
            width_minutes=120,
            schedule_indices=[0, 1],
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            include_weekends=False,
            include_holidays=False,
            min_start_hour=10,
            max_end_hour=16
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что время начала не раньше 10:00
        self.assertGreaterEqual(window['start_time'].hour, 10)

        # Проверяем, что время окончания не позже 16:00
        self.assertLessEqual(window['end_time'].hour, 16)

    def test_edge_cases(self):
        """
        Тест граничных случаев.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Тест с очень большой шириной окна
        window = analyzer.find_nearest_window_by_width(
            width_minutes=1000,  # Очень большая ширина
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0
        )

        # Проверяем, что окно не найдено
        self.assertIsNone(window)

        # Тест с очень большим количеством дней
        window = analyzer.find_nearest_window_by_width_and_length(
            width_minutes=120,
            days_count=100,  # Очень большое количество дней
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0
        )

        # Проверяем, что окно не найдено
        self.assertIsNone(window)

        # Тест с очень большим объемом
        window = analyzer.find_window_by_volume(
            total_minutes=10000,  # Очень большой объем
            min_width_minutes=60,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0
        )

        # Проверяем, что окно не найдено
        self.assertIsNone(window)

        # Тест с пустым расписанием
        analyzer = ScheduleAnalyzer(year=self.test_year)

        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0
        )

        # Проверяем, что окно не найдено
        self.assertIsNone(window)

    def test_holidays_integration(self):
        """
        Тест интеграции с библиотекой holidays.
        """
        # Создаем экземпляр анализатора с праздниками России
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year, country='RU')

        # Проверяем, что 1 января является праздником
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 1, 1)))

        # Проверяем, что 23 февраля является праздником
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 2, 23)))

        # Создаем экземпляр анализатора с праздниками США
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year, country='US')

        # Проверяем, что 4 июля является праздником
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 7, 4)))

        # Проверяем, что 23 февраля не является праздником в США
        self.assertFalse(analyzer._is_holiday(datetime.date(self.test_year, 2, 23)))

        # Добавляем пользовательский праздник
        analyzer.add_custom_holiday(23, 2)

        # Проверяем, что 23 февраля теперь является праздником
        self.assertTrue(analyzer._is_holiday(datetime.date(self.test_year, 2, 23)))

    def test_time_constraints(self):
        """
        Тест ограничений по времени.
        """
        # Создаем экземпляр анализатора
        analyzer = ScheduleAnalyzer([self.test_schedule1], year=self.test_year)

        # Ищем окно с ранним временем начала
        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            min_start_hour=5  # Раннее время начала
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что время начала не раньше 5:00
        self.assertGreaterEqual(window['start_time'].hour, 5)

        # Ищем окно с поздним временем окончания
        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            max_end_hour=22  # Позднее время окончания
        )

        # Проверяем, что окно найдено
        self.assertIsNotNone(window)

        # Проверяем, что время окончания не позже 22:00
        self.assertLessEqual(window['end_time'].hour, 22)

        # Ищем окно с узким диапазоном времени
        window = analyzer.find_nearest_window_by_width(
            width_minutes=120,
            start_date=datetime.date(2025, 2, 17),  # Понедельник
            schedule_index=0,
            min_start_hour=13,
            max_end_hour=15
        )

        # Проверяем, что окно найдено, так как диапазон ровно 2 часа (120 минут)
        self.assertIsNotNone(window)


if __name__ == '__main__':
    unittest.main()
