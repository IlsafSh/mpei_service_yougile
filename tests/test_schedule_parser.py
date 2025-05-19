import unittest
from unittest.mock import patch, MagicMock, Mock, mock_open
import os
import json
import logging
from datetime import datetime
from schedule_parser.ScheduleParser import MPEIRuzParser


class TestMPEIRuzParser(unittest.TestCase):
    """
    Комплексные тесты для класса MPEIRuzParser из модуля schedule_parser.

    Тесты покрывают следующие сценарии:
    1. Инициализация парсера
    2. Парсинг расписания для разных типов объектов (группа, преподаватель, аудитория)
    3. Парсинг расписания за указанный период дат
    4. Обработка ошибок при парсинге
    5. Корректное закрытие ресурсов
    """

    def setUp(self):
        """
        Подготовка окружения для тестов.
        Создаем моки для Selenium и других внешних зависимостей.
        """
        # Создаем временную директорию для тестовых файлов
        self.test_dir = os.path.join(os.getcwd(), "test_files")
        os.makedirs(self.test_dir, exist_ok=True)

        # Создаем директорию для диагностических файлов (важно для логирования)
        self.diagnostic_dir = os.path.join(os.getcwd(), "diagnostic_files")
        os.makedirs(self.diagnostic_dir, exist_ok=True)

        # Подготавливаем тестовые данные расписания
        self.test_schedule = [
            {
                "day": "Пн, 07 апреля",
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
                "day": "Вт, 08 апреля",
                "lessons": [
                    {
                        "time": "13:45-15:20",
                        "subject": "Информатика",
                        "type": "Лабораторная",
                        "teacher": "Сидоров С.С.",
                        "room": "В-300"
                    }
                ]
            }
        ]

        # Патчим логгер, чтобы не засорять вывод тестов
        self.logger_patcher = patch('logging.Logger')
        self.mock_logger = self.logger_patcher.start()

        # Патчим FileHandler, чтобы избежать проблем с созданием лог-файла
        self.file_handler_patcher = patch('logging.FileHandler')
        self.mock_file_handler = self.file_handler_patcher.start()

        # Патчим драйвер Firefox
        self.firefox_patcher = patch('selenium.webdriver.Firefox')
        self.mock_firefox = self.firefox_patcher.start()

        # Настраиваем мок для драйвера
        self.mock_driver = MagicMock()
        self.mock_firefox.return_value = self.mock_driver

        # Настраиваем мок для метода save_screenshot
        self.mock_driver.save_screenshot.return_value = True

        # Патчим WebDriverWait
        self.wait_patcher = patch('selenium.webdriver.support.ui.WebDriverWait')
        self.mock_wait = self.wait_patcher.start()

    def tearDown(self):
        """
        Очистка после тестов.
        """
        # Останавливаем все патчи
        self.logger_patcher.stop()
        self.file_handler_patcher.stop()
        self.firefox_patcher.stop()
        self.wait_patcher.stop()

        # Удаляем тестовые файлы, если они существуют
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

        # Удаляем диагностические файлы, если они существуют
        if os.path.exists(self.diagnostic_dir):
            for file in os.listdir(self.diagnostic_dir):
                try:
                    os.remove(os.path.join(self.diagnostic_dir, file))
                except:
                    pass
            try:
                os.rmdir(self.diagnostic_dir)
            except:
                pass

    def _setup_mock_driver(self, mock_driver):
        """
        Настройка мока драйвера для имитации работы Selenium.
        """
        # Настраиваем мок для метода find_element
        mock_element = MagicMock()
        mock_element.text = "Текст элемента"
        mock_driver.find_element.return_value = mock_element

        # Настраиваем мок для метода find_elements
        mock_elements = [MagicMock() for _ in range(3)]
        for i, elem in enumerate(mock_elements):
            elem.text = f"Элемент {i}"
        mock_driver.find_elements.return_value = mock_elements

        # Настраиваем мок для метода get
        mock_driver.get.return_value = None

        # Настраиваем мок для метода execute_script
        mock_driver.execute_script.return_value = None

        # Настраиваем мок для метода quit
        mock_driver.quit.return_value = None

        # Настраиваем мок для метода save_screenshot
        mock_driver.save_screenshot.return_value = True

        return mock_driver

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_init(self, mock_firefox_options):
        """
        Тест инициализации парсера.
        """
        # Настраиваем мок для FirefoxOptions
        mock_options = MagicMock()
        mock_firefox_options.return_value = mock_options

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True, max_weeks=10, cleanup_files=False)

        # Проверяем, что драйвер Firefox был инициализирован с правильными параметрами
        self.mock_firefox.assert_called_once()

        # Проверяем, что параметры парсера установлены правильно
        self.assertEqual(parser.url, "https://bars.mpei.ru/bars_web/Open/RUZ/Timetable")
        self.assertEqual(parser.max_weeks, 10)
        self.assertEqual(parser.cleanup_files, False)

        # Проверяем, что опции Firefox были настроены правильно
        mock_options.add_argument.assert_any_call("--headless")
        mock_options.add_argument.assert_any_call("--width=1920")
        mock_options.add_argument.assert_any_call("--height=1080")

    @patch('schedule_parser.ScheduleParser.json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_schedule_to_json(self, mock_open, mock_json_dump):
        """
        Тест сохранения расписания в JSON-файл.
        """
        # Создаем экземпляр парсера с моками
        with patch('schedule_parser.ScheduleParser.FirefoxOptions'):
            parser = MPEIRuzParser(headless=True)

        # Вызываем метод сохранения расписания
        parser._save_schedule_to_json(self.test_schedule, "test_schedule.json")

        # Проверяем, что файл был открыт для записи
        mock_open.assert_called_once()

        # Проверяем, что json.dump был вызван с правильными параметрами
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], self.test_schedule)  # Первый аргумент - данные расписания
        self.assertEqual(kwargs['ensure_ascii'], False)  # Проверяем параметр ensure_ascii
        self.assertEqual(kwargs['indent'], 4)  # Проверяем параметр indent

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_close(self, mock_firefox_options):
        """
        Тест метода close() для корректного закрытия ресурсов.
        """
        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Вызываем метод close
        parser.close()

        # Проверяем, что метод quit был вызван у драйвера
        self.mock_driver.quit.assert_called_once()

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_group_schedule(self, mock_firefox_options):
        """
        Тест парсинга расписания для учебной группы.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Патчим приватные методы парсера
        with patch.object(parser, '_open_page', return_value=True), \
                patch.object(parser, '_select_schedule_type', return_value=True), \
                patch.object(parser, '_select_schedule_object', return_value=True), \
                patch.object(parser, '_find_zero_week', return_value=True), \
                patch.object(parser, '_get_current_week_number', return_value=0), \
                patch.object(parser, '_parse_week_schedule', return_value=self.test_schedule), \
                patch.object(parser, '_go_to_next_week', return_value=True), \
                patch.object(parser, '_save_schedule_to_json'):
            # Вызываем метод парсинга
            result = parser.parse("ЭР-03-23", schedule_type=MPEIRuzParser.TYPE_GROUP, save_to_file=True)

            # Проверяем, что приватные методы были вызваны с правильными параметрами
            parser._open_page.assert_called_once()
            parser._select_schedule_type.assert_called_once_with(MPEIRuzParser.TYPE_GROUP)
            parser._select_schedule_object.assert_called_once_with("ЭР-03-23", MPEIRuzParser.TYPE_GROUP)

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_teacher_schedule(self, mock_firefox_options):
        """
        Тест парсинга расписания для преподавателя.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Патчим приватные методы парсера
        with patch.object(parser, '_open_page', return_value=True), \
                patch.object(parser, '_select_schedule_type', return_value=True), \
                patch.object(parser, '_select_schedule_object', return_value=True), \
                patch.object(parser, '_find_zero_week', return_value=True), \
                patch.object(parser, '_get_current_week_number', return_value=0), \
                patch.object(parser, '_parse_week_schedule', return_value=self.test_schedule), \
                patch.object(parser, '_go_to_next_week', return_value=True), \
                patch.object(parser, '_save_schedule_to_json'):
            # Вызываем метод парсинга
            result = parser.parse("Иванов И.И.", schedule_type=MPEIRuzParser.TYPE_TEACHER, save_to_file=True)

            # Проверяем, что приватные методы были вызваны с правильными параметрами
            parser._open_page.assert_called_once()
            parser._select_schedule_type.assert_called_once_with(MPEIRuzParser.TYPE_TEACHER)
            parser._select_schedule_object.assert_called_once_with("Иванов И.И.", MPEIRuzParser.TYPE_TEACHER)

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_room_schedule(self, mock_firefox_options):
        """
        Тест парсинга расписания для аудитории.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Патчим приватные методы парсера
        with patch.object(parser, '_open_page', return_value=True), \
                patch.object(parser, '_select_schedule_type', return_value=True), \
                patch.object(parser, '_select_schedule_object', return_value=True), \
                patch.object(parser, '_find_zero_week', return_value=True), \
                patch.object(parser, '_get_current_week_number', return_value=0), \
                patch.object(parser, '_parse_week_schedule', return_value=self.test_schedule), \
                patch.object(parser, '_go_to_next_week', return_value=True), \
                patch.object(parser, '_save_schedule_to_json'):
            # Вызываем метод парсинга
            result = parser.parse("А-100", schedule_type=MPEIRuzParser.TYPE_ROOM, save_to_file=True)

            # Проверяем, что приватные методы были вызваны с правильными параметрами
            parser._open_page.assert_called_once()
            parser._select_schedule_type.assert_called_once_with(MPEIRuzParser.TYPE_ROOM)
            parser._select_schedule_object.assert_called_once_with("А-100", MPEIRuzParser.TYPE_ROOM)

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_by_date_range(self, mock_firefox_options):
        """
        Тест парсинга расписания за указанный период дат.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Патчим метод parse, чтобы он возвращал тестовое расписание
        with patch.object(parser, 'parse', return_value=self.test_schedule), \
                patch.object(parser, '_save_schedule_to_json'):
            # Вызываем метод парсинга по диапазону дат
            result = parser.parse_by_date_range(
                "ЭР-03-23",
                "01.04.2025",
                "10.04.2025",
                schedule_type=MPEIRuzParser.TYPE_GROUP,
                save_to_file=True
            )

            # Проверяем, что метод parse был вызван с правильными параметрами
            parser.parse.assert_called_once_with("ЭР-03-23", MPEIRuzParser.TYPE_GROUP, save_to_file=False)

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_error_handling(self, mock_firefox_options):
        """
        Тест обработки ошибок при парсинге.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Патчим метод _open_page, чтобы он возвращал False (ошибка)
        with patch.object(parser, '_open_page', return_value=False):
            # Вызываем метод парсинга
            result = parser.parse("ЭР-03-23", schedule_type=MPEIRuzParser.TYPE_GROUP)

            # Проверяем, что результат пустой (из-за ошибки)
            self.assertEqual(result, [])

            # Проверяем, что метод _open_page был вызван
            parser._open_page.assert_called_once()

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_parse_by_date_range_invalid_dates(self, mock_firefox_options):
        """
        Тест обработки некорректных дат при парсинге по диапазону.
        """
        # Настраиваем мок драйвера
        self._setup_mock_driver(self.mock_driver)

        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Тест с некорректным форматом даты
        result = parser.parse_by_date_range(
            "ЭР-03-23",
            "01-04-2025",  # Неверный формат даты
            "10.04.2025",
            schedule_type=MPEIRuzParser.TYPE_GROUP
        )

        # Проверяем, что результат пустой (из-за ошибки)
        self.assertEqual(result, [])

        # Тест с начальной датой позже конечной
        result = parser.parse_by_date_range(
            "ЭР-03-23",
            "20.04.2025",  # Дата позже конечной
            "10.04.2025",
            schedule_type=MPEIRuzParser.TYPE_GROUP
        )

        # Проверяем, что результат пустой (из-за ошибки)
        self.assertEqual(result, [])

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_cleanup_diagnostic_files(self, mock_firefox_options):
        """
        Тест очистки диагностических файлов.
        """
        # Создаем экземпляр парсера с включенной опцией очистки
        parser = MPEIRuzParser(headless=True, cleanup_files=True)

        # Создаем тестовые файлы в директории diagnostic_files
        test_files = ["test1.png", "test2.png"]
        for file in test_files:
            with open(os.path.join(self.diagnostic_dir, file), 'w') as f:
                f.write("test content")

        # Вызываем приватный метод очистки напрямую
        # Вместо мокирования os.remove, проверяем реальное удаление файлов
        parser._cleanup_diagnostic_files()

        # Проверяем, что файлы были удалены
        for file in test_files:
            self.assertFalse(os.path.exists(os.path.join(self.diagnostic_dir, file)))

    @patch('schedule_parser.ScheduleParser.FirefoxOptions')
    def test_save_diagnostic_screenshot(self, mock_firefox_options):
        """
        Тест сохранения диагностического скриншота.
        """
        # Создаем экземпляр парсера
        parser = MPEIRuzParser(headless=True)

        # Заменяем драйвер на наш мок напрямую
        parser.driver = self.mock_driver

        # Вызываем приватный метод сохранения скриншота
        screenshot_name = "test_screenshot.png"
        parser._save_diagnostic_screenshot(screenshot_name)

        # Проверяем, что метод save_screenshot был вызван с правильным путем
        self.mock_driver.save_screenshot.assert_called_once()


if __name__ == '__main__':
    unittest.main()
