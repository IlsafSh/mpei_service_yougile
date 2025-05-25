#!/usr/bin/env python3
"""
Модуль для запуска всех тестов проекта.

Этот модуль позволяет запускать все тесты проекта одной командой:
python -m tests.test_all

Тесты запускаются в следующем порядке:
1. Тесты API YouGile
2. Тесты парсера расписания
3. Тесты анализатора расписания
"""

import unittest
import os
import sys
import logging

# Отключаем логирование во время тестов
logging.basicConfig(level=logging.CRITICAL)

def run_all_tests():
    """
    Запускает все тесты проекта и выводит результаты.
    """
    # Создаем директорию для диагностических файлов, если она не существует
    diagnostic_dir = os.path.join(os.getcwd(), "diagnostic_files")
    os.makedirs(diagnostic_dir, exist_ok=True)
    
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()
    
    # Создаем набор тестов
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты из текущей директории
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Добавляем тесты API YouGile
    yougile_tests = loader.discover(tests_dir, pattern="test_yougile_api.py")
    test_suite.addTest(yougile_tests)
    
    # Добавляем тесты парсера расписания
    parser_tests = loader.discover(tests_dir, pattern="test_schedule_parser.py")
    test_suite.addTest(parser_tests)
    
    # Добавляем тесты анализатора расписания
    analyzer_tests = loader.discover(tests_dir, pattern="test_schedule_analyzer.py")
    test_suite.addTest(analyzer_tests)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим итоговую статистику
    print("\n=== Итоговая статистика тестирования ===")
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Неудач: {len(result.failures)}")
    
    # Возвращаем код завершения
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
