import os  # Импортируем модуль для работы с операционной системой
import re  # Импортируем модуль для работы с регулярными выражениями
import pandas as pd  # Импортируем библиотеку pandas для работы с данными
from datetime import datetime  # Импортируем класс для работы с датой и временем
from .json_manager import JsonTermManager  # Импортируем класс для управления терминами в JSON

class DataSaver:  # Класс для сохранения данных
    def __init__(self):  # Конструктор класса
        self.directories = {  # Словарь с путями к директориям для сохранения результатов
            'csv': 'results/csv',  # Путь для CSV файлов
            'excel': 'results/excel'  # Путь для Excel файлов
        }
        self._create_directories()  # Создаем необходимые директории
        self.json_manager = JsonTermManager()  # Создаем экземпляр менеджера JSON

    def _create_directories(self):  # Приватный метод для создания директорий
        """Создание необходимых директорий"""
        for directory in self.directories.values():  # Перебираем все пути из словаря
            if not os.path.exists(directory):  # Если директория не существует
                os.makedirs(directory)  # Создаем директорию

    def parse_ai_terms(self, ai_response):  # Метод для парсинга терминов из ответа ИИ
        """Парсинг терминов из ответа ИИ в разных форматах"""
        terms_data = []  # Список для хранения данных о терминах
        current_term = {}  # Словарь для текущего термина
        
        # Разбиваем текст на строки и удаляем пустые
        lines = [line.strip() for line in ai_response.split('\n') if line.strip()]  # Разбиваем текст на строки и удаляем пустые
        
        # Регулярное выражение для определения начала нумерованного термина
        number_pattern = r'^\d+\.'  # Шаблон для поиска номера в начале строки
        
        for line in lines:  # Перебираем все строки
            # Удаляем лишние пробелы
            line = line.strip()  # Удаляем пробелы в начале и конце строки
            
            # Проверяем различные форматы начала термина
            is_numbered_term = bool(re.match(number_pattern, line) and ('Термин:' in line or '**Термин:**' in line))  # Проверяем, является ли строка нумерованным термином
            is_simple_term = line.startswith(('Термин:', '**Термин:**', '### Термин:'))  # Проверяем, является ли строка простым термином
            
            if is_numbered_term or is_simple_term:  # Если строка является началом нового термина
                # Если есть предыдущий термин, сохраняем его
                if current_term:  # Если словарь текущего термина не пуст
                    terms_data.append(current_term)  # Добавляем текущий термин в список
                
                # Создаем новый термин
                current_term = {}  # Создаем новый пустой словарь для текущего термина
                
                # Извлекаем название термина
                if '**Термин:**' in line:  # Если в строке есть маркер "**Термин:**"
                    term = line.split('**Термин:**')[1].strip()  # Извлекаем название термина
                elif 'Термин:' in line:  # Если в строке есть маркер "Термин:"
                    term = line.split('Термин:')[1].strip()  # Извлекаем название термина
                
                # Убираем номер и решетки, если они есть
                if is_numbered_term:  # Если термин нумерованный
                    term = re.sub(number_pattern, '', term).strip()  # Удаляем номер
                term = term.replace('#', '').strip()  # Удаляем символы решетки и пробелы
                    
                current_term['термин'] = term  # Сохраняем название термина в словарь
                
            elif any(marker in line for marker in ['**Определение:**', 'Определение:', '- **Определение:**']):  # Если строка содержит определение
                definition = line  # Копируем строку
                for marker in ['**Определение:**', 'Определение:', '- **Определение:**', '-']:  # Перебираем возможные маркеры
                    definition = definition.replace(marker, '')  # Удаляем маркеры
                current_term['определение'] = definition.strip()  # Сохраняем определение в словарь
                
            elif any(marker in line for marker in ['**Перевод:**', 'Перевод:', '- **Перевод:**']):  # Если строка содержит перевод
                translation = line  # Копируем строку
                for marker in ['**Перевод:**', 'Перевод:', '- **Перевод:**', '-']:  # Перебираем возможные маркеры
                    translation = translation.replace(marker, '')  # Удаляем маркеры
                current_term['перевод'] = translation.strip()  # Сохраняем перевод в словарь
                
            elif any(marker in line for marker in ['**Релевантность:**', 'Релевантность:', '- **Релевантность:**']):  # Если строка содержит релевантность
                relevance = line  # Копируем строку
                for marker in ['**Релевантность:**', 'Релевантность:', '- **Релевантность:**', '-']:  # Перебираем возможные маркеры
                    relevance = relevance.replace(marker, '')  # Удаляем маркеры
                relevance = relevance.replace('%', '').strip()  # Удаляем символ процента и пробелы
                try:
                    current_term['релевантность'] = float(relevance)  # Преобразуем строку в число и сохраняем в словарь
                except ValueError:  # Если не удалось преобразовать в число
                    current_term['релевантность'] = 0.0  # Устанавливаем релевантность 0
        
        # Добавляем последний термин
        if current_term:  # Если словарь текущего термина не пуст
            terms_data.append(current_term)  # Добавляем последний термин в список
            
        return terms_data  # Возвращаем список с данными о терминах

    def save_to_csv(self, terms_data, base_filename):  # Метод для сохранения в CSV
        """Сохранение в CSV формат"""
        if not terms_data:  # Если нет данных для сохранения
            return False  # Возвращаем False
            
        csv_path = os.path.join(self.directories['csv'], f"{base_filename}.csv")  # Формируем путь к CSV файлу
        df = pd.DataFrame(terms_data)  # Создаем DataFrame из данных
        df.to_csv(csv_path, index=False, encoding='utf-8')  # Сохраняем DataFrame в CSV
        print(f"Термины сохранены в CSV: {csv_path}")  # Выводим сообщение об успешном сохранении
        return True  # Возвращаем True

    def save_to_excel(self, terms_data, base_filename):  # Метод для сохранения в Excel
        """Сохранение в Excel формат"""
        if not terms_data:  # Если нет данных для сохранения
            return False  # Возвращаем False
            
        excel_path = os.path.join(self.directories['excel'], f"{base_filename}.xlsx")  # Формируем путь к Excel файлу
        df = pd.DataFrame(terms_data)  # Создаем DataFrame из данных
        df.to_excel(excel_path, index=False)  # Сохраняем DataFrame в Excel
        print(f"Термины сохранены в Excel: {excel_path}")  # Выводим сообщение об успешном сохранении
        return True  # Возвращаем True

    def prepare_terms_for_json(self, terms_data):  # Метод для подготовки терминов для JSON
      """Подготовка терминов для сохранения в JSON"""
      try:
          json_terms = {}  # Изменяем на словарь вместо списка
          
          for term in terms_data:  # Перебираем все термины
              if isinstance(term, dict) and term.get('релевантность', 0) >= 80:  # Если термин - словарь и его релевантность >= 80
                  term_name = term.get('термин', '')  # Получаем название термина
                  if term_name:  # Если название термина не пустое
                      json_terms[term_name] = {  # Добавляем термин в словарь
                          'term': term_name,  # Название термина
                          'definition': term.get('определение', ''),  # Определение термина
                          'translation': term.get('перевод', ''),  # Перевод термина
                          'relevance': term.get('релевантность', 0),  # Релевантность термина
                          'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Текущая дата и время
                      }
          
          return json_terms  # Возвращаем словарь с терминами
          
      except Exception as e:  # Если произошла ошибка
          print(f"Ошибка при подготовке терминов для JSON: {str(e)}")  # Выводим сообщение об ошибке
          return None  # Возвращаем None

    def save_terms(self, ai_response, filename):  # Основной метод для сохранения терминов
        """Основной метод сохранения терминов"""
        # Парсинг терминов
        terms_data = self.parse_ai_terms(ai_response)  # Парсим термины из ответа ИИ
        
        if not terms_data:  # Если нет данных о терминах
            print("В ответе ИИ не найдено терминов для сохранения")  # Выводим сообщение
            return False  # Возвращаем False

        # Удаляем расширение из имени файла
        base_filename = os.path.splitext(filename)[0]  # Получаем имя файла без расширения
        
        # Формирование базового имени файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Получаем текущую дату и время в формате строки
        output_filename = f"terms_{timestamp}_{base_filename}"  # Формируем имя выходного файла

        # Сохранение в CSV и Excel
        csv_saved = self.save_to_csv(terms_data, output_filename)  # Сохраняем в CSV
        excel_saved = self.save_to_excel(terms_data, output_filename)  # Сохраняем в Excel
        
        # Подготовка и сохранение в JSON базу данных
        json_terms = self.prepare_terms_for_json(terms_data)  # Подготавливаем термины для JSON
        
        added_count = 0  # Счетчик добавленных терминов
        updated_count = 0  # Счетчик обновленных терминов
        
        if json_terms:  # Если есть термины для сохранения в JSON
            db_saved = self.json_manager.add_terms(json_terms)  # Добавляем термины в базу данных
            if db_saved:  # Если сохранение прошло успешно
                # Подсчитываем статистику
                for term_data in json_terms.values():  # Перебираем все термины
                    if self.json_manager.term_exists(term_data['term']):  # Если термин уже существует в базе
                        updated_count += 1  # Увеличиваем счетчик обновленных терминов
                    else:  # Если термин новый
                        added_count += 1  # Увеличиваем счетчик добавленных терминов
                
                # Выводим статистику
                print(f"\nСтатистика обработки терминов:")  # Заголовок статистики
                print(f"✨ Добавлено новых терминов: {added_count}")  # Количество новых терминов
                print(f"🔄 Обновлено существующих терминов: {updated_count}")  # Количество обновленных терминов
                print(f"📚 Всего обработано терминов: {added_count + updated_count}")  # Общее количество терминов
                print("Термины с релевантностью больше 80% успешно сохранены в базу данных")  # Сообщение об успешном сохранении
            else:  # Если произошла ошибка при сохранении
                print("Произошла ошибка при сохранении терминов в базу данных")  # Выводим сообщение об ошибке
        else:  # Если нет терминов для сохранения
            print("Нет терминов для сохранения в базу данных")  # Выводим сообщение
            db_saved = False  # Устанавливаем флаг сохранения в False

        return all([csv_saved, excel_saved, db_saved])  # Возвращаем True, если все операции сохранения прошли успешно
