import json
import os
from datetime import datetime

class JsonTermManager:
    def __init__(self):
        self.db_folder = 'db'
        self.db_file = 'db_terms.json'
        self.db_path = os.path.join(self.db_folder, self.db_file)
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Проверка существования папки и файла базы данных"""
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
        
        if not os.path.exists(self.db_path):
            self._save_terms({})

    def _load_terms(self):
        """Загрузка терминов из JSON файла"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
        except Exception as e:
            print(f"Ошибка при чтении базы терминов: {str(e)}")
            return {}

    def _save_terms(self, terms):
        """Сохранение терминов в JSON файл"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as file:
                json.dump(terms, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении базы терминов: {str(e)}")
            return False

    def add_terms(self, new_terms, relevance_threshold=80):
        """
        Добавление новых терминов в базу
        
        :param new_terms: словарь с терминами
        :param relevance_threshold: порог релевантности (по умолчанию 80)
        :return: True если успешно, False если произошла ошибка
        """
        try:
            # Загружаем существующие термины
            existing_terms = self._load_terms()
            
            if not isinstance(new_terms, dict):
                print("Ошибка: new_terms должен быть словарем")
                return False

            # Обновляем существующие термины новыми
            existing_terms.update(new_terms)

            # Сохраняем обновленную базу
            return self._save_terms(existing_terms)

        except Exception as e:
            print(f"Ошибка при добавлении терминов: {str(e)}")
            return False

    def get_all_terms(self):
        """Получение всех терминов из базы"""
        return self._load_terms()

    def get_term(self, term_name):
        """Получение конкретного термина по названию"""
        terms = self._load_terms()
        return terms.get(term_name)
    
    def term_exists(self, term_name):
        """Проверяет существование термина в базе данных"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return term_name in data
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False