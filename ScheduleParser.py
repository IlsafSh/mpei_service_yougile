import re
import requests
from bs4 import BeautifulSoup


class ScheduleParser:
    def __init__(self, html_content):
        """
        Инициализация парсера расписания.
        :param html_content: HTML-код страницы с расписанием.
        """
        self.response = requests.get(html_content)
        self.soup = BeautifulSoup(self.response.text, 'lxml')
        self.schedule = []
        self.weekdays = []

    @staticmethod
    def clean_text(text):
        """
        Удаляет лишние пробелы, символы \n, \r и табуляции.
        :param text: Исходный текст.
        :return: Очищенный текст.
        """
        return re.sub(r'\s+', ' ', text.replace("\n", "").replace("\r", "")).strip()

    def parse_header(self):
        """
        Парсинг заголовка таблицы (дни недели).
        """
        header_cells = self.soup.find_all('tr')[0].find_all('td')[1:]  # Пропускаем первый столбец
        self.weekdays = [self.clean_text(cell.text) for cell in header_cells]

    def parse_rows(self):
        """
        Парсинг строк с расписанием.
        """
        rows = self.soup.find_all('tr')[1:]  # Пропускаем строку с заголовками
        for row in rows:
            cells = row.find_all('td')
            time_info = self.clean_text(cells[0].text)  # Время пары (первый столбец)
            for i, cell in enumerate(cells[1:]):  # Пропускаем первый столбец с временем
                if len(self.schedule) <= i:  # Создаем словарь для нового дня недели
                    self.schedule.append({"day": self.weekdays[i], "lessons": []})

                if cell.text.strip():  # Если ячейка не пуста
                    # Извлечение информации о занятии
                    subject = self.clean_text(cell.find('strong').text) if cell.find('strong') else ""

                    # Извлечение типа занятия
                    contents = cell.contents
                    type_info = ""
                    for content in contents:
                        if isinstance(content, str) and any(keyword in content for keyword in
                                                            ["Лекция", "Практическое занятие", "Консультация",
                                                             "Лабораторная работа"]):
                            type_info = self.clean_text(content)
                            break

                    # Извлечение аудитории
                    room = self.clean_text(cell.find('a', href=True).text) if cell.find('a', href=True) else ""

                    # Извлечение преподавателя
                    lecturer = self.clean_text(cell.find_all('a')[-1].text) if cell.find_all('a') else ""

                    # Добавление информации о занятии
                    lesson_details = {
                        "time": time_info,
                        "subject": subject,
                        "type": type_info,
                        "room": room,
                        "lecturer": lecturer,
                    }
                    self.schedule[i]["lessons"].append(lesson_details)

    def parse(self):
        """
        Основной метод парсинга расписания.
        """
        self.parse_header()
        self.parse_rows()
        return self.schedule

    def display_schedule(self):
        """
        Вывод расписания в читаемом формате.
        """
        for day in self.schedule:
            print(f"{day['day']}:")
            for lesson in day['lessons']:
                print(
                    f"  {lesson['time']}: {lesson['subject']} ({lesson['type']}) в {lesson['room']}, {lesson['lecturer']}")