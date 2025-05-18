import time
import os
import re
import json
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


class MPEIRuzParser:
    """
    Универсальный парсер расписания с сайта БАРС МЭИ (https://bars.mpei.ru/bars_web/Open/RUZ/Timetable)
    с использованием Selenium для работы с интерактивными элементами.

    Поддерживает парсинг расписания для:
    - учебных групп
    - преподавателей
    - аудиторий

    Алгоритм парсинга:
    1. Находит нулевую учебную неделю
    2. Последовательно парсит каждую неделю от 0 до 16
    """

    # Типы расписания
    TYPE_GROUP = 'group'  # Расписание группы
    TYPE_TEACHER = 'teacher'  # Расписание преподавателя
    TYPE_ROOM = 'room'  # Расписание аудитории

    # Соответствие типов расписания значениям на сайте
    TYPE_MAP = {
        TYPE_GROUP: '3',  # Группа
        TYPE_TEACHER: '1',  # Преподаватель
        TYPE_ROOM: '2',  # Аудитория
    }

    # Соответствие типов расписания индексам элементов на странице
    TYPE_INDEX_MAP = {
        TYPE_GROUP: 12,  # Индекс элемента "Учебная группа"
        TYPE_TEACHER: 13,  # Индекс элемента "Преподаватель"
        TYPE_ROOM: 14,  # Индекс элемента "Аудитория"
    }

    # Академические звания и должности для идентификации преподавателей
    ACADEMIC_TITLES = [
        "проф.", "профессор",
        "доц.", "доцент",
        "ст.преп.", "старший преподаватель",
        "асс.", "ассистент",
        "преп.", "преподаватель"
    ]

    def __init__(self, headless=True, max_weeks=16, cleanup_files=True):
        """
        Инициализация парсера.

        Args:
            headless (bool): Запуск браузера в фоновом режиме без GUI
            max_weeks (int): Максимальное количество недель для парсинга (от 0 до max_weeks)
            cleanup_files (bool): Удалять ли вспомогательные файлы после завершения работы
        """
        # Создаем директорию для диагностических файлов
        self.diagnostic_dir = os.path.join(os.getcwd(), "diagnostic_files")
        os.makedirs(self.diagnostic_dir, exist_ok=True)

        # Настраиваем логирование
        self._setup_logging()

        self.logger.info("Инициализация парсера...")
        self.url = "https://bars.mpei.ru/bars_web/Open/RUZ/Timetable"
        self.max_weeks = max_weeks
        self.cleanup_files = cleanup_files

        # Настройка опций Firefox
        firefox_options = FirefoxOptions()
        if headless:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        firefox_options.set_preference("intl.accept_languages", "ru-RU, ru")

        # Инициализация драйвера Firefox
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.implicitly_wait(10)  # Увеличиваем время ожидания элементов
        self.wait = WebDriverWait(self.driver, 10)

    def _setup_logging(self):
        """Настройка логирования в файл"""
        self.logger = logging.getLogger('MPEIRuzParser')
        self.logger.setLevel(logging.DEBUG)

        # Создаем обработчик для записи в файл
        log_file = os.path.join(self.diagnostic_dir, 'parser.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Создаем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Создаем форматтер для логов
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Логирование настроено. Файл логов: {log_file}")

    def close(self):
        """Закрытие браузера и освобождение ресурсов."""
        self.logger.info("Закрытие браузера...")
        if self.driver:
            self.driver.quit()

        # Удаляем диагностические файлы, если они есть и если включена опция очистки
        if self.cleanup_files:
            self._cleanup_diagnostic_files()

    def parse(self, name, schedule_type=TYPE_GROUP, save_to_file=True, filename=None):
        """
        Универсальный метод для парсинга расписания.

        Args:
            name (str): Название группы, ФИО преподавателя или номер аудитории
            schedule_type (str): Тип расписания (group, teacher, room)
            save_to_file (bool): Сохранять результат в JSON-файл
            filename (str): Имя файла для сохранения (если None, генерируется автоматически)

        Returns:
            list: Список дней с расписанием занятий
        """
        self.logger.info(f"Начинаем парсинг расписания для {schedule_type}: {name}...")

        try:
            # Открываем страницу расписания
            if not self._open_page():
                self.logger.error("Не удалось открыть страницу расписания")
                return []

            # Выбираем тип расписания и объект
            if not self._select_schedule_type(schedule_type):
                self.logger.error(f"Не удалось выбрать тип расписания: {schedule_type}")
                return []

            if not self._select_schedule_object(name, schedule_type):
                self.logger.error(f"Не удалось выбрать объект: {name}")
                return []

            # Создаем список для хранения всего расписания
            all_schedule = []

            # Находим нулевую учебную неделю
            if not self._find_zero_week():
                self.logger.warning("Не удалось найти нулевую учебную неделю, используем текущую неделю")

            # Получаем номер текущей недели
            current_week_number = self._get_current_week_number()
            if current_week_number is None:
                self.logger.error("Не удалось определить номер текущей недели")
                return []

            self.logger.info(f"Текущая неделя: {current_week_number}")

            # Парсим последовательно каждую неделю от текущей до max_weeks
            for week in range(current_week_number, self.max_weeks + 1):
                self.logger.info(f"Парсинг недели {week}")

                # Парсим текущую неделю
                week_schedule = self._parse_week_schedule(week, schedule_type, name)
                if week_schedule:
                    all_schedule.extend(week_schedule)

                # Переходим к следующей неделе, если это не последняя неделя
                if week < self.max_weeks:
                    if not self._go_to_next_week():
                        self.logger.warning(f"Не удалось перейти к неделе {week + 1}")
                        break

            # Проверяем, что расписание не пустое
            if not all_schedule:
                self.logger.warning("Внимание: расписание пустое. Возможно, проблема с извлечением данных.")
                return []

            # Выводим информацию о полученном расписании
            self.logger.info(f"Получено расписание на {len(all_schedule)} дней")

            # Сохраняем расписание в JSON
            if save_to_file:
                if not filename:
                    # Генерируем имя файла на основе типа расписания и названия объекта
                    filename = f"schedule_{schedule_type}_{name.replace(' ', '_')}.json"

                self._save_schedule_to_json(all_schedule, filename)
                self.logger.info(f"Расписание сохранено в файл: {filename}")

            return all_schedule

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге расписания: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error.png")
            return []

    def parse_by_date_range(self, name, start_date, end_date, schedule_type=TYPE_GROUP, save_to_file=True,
                            filename=None):
        """
        Парсинг расписания за указанный период дат.

        Args:
            name (str): Название группы, ФИО преподавателя или номер аудитории
            start_date (str): Начальная дата в формате 'DD.MM.YYYY'
            end_date (str): Конечная дата в формате 'DD.MM.YYYY'
            schedule_type (str): Тип расписания (group, teacher, room)
            save_to_file (bool): Сохранять результат в JSON-файл
            filename (str): Имя файла для сохранения (если None, генерируется автоматически)

        Returns:
            list: Список дней с расписанием занятий за указанный период
        """
        self.logger.info(
            f"Начинаем парсинг расписания для {schedule_type}: {name} за период с {start_date} по {end_date}...")

        try:
            # Преобразуем строки дат в объекты datetime
            try:
                start_date_obj = datetime.strptime(start_date, '%d.%m.%Y')
                end_date_obj = datetime.strptime(end_date, '%d.%m.%Y')

                # Проверяем корректность диапазона дат
                if start_date_obj > end_date_obj:
                    self.logger.error("Начальная дата не может быть позже конечной даты")
                    return []

                # Ограничиваем период парсинга разумными пределами (не более 6 месяцев)
                max_period = timedelta(days=180)
                if end_date_obj - start_date_obj > max_period:
                    self.logger.warning(f"Указан слишком большой период. Ограничиваем до {max_period.days} дней")
                    end_date_obj = start_date_obj + max_period
                    end_date = end_date_obj.strftime('%d.%m.%Y')

            except ValueError as e:
                self.logger.error(f"Неверный формат даты: {e}", exc_info=True)
                return []

            # Получаем полное расписание
            all_schedule = self.parse(name, schedule_type, save_to_file=False)

            if not all_schedule:
                self.logger.error("Не удалось получить расписание")
                return []

            # Фильтруем расписание по указанному диапазону дат
            filtered_schedule = []

            for day in all_schedule:
                # Извлекаем дату из заголовка дня
                try:
                    # Формат заголовка может быть разным, пробуем разные варианты
                    day_text = day["day"]

                    # Вариант 1: "Пн, 07 апреля"
                    date_match = re.search(r'(\d{1,2})\s+(\w+)', day_text)
                    if date_match:
                        day_num = int(date_match.group(1))
                        month_name = date_match.group(2).lower()

                        # Словарь соответствия названий месяцев их номерам
                        month_map = {
                            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
                        }

                        if month_name in month_map:
                            month_num = month_map[month_name]
                            # Предполагаем текущий год, если не указан
                            year = datetime.now().year

                            # Создаем объект даты
                            day_date = datetime(year, month_num, day_num)

                            # Если дата в указанном диапазоне, добавляем день в отфильтрованное расписание
                            if start_date_obj <= day_date <= end_date_obj:
                                filtered_schedule.append(day)
                    else:
                        self.logger.warning(f"Не удалось извлечь дату из заголовка дня: {day_text}")

                except Exception as e:
                    self.logger.error(f"Ошибка при обработке даты дня: {e}", exc_info=True)

            self.logger.info(f"Отфильтровано расписание на {len(filtered_schedule)} дней в указанном диапазоне")

            # Сохраняем отфильтрованное расписание в JSON
            if save_to_file and filtered_schedule:
                if not filename:
                    # Генерируем имя файла на основе типа расписания, названия объекта и диапазона дат
                    filename = f"schedule_{schedule_type}_{name.replace(' ', '_')}_{start_date.replace('.', '_')}-{end_date.replace('.', '_')}.json"

                self._save_schedule_to_json(filtered_schedule, filename)
                self.logger.info(f"Отфильтрованное расписание сохранено в файл: {filename}")

            return filtered_schedule

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге расписания за период: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_date_range.png")
            return []

    def _open_page(self):
        """
        Открытие страницы расписания.

        Returns:
            bool: True, если страница успешно открыта, иначе False
        """
        try:
            self.logger.info(f"Открываем страницу: {self.url}")
            self.driver.get(self.url)
            time.sleep(3)  # Даем странице полностью загрузиться

            # Проверяем, что страница загрузилась
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                return True
            except TimeoutException:
                self.logger.error("Таймаут при ожидании загрузки страницы")
                self._save_diagnostic_screenshot("timeout_page.png")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка при открытии страницы: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_open_page.png")
            return False

    def _select_schedule_type(self, schedule_type):
        """
        Выбор типа расписания (группа, преподаватель, аудитория).

        Args:
            schedule_type (str): Тип расписания (group, teacher, room)

        Returns:
            bool: True, если тип расписания успешно выбран, иначе False
        """
        try:
            self.logger.info(f"Выбираем тип расписания: {schedule_type}")

            # Проверяем корректность типа расписания
            if schedule_type not in [self.TYPE_GROUP, self.TYPE_TEACHER, self.TYPE_ROOM]:
                self.logger.error(f"Неверный тип расписания: {schedule_type}")
                return False

            # Сохраняем скриншот для диагностики перед выбором типа
            self._save_diagnostic_screenshot("before_select_type.png")

            # Метод 1: Прямое взаимодействие с DOM через JavaScript
            try:
                self.logger.debug("Метод 1: Прямое взаимодействие с DOM через JavaScript")

                # Определяем значение data-receivertype в зависимости от типа расписания
                receiver_type = self.TYPE_MAP.get(schedule_type, '3')

                # Выполняем JavaScript для выбора типа расписания
                script = f"""
                // Функция для поиска и клика по элементу с нужным data-receivertype
                function selectReceiverType() {{
                    // Ищем все ссылки с атрибутом data-receivertype
                    var links = document.querySelectorAll('a[data-receivertype]');
                    console.log('Найдено ссылок с data-receivertype:', links.length);

                    // Ищем нужную ссылку
                    for (var i = 0; i < links.length; i++) {{
                        if (links[i].getAttribute('data-receivertype') === '{receiver_type}') {{
                            console.log('Найдена нужная ссылка:', links[i].textContent);
                            links[i].click();
                            return true;
                        }}
                    }}

                    // Если не нашли по data-receivertype, ищем по тексту
                    var allLinks = document.querySelectorAll('a');
                    var searchText = '';

                    if ('{schedule_type}' === 'group') searchText = 'Учебная группа';
                    else if ('{schedule_type}' === 'teacher') searchText = 'Преподаватель';
                    else if ('{schedule_type}' === 'room') searchText = 'Аудитория';

                    for (var i = 0; i < allLinks.length; i++) {{
                        if (allLinks[i].textContent.includes(searchText)) {{
                            console.log('Найдена ссылка по тексту:', allLinks[i].textContent);
                            allLinks[i].click();
                            return true;
                        }}
                    }}

                    return false;
                }}

                // Пытаемся выбрать тип расписания
                return selectReceiverType();
                """

                result = self.driver.execute_script(script)
                if result:
                    self.logger.info("Тип расписания выбран через JavaScript")
                    time.sleep(2)
                    return True
                else:
                    self.logger.warning("Не удалось найти элемент для выбора типа расписания через JavaScript")

            except Exception as e:
                self.logger.warning(f"Метод 1 не сработал: {e}")

            # Метод 2: Прямой клик по элементам
            try:
                self.logger.debug("Метод 2: Прямой клик по элементам")

                # Определяем, какой элемент нужно выбрать
                if schedule_type == self.TYPE_GROUP:
                    selector = "//a[text()='Учебная группа']"
                elif schedule_type == self.TYPE_TEACHER:
                    selector = "//a[text()='Преподаватель']"
                elif schedule_type == self.TYPE_ROOM:
                    selector = "//a[text()='Аудитория']"
                else:
                    return False

                # Пытаемся найти элемент напрямую без открытия выпадающего списка
                self.logger.debug(f"Ищем элемент типа расписания по селектору: {selector}")
                type_option = self.driver.find_element(By.XPATH, selector)
                self.logger.debug(f"Найден элемент типа расписания, кликаем...")
                type_option.click()
                time.sleep(2)
                return True

            except Exception as e2:
                self.logger.warning(f"Метод 2 не сработал: {e2}")

            # Метод 3: Имитация пользовательских действий
            try:
                self.logger.debug("Метод 3: Имитация пользовательских действий")

                # Сначала кликаем по выпадающему списку
                dropdown_selectors = [
                    "span.select2-selection__rendered",
                    "button.select2-selection__rendered",
                    ".select2-selection",
                    "#ddlReciever + span"
                ]

                dropdown_clicked = False
                for selector in dropdown_selectors:
                    try:
                        dropdown = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        dropdown.click()
                        self.logger.debug(f"Кликнули по выпадающему списку с селектором: {selector}")
                        dropdown_clicked = True
                        time.sleep(2)
                        break
                    except:
                        self.logger.debug(f"Не удалось кликнуть по селектору: {selector}")

                if not dropdown_clicked:
                    self.logger.warning("Не удалось кликнуть по выпадающему списку")
                    return False

                # Сохраняем скриншот после клика по выпадающему списку
                self._save_diagnostic_screenshot("after_dropdown_click_method3.png")

                # Теперь пытаемся найти и кликнуть по нужному элементу в выпадающем списке
                option_selectors = [
                    f"//li[contains(text(), 'Учебная группа')]",
                    f"//li[contains(text(), 'Преподаватель')]",
                    f"//li[contains(text(), 'Аудитория')]"
                ]

                option_index = 0
                if schedule_type == self.TYPE_TEACHER:
                    option_index = 1
                elif schedule_type == self.TYPE_ROOM:
                    option_index = 2

                try:
                    option = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, option_selectors[option_index]))
                    )
                    option.click()
                    self.logger.debug(f"Кликнули по опции в выпадающем списке")
                    time.sleep(2)
                    return True
                except Exception as e:
                    self.logger.warning(f"Не удалось кликнуть по опции в выпадающем списке: {e}")
                    return False

            except Exception as e3:
                self.logger.warning(f"Метод 3 не сработал: {e3}")

            return False

        except Exception as e:
            self.logger.error(f"Ошибка при выборе типа расписания: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_select_type.png")
            return False

    def _select_schedule_object(self, name, schedule_type):
        """
        Выбор объекта расписания (конкретной группы, преподавателя или аудитории).

        Args:
            name (str): Название объекта
            schedule_type (str): Тип расписания (group, teacher, room)

        Returns:
            bool: True, если объект успешно выбран, иначе False
        """
        try:
            self.logger.info(f"Выбираем объект: {name}")

            # Проверяем, что имя объекта не пустое
            if not name or not name.strip():
                self.logger.error("Имя объекта не может быть пустым")
                return False

            # Метод 1: Использование select2
            try:
                self.logger.debug("Метод 1: Использование select2")

                # Находим поле ввода select2
                select2_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".select2-search__field"))
                )

                # Очищаем поле и вводим название объекта
                select2_input.clear()
                select2_input.send_keys(name)
                time.sleep(1)

                # Нажимаем Enter для выбора первого совпадения
                select2_input.send_keys(Keys.ENTER)
                time.sleep(2)

                # Сохраняем скриншот после выбора объекта
                self._save_diagnostic_screenshot("after_select_object_method1.png")

                self.logger.info("Объект выбран через select2")

            except Exception as e:
                self.logger.warning(f"Метод 1 не сработал: {e}")
                self.logger.debug("Пробуем метод 2: Установка значения через JavaScript")

                # Метод 2: Установка значения через JavaScript
                try:
                    # Определяем ID селекта в зависимости от типа расписания
                    select_id = "ddlReciever"

                    # Устанавливаем значение через JavaScript
                    script = f"""
                    var select = document.querySelector('#ddlReciever');
                    if (select) {{
                        // Создаем новую опцию
                        var option = new Option('{name}', '{name}', true, true);
                        // Добавляем опцию в селект
                        select.appendChild(option);
                        // Обновляем select2
                        $(select).trigger('change');
                        return true;
                    }}
                    return false;
                    """
                    result = self.driver.execute_script(script)
                    if not result:
                        self.logger.warning("Не удалось установить значение через JavaScript")
                        return False

                    self.logger.info("Значение установлено через JavaScript")
                    time.sleep(2)

                except Exception as e2:
                    self.logger.warning(f"Метод 2 не сработал: {e2}")
                    self.logger.debug("Пробуем метод 3: Прямой ввод в поле без select2")

                    # Метод 3: Прямой ввод в поле без использования select2
                    try:
                        # Ищем любое доступное поле ввода
                        input_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                        input_field.clear()
                        input_field.send_keys(name)
                        time.sleep(1)
                        input_field.send_keys(Keys.ENTER)
                        time.sleep(2)
                        self.logger.info("Значение введено напрямую в поле ввода")
                    except Exception as e3:
                        self.logger.warning(f"Метод 3 не сработал: {e3}")
                        return False

            # Нажимаем кнопку "Просмотр"
            self.logger.debug("Ищем кнопку 'Просмотр'...")
            try:
                view_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Просмотр')]"))
                )
                self.logger.debug("Нажимаем кнопку 'Просмотр'...")
                view_button.click()
            except Exception as e:
                self.logger.warning(f"Не удалось найти кнопку 'Просмотр': {e}")
                self.logger.debug("Пробуем найти кнопку по CSS-селектору...")

                try:
                    view_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary"))
                    )
                    self.logger.debug("Нажимаем кнопку по CSS-селектору...")
                    view_button.click()
                except Exception as e2:
                    self.logger.warning(f"Не удалось найти кнопку по CSS-селектору: {e2}")

                    # Пробуем использовать JavaScript для нажатия кнопки
                    self.logger.debug("Пробуем нажать кнопку через JavaScript...")
                    try:
                        self.driver.execute_script("""
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            if (buttons[i].textContent.includes('Просмотр')) {
                                buttons[i].click();
                                return true;
                            }
                        }
                        return false;
                        """)
                        self.logger.info("Кнопка нажата через JavaScript")
                    except Exception as e3:
                        self.logger.error(f"Не удалось нажать кнопку через JavaScript: {e3}")
                        return False

            # Ожидаем загрузки расписания
            self.logger.info("Ожидаем загрузки расписания...")
            time.sleep(5)  # Увеличиваем время ожидания загрузки расписания

            # Сохраняем скриншот после выбора объекта
            self._save_diagnostic_screenshot("after_select_object.png")

            # Проверяем, что расписание загрузилось
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
                self.logger.info("Расписание загружено успешно")
                return True
            except TimeoutException:
                self.logger.error("Таймаут при ожидании загрузки расписания")
                self._save_diagnostic_screenshot("timeout_load_schedule.png")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка при выборе объекта {name}: {e}", exc_info=True)
            # Сохраняем скриншот для отладки
            self._save_diagnostic_screenshot("error_select_object.png")
            return False

    def _find_zero_week(self):
        """
        Поиск нулевой учебной недели.

        Returns:
            bool: True, если нулевая неделя найдена, иначе False
        """
        try:
            self.logger.info("Ищем нулевую учебную неделю")

            # Получаем номер текущей недели
            current_week = self._get_current_week_number()
            if current_week is None:
                # Проверяем, не находимся ли мы уже на нулевой неделе с пустым заголовком
                if self._check_zero_week_by_empty_header():
                    self.logger.info("Обнаружена нулевая неделя с пустым заголовком")
                    return True
                self.logger.error("Не удалось определить номер текущей недели")
                return False

            self.logger.info(f"Текущая неделя: {current_week}")

            # Если уже на нулевой неделе, возвращаем True
            if current_week == 0:
                self.logger.info("Уже находимся на нулевой неделе")
                return True

            # Переходим к предыдущим неделям, пока не найдем нулевую
            attempts = 0
            max_attempts = 20  # Ограничиваем количество попыток

            while current_week > 0 and attempts < max_attempts:
                if not self._go_to_prev_week():
                    self.logger.warning("Не удалось перейти к предыдущей неделе")
                    return False

                # Проверяем, не находимся ли мы на нулевой неделе с пустым заголовком
                if self._check_zero_week_by_empty_header():
                    self.logger.info("Обнаружена нулевая неделя с пустым заголовком")
                    return True

                current_week = self._get_current_week_number()
                if current_week is None:
                    # Если не удалось определить номер недели, проверяем, не нулевая ли это неделя
                    if self._check_zero_week_by_empty_header():
                        self.logger.info("Обнаружена нулевая неделя с пустым заголовком")
                        return True
                    self.logger.error("Не удалось определить номер недели после перехода")
                    return False

                self.logger.info(f"Текущая неделя после перехода: {current_week}")
                attempts += 1

                if current_week == 0:
                    self.logger.info("Нулевая неделя найдена")
                    return True

            self.logger.warning(f"Не удалось найти нулевую неделю после {attempts} попыток")
            return False

        except Exception as e:
            self.logger.error(f"Ошибка при поиске нулевой недели: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_find_zero_week.png")
            return False

    def _check_zero_week_by_empty_header(self):
        """
        Проверка, является ли текущая неделя нулевой по пустому заголовку.

        Returns:
            bool: True, если это нулевая неделя с пустым заголовком, иначе False
        """
        try:
            # Находим заголовок с номером недели
            week_headers = self.driver.find_elements(By.XPATH,
                                                     "//td[@class='th-primary' and contains(@style, 'min-width: 55px')]")

            if not week_headers:
                self.logger.warning("Не найден заголовок с номером недели")
                return False

            # Проверяем, пустой ли текст заголовка
            week_header = week_headers[0]
            week_text = week_header.text.strip()

            # Если текст пустой или содержит только пробельные символы, это может быть нулевая неделя
            if not week_text:
                self.logger.info("Обнаружен пустой заголовок недели, вероятно это нулевая неделя")

                # Дополнительная проверка: пытаемся перейти к предыдущей неделе
                # Если кнопка "Предыдущая" неактивна, то это подтверждает, что мы на нулевой неделе
                try:
                    prev_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Предыдущая')]")
                    if not prev_button.is_enabled():
                        self.logger.info("Кнопка 'Предыдущая' неактивна, подтверждена нулевая неделя")
                        return True
                except:
                    # Если кнопка не найдена или возникла ошибка, предполагаем, что это нулевая неделя
                    self.logger.info("Не удалось найти кнопку 'Предыдущая', предполагаем нулевую неделю")
                    return True

                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка при проверке нулевой недели по пустому заголовку: {e}", exc_info=True)
            return False

    def _get_current_week_number(self):
        """
        Получение номера текущей недели.

        Returns:
            int: Номер текущей недели или None, если не удалось определить
        """
        try:
            # Находим заголовок с номером недели
            week_headers = self.driver.find_elements(By.XPATH,
                                                     "//td[@class='th-primary' and contains(@style, 'min-width: 55px')]")

            if not week_headers:
                self.logger.warning("Не найден заголовок с номером недели")
                return None

            week_header = week_headers[0]

            # Извлекаем номер недели из текста
            week_text = week_header.text.strip()
            self.logger.debug(f"Текст заголовка недели: '{week_text}'")

            # Проверяем на пустой текст (возможно, это нулевая неделя)
            if not week_text:
                self.logger.info("Пустой текст заголовка недели, возможно это нулевая неделя")

                # Дополнительная проверка: пытаемся перейти к предыдущей неделе
                # Если кнопка "Предыдущая" неактивна, то это подтверждает, что мы на нулевой неделе
                try:
                    prev_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Предыдущая')]")
                    if not prev_button.is_enabled():
                        self.logger.info("Кнопка 'Предыдущая' неактивна, подтверждена нулевая неделя")
                        return 0
                except:
                    # Если кнопка не найдена или возникла ошибка, предполагаем, что это нулевая неделя
                    self.logger.info("Не удалось найти кнопку 'Предыдущая', предполагаем нулевую неделю")
                    return 0

                return 0

            # Используем регулярное выражение для извлечения номера недели
            week_match = re.search(r'(\d+)\s*н\.', week_text)
            if not week_match:
                self.logger.warning(f"Не удалось извлечь номер недели из текста: '{week_text}'")
                return None

            week_number = int(week_match.group(1))
            self.logger.debug(f"Извлечен номер недели: {week_number}")
            return week_number

        except Exception as e:
            self.logger.error(f"Ошибка при получении номера текущей недели: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_get_week_number.png")
            return None

    def _go_to_next_week(self):
        """
        Переход к следующей неделе.

        Returns:
            bool: True, если переход успешен, иначе False
        """
        try:
            self.logger.info("Переходим к следующей неделе")

            # Находим кнопку перехода к следующей неделе
            next_week_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Следующая')]"))
            )
            next_week_button.click()
            time.sleep(2)
            self.logger.info("Переход к следующей неделе выполнен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при переходе к следующей неделе: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_next_week.png")
            return False

    def _go_to_prev_week(self):
        """
        Переход к предыдущей неделе.

        Returns:
            bool: True, если переход успешен, иначе False
        """
        try:
            self.logger.info("Переходим к предыдущей неделе")

            # Находим кнопку перехода к предыдущей неделе
            prev_week_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Предыдущая')]"))
            )

            # Проверяем, активна ли кнопка
            if not prev_week_button.is_enabled():
                self.logger.info("Кнопка 'Предыдущая' неактивна, возможно мы уже на нулевой неделе")
                return False

            prev_week_button.click()
            time.sleep(2)
            self.logger.info("Переход к предыдущей неделе выполнен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при переходе к предыдущей неделе: {e}", exc_info=True)
            self._save_diagnostic_screenshot("error_prev_week.png")
            return False

    def _parse_week_schedule(self, week_number, schedule_type=TYPE_GROUP, object_name=None):
        """
        Парсинг расписания текущей отображаемой недели.

        Args:
            week_number (int): Номер недели
            schedule_type (str): Тип расписания (group, teacher, room)
            object_name (str): Название объекта (группы, преподавателя, аудитории)

        Returns:
            list: Список дней с расписанием занятий
        """
        schedule = []

        try:
            self.logger.info(f"Парсим расписание для недели {week_number}")

            # Сохраняем HTML страницы для диагностики
            self._save_diagnostic_html(f"week_{week_number}.html")

            # Делаем скриншот для визуальной диагностики
            self._save_diagnostic_screenshot(f"week_{week_number}.png")

            # Проверяем наличие таблицы расписания с увеличенным таймаутом
            try:
                self.logger.debug("Ожидаем появления таблицы расписания...")
                table = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
                )
                self.logger.debug(f"Таблица найдена: {table.tag_name}")
            except TimeoutException:
                self.logger.error("Таблица расписания не найдена после ожидания")
                return []

            # Получаем все строки таблицы
            rows = table.find_elements(By.TAG_NAME, "tr")
            self.logger.debug(f"Найдено строк в таблице: {len(rows)}")

            if len(rows) == 0:
                self.logger.warning("В таблице нет строк")
                return []

            # Получаем заголовки дней недели из первой строки
            header_row = rows[0]
            day_headers = header_row.find_elements(By.TAG_NAME, "td")

            # Пропускаем первую ячейку с номером недели
            day_headers = day_headers[1:]

            self.logger.debug(f"Найдено заголовков дней: {len(day_headers)}")

            # Создаем словарь для хранения дней недели
            days_dict = {}

            for i, header in enumerate(day_headers):
                day_text = header.text.strip()
                self.logger.debug(f"Заголовок дня {i + 1}: {day_text}")

                days_dict[i] = {
                    "day": day_text,
                    "week": week_number,
                    "lessons": []
                }

            # Обрабатываем строки с парами (начиная со второй строки)
            for i in range(1, len(rows)):
                row = rows[i]
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) <= 1:
                    self.logger.debug(f"Строка {i + 1} не содержит ячеек с занятиями")
                    continue

                # Получаем время пары из первой ячейки
                time_cell = cells[0]
                time_text = time_cell.text.strip()

                # Извлекаем время начала и окончания
                time_parts = time_text.split('\n')
                if len(time_parts) >= 4:
                    time_range = f"{time_parts[1]}-{time_parts[3]}"
                else:
                    time_range = time_text

                self.logger.debug(f"Время пары: {time_range}")

                # Обрабатываем ячейки с занятиями для каждого дня
                for day_idx in range(len(day_headers)):
                    if day_idx + 1 < len(cells):
                        lesson_cell = cells[day_idx + 1]
                        lesson_text = lesson_cell.text.strip()

                        if lesson_text:
                            self.logger.debug(f"Занятие для дня {day_idx + 1}: {lesson_text}")

                            # Получаем HTML-код ячейки для более точного парсинга
                            lesson_html = lesson_cell.get_attribute('innerHTML')

                            # Используем BeautifulSoup для парсинга HTML
                            soup = BeautifulSoup(lesson_html, 'html.parser')

                            # Извлекаем название предмета из тега strong
                            subject_elem = soup.find('strong')
                            if subject_elem:
                                subject = subject_elem.text.strip()
                            else:
                                # Если тег strong не найден, пытаемся извлечь название из текста
                                subject = lesson_text.split('\n')[0] if '\n' in lesson_text else lesson_text

                            # Извлекаем тип занятия из текста между тегом strong и первой ссылкой
                            lesson_type = self._extract_lesson_type_from_html(soup)

                            # Пытаемся найти аудиторию
                            room = ""
                            room_link = soup.find('a')
                            if room_link:
                                room = room_link.text.strip()
                            else:
                                # Если ссылки нет, пытаемся извлечь аудиторию из текста
                                room_match = lesson_text.split('\n')
                                if len(room_match) > 1:
                                    for line in room_match:
                                        if "Корпус" in line:
                                            room = line.strip()
                                            break

                            # Извлекаем информацию о преподавателе
                            teacher = ""
                            if schedule_type != self.TYPE_TEACHER:  # Не извлекаем преподавателя для расписания преподавателя
                                teacher = self._extract_teacher_info(lesson_text, lesson_type, object_name)

                            # Добавляем занятие в расписание соответствующего дня
                            lesson_info = {
                                "time": time_range,
                                "subject": subject,
                                "type": lesson_type,
                                "room": room
                            }

                            # Добавляем информацию о преподавателе для расписания групп и аудиторий
                            if schedule_type != self.TYPE_TEACHER:
                                lesson_info["teacher"] = teacher

                            days_dict[day_idx]["lessons"].append(lesson_info)
                            self.logger.debug(f"Занятие добавлено в расписание дня {day_idx + 1}")

            # Преобразуем словарь дней в список и фильтруем дни без занятий
            schedule = [day for day in days_dict.values() if day["lessons"]]
            self.logger.info(f"Итоговое количество дней с занятиями: {len(schedule)}")

            return schedule

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге недели {week_number}: {e}", exc_info=True)
            self._save_diagnostic_screenshot(f"error_parse_week_{week_number}.png")
            return []

    def _extract_lesson_type_from_html(self, soup):
        """
        Извлечение типа занятия из HTML-кода ячейки.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup с HTML-кодом ячейки

        Returns:
            str: Тип занятия
        """
        try:
            # Находим тег strong (название предмета)
            subject_elem = soup.find('strong')
            if not subject_elem:
                return ""

            # Находим текст между тегом strong и первой ссылкой
            # Это будет текст, который идет после названия предмета и до аудитории
            lesson_type = ""

            # Получаем следующий элемент после strong
            next_elem = subject_elem.next_sibling

            # Собираем весь текст до первой ссылки
            while next_elem and not (hasattr(next_elem, 'name') and next_elem.name == 'a'):
                if isinstance(next_elem, str):
                    lesson_type += next_elem
                elif hasattr(next_elem, 'name') and next_elem.name == 'br':
                    lesson_type += " "
                next_elem = next_elem.next_sibling

            # Очищаем и форматируем результат
            lesson_type = re.sub(r'\s+', ' ', lesson_type).strip()

            # Если тип занятия не найден, возвращаем ""
            if not lesson_type:
                return ""

            return lesson_type

        except Exception as e:
            self.logger.error(f"Ошибка при извлечении типа занятия из HTML: {e}", exc_info=True)
            return ""  # Возвращаем значение по умолчанию в случае ошибки

    def _extract_teacher_info(self, lesson_text, lesson_type, object_name=None):
        """
        Извлечение информации о преподавателе из текста занятия.

        Args:
            lesson_text (str): Полный текст ячейки занятия
            lesson_type (str): Тип занятия
            object_name (str): Название объекта (группы, преподавателя, аудитории)

        Returns:
            str: Информация о преподавателе или пустая строка
        """
        try:
            # Разбиваем текст на строки
            lines = lesson_text.split('\n')

            # Фильтруем строки, исключая название предмета, тип занятия и аудиторию
            filtered_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Исключаем строки с аудиторией
                if "Корпус" in line:
                    continue

                # Исключаем строки, которые совпадают с типом занятия
                if line == lesson_type:
                    continue

                # Исключаем строки, которые совпадают с названием объекта (группы)
                if object_name and line == object_name:
                    continue

                filtered_lines.append(line)

            # Ищем строку, которая может быть преподавателем
            for line in filtered_lines:
                # Проверяем наличие академических званий или должностей
                for title in self.ACADEMIC_TITLES:
                    if title in line:
                        return line

                # Проверяем формат ФИО (Фамилия И.О.)
                if re.search(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.\b', line):
                    return line

                # Проверяем формат ФИО (Фамилия Имя Отчество)
                if re.search(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b', line):
                    return line

            # Если не нашли явного указания на преподавателя, возвращаем пустую строку
            return ""

        except Exception as e:
            self.logger.error(f"Ошибка при извлечении информации о преподавателе: {e}", exc_info=True)
            return ""  # Возвращаем пустую строку в случае ошибки

    def _save_schedule_to_json(self, schedule, filename):
        """
        Сохранение расписания в JSON-файл.

        Args:
            schedule (list): Список дней с расписанием
            filename (str): Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Расписание сохранено в файл: {filename}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении расписания в файл: {e}", exc_info=True)

    def _save_diagnostic_screenshot(self, filename):
        """
        Сохранение скриншота для диагностики.

        Args:
            filename (str): Имя файла
        """
        try:
            filepath = os.path.join(self.diagnostic_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.debug(f"Скриншот сохранен в файл: {filepath}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении скриншота: {e}", exc_info=True)

    def _save_diagnostic_html(self, filename):
        """
        Сохранение HTML-кода страницы для диагностики.

        Args:
            filename (str): Имя файла
        """
        try:
            filepath = os.path.join(self.diagnostic_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.debug(f"HTML-код страницы сохранен в файл: {filepath}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении HTML-кода страницы: {e}", exc_info=True)

    def _cleanup_diagnostic_files(self):
        """Удаление диагностических файлов."""
        try:
            if os.path.exists(self.diagnostic_dir):
                # Сохраняем файл логов
                log_file = os.path.join(self.diagnostic_dir, 'parser.log')
                has_log_file = os.path.exists(log_file)

                if has_log_file:
                    # Создаем временную копию файла логов
                    temp_log = os.path.join(os.getcwd(), 'temp_parser.log')
                    with open(log_file, 'r', encoding='utf-8') as src:
                        with open(temp_log, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())

                # Удаляем все файлы, кроме логов
                for filename in os.listdir(self.diagnostic_dir):
                    file_path = os.path.join(self.diagnostic_dir, filename)
                    if os.path.isfile(file_path) and filename != 'parser.log':
                        os.remove(file_path)
                        self.logger.debug(f"Удален файл: {file_path}")

                # Если директория пуста (нет файла логов), удаляем ее
                if not has_log_file and not os.listdir(self.diagnostic_dir):
                    os.rmdir(self.diagnostic_dir)
                    self.logger.info(f"Удалена директория: {self.diagnostic_dir}")

                self.logger.info("Диагностические файлы очищены")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке диагностических файлов: {e}", exc_info=True)
