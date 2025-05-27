import json  # Импортируем модуль для работы с JSON
import os  # Импортируем модуль для работы с операционной системой
from datetime import datetime  # Импортируем класс для работы с датой и временем

class JsonTermManager:  # Класс для управления терминами в JSON формате
    def __init__(self):  # Конструктор класса
        self.db_folder = 'db'  # Папка для хранения базы данных
        self.db_file = 'db_terms.json'  # Имя файла базы данных
        self.db_path = os.path.join(self.db_folder, self.db_file)  # Полный путь к файлу базы данных
        self._ensure_db_exists()  # Вызываем метод для проверки существования базы данных

    def _ensure_db_exists(self):  # Приватный метод для проверки существования базы данных
        """Проверка существования папки и файла базы данных"""
        if not os.path.exists(self.db_folder):  # Если папка не существует
            os.makedirs(self.db_folder)  # Создаем папку
        
        if not os.path.exists(self.db_path):  # Если файл базы данных не существует
            self._save_terms({})  # Создаем пустой файл базы данных

    def _load_terms(self):  # Приватный метод для загрузки терминов
        """Загрузка терминов из JSON файла"""
        try:  # Начало блока обработки исключений
            with open(self.db_path, 'r', encoding='utf-8') as file:  # Открываем файл для чтения
                return json.load(file)  # Загружаем JSON из файла и возвращаем его
        except json.JSONDecodeError:  # Если произошла ошибка декодирования JSON
            return {}  # Возвращаем пустой словарь
        except Exception as e:  # Если произошла любая другая ошибка
            print(f"Ошибка при чтении базы терминов: {str(e)}")  # Выводим сообщение об ошибке
            return {}  # Возвращаем пустой словарь

    def _save_terms(self, terms):  # Приватный метод для сохранения терминов
        """Сохранение терминов в JSON файл"""
        try:  # Начало блока обработки исключений
            with open(self.db_path, 'w', encoding='utf-8') as file:  # Открываем файл для записи
                json.dump(terms, file, ensure_ascii=False, indent=4)  # Записываем словарь в JSON формате
            return True  # Возвращаем True в случае успеха
        except Exception as e:  # Если произошла ошибка
            print(f"Ошибка при сохранении базы терминов: {str(e)}")  # Выводим сообщение об ошибке
            return False  # Возвращаем False в случае ошибки

    def add_terms(self, new_terms, relevance_threshold=80):  # Метод для добавления новых терминов
        """
        Добавление новых терминов в базу
        
        :param new_terms: словарь с терминами
        :param relevance_threshold: порог релевантности (по умолчанию 80)
        :return: True если успешно, False если произошла ошибка
        """
        try:  # Начало блока обработки исключений
            # Загружаем существующие термины
            existing_terms = self._load_terms()  # Загружаем существующие термины
            
            if not isinstance(new_terms, dict):  # Проверяем, является ли new_terms словарем
                print("Ошибка: new_terms должен быть словарем")  # Выводим сообщение об ошибке
                return False  # Возвращаем False в случае ошибки

            # Обновляем существующие термины новыми
            existing_terms.update(new_terms)  # Обновляем словарь существующих терминов новыми

            # Сохраняем обновленную базу
            return self._save_terms(existing_terms)  # Сохраняем обновленные термины и возвращаем результат

        except Exception as e:  # Если произошла ошибка
            print(f"Ошибка при добавлении терминов: {str(e)}")  # Выводим сообщение об ошибке
            return False  # Возвращаем False в случае ошибки

    def get_all_terms(self):  # Метод для получения всех терминов
        """Получение всех терминов из базы"""
        return self._load_terms()  # Загружаем и возвращаем все термины

    def get_term(self, term_name):  # Метод для получения конкретного термина
        """Получение конкретного термина по названию"""
        terms = self._load_terms()  # Загружаем все термины
        return terms.get(term_name)  # Возвращаем термин по ключу или None, если термин не найден
    
    def term_exists(self, term_name):  # Метод для проверки существования термина
        """Проверяет существование термина в базе данных"""
        try:  # Начало блока обработки исключений
            with open(self.db_path, 'r', encoding='utf-8') as file:  # Открываем файл для чтения
                data = json.load(file)  # Загружаем JSON из файла
                return term_name in data  # Проверяем наличие термина в словаре и возвращаем результат
        except FileNotFoundError:  # Если файл не найден
            return False  # Возвращаем False
        except json.JSONDecodeError:  # Если произошла ошибка декодирования JSON
            return False  # Возвращаем False
