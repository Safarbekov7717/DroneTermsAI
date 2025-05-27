import os  # Импортирует модуль для работы с операционной системой
from datetime import datetime  # Импортирует класс для работы с датой и временем
from modules.text_extractor import TextExtractor  # Импортирует класс для извлечения текста из файлов
from modules.text_cleaner import TextCleaner  # Импортирует класс для очистки текста
from modules.ai_processor import AIProcessor  # Импортирует класс для обработки текста через ИИ
from modules.data_saver import DataSaver  # Импортирует класс для сохранения данных
import time  # Импортирует модуль для работы со временем
from colorama import init, Fore, Back, Style  # Импортирует библиотеку для цветного вывода в консоль
from tqdm import tqdm  # Импортирует библиотеку для отображения прогресс-баров

# Инициализация colorama для Windows
init()  # Инициализирует библиотеку colorama для корректной работы в Windows

class Colors:  # Определяет класс для хранения цветовых констант
    HEADER = Fore.CYAN  # Цвет для заголовков - голубой
    PRIMARY = Fore.BLUE  # Основной цвет - синий
    SUCCESS = Fore.GREEN  # Цвет успешных операций - зеленый
    WARNING = Fore.YELLOW  # Цвет предупреждений - желтый
    ERROR = Fore.RED  # Цвет ошибок - красный
    INFO = Fore.WHITE  # Цвет информационных сообщений - белый
    RESET = Style.RESET_ALL  # Сброс всех цветовых настроек
    
class Interface:  # Определяет основной класс интерфейса программы
    def __init__(self):  # Конструктор класса
        self.cleaner = TextCleaner()  # Создает экземпляр очистителя текста
        self.extractor = TextExtractor(self.cleaner)  # Создает экземпляр извлекателя текста, передавая очиститель
        self.ai_processor = AIProcessor()  # Создает экземпляр обработчика ИИ
        self.data_saver = DataSaver()  # Создает экземпляр сохранителя данных
        self.supported_formats = ('.pdf', '.doc', '.docx')  # Определяет поддерживаемые форматы файлов
        
    def show_logo(self):  # Метод для отображения логотипа программы
        logo = """
    ██████╗ ██████╗  ██████╗ ███╗   ██╗███████╗████████╗███████╗██████╗ ███╗   ███╗███████╗
    ██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝
    ██║  ██║██████╔╝██║   ██║██╔██╗ ██║█████╗     ██║   █████╗  ██████╔╝██╔████╔██║███████╗
    ██║  ██║██╔══██╗██║   ██║██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║╚════██║
    ██████╔╝██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║███████║
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
    """  # ASCII-арт логотип программы
        print(f"{Colors.PRIMARY}{logo}{Colors.RESET}")  # Выводит логотип синим цветом
        print(f"{Colors.INFO}DroneTerms AI - Система обработки терминологии БАС{Colors.RESET}")  # Выводит название программы
        print(f"{Colors.INFO}Версия 1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")  # Выводит версию и текущую дату/время
        print("="*80)  # Выводит разделительную линию

    def show_progress(self, description, seconds):  # Метод для отображения прогресс-бара
        for _ in tqdm(range(100), desc=description, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):  # Создает прогресс-бар с 100 шагами
            time.sleep(seconds/100)  # Задержка для каждого шага (общее время = seconds)

    def display_terms(self, ai_response):  # Метод для отображения найденных терминов
        print(f"\n{Colors.HEADER}Найденные термины:{Colors.RESET}")  # Выводит заголовок
        print("="*80)  # Выводит разделительную линию
        print(f"{Colors.INFO}{ai_response}{Colors.RESET}")  # Выводит ответ ИИ с терминами
        print("="*80)  # Выводит разделительную линию

    def process_file(self, file_path):  # Метод для обработки файла
        print(f"\n{Colors.HEADER}Обработка файла:{Colors.RESET} {file_path}")  # Выводит информацию о файле
        print("="*80)  # Выводит разделительную линию

        # Извлечение текста
        print(f"\n{Colors.INFO}Извлечение текста из файла...{Colors.RESET}")  # Сообщение о начале извлечения текста
        self.show_progress("Чтение файла", 1)  # Показывает прогресс-бар чтения файла (1 секунда)
        original_text = self.extractor.extract_raw_text(file_path)  # Извлекает текст из файла
        
        if not original_text:  # Проверяет, успешно ли извлечен текст
            print(f"{Colors.ERROR}Ошибка: Не удалось извлечь текст из файла{Colors.RESET}")  # Выводит сообщение об ошибке
            return False  # Возвращает False в случае ошибки

        original_length = len(original_text)  # Вычисляет длину исходного текста
        print(f"\n{Colors.SUCCESS}Успешно извлечено символов: {original_length}{Colors.RESET}")  # Выводит количество извлеченных символов

        # Вывод статистики исходного текста
        print(f"\n{Colors.HEADER}Исходный текст:{Colors.RESET}")  # Заголовок для исходного текста
        print("-"*80)  # Выводит разделительную линию
        print(f"{Colors.WARNING}{original_text[:500]}...{Colors.RESET}")  # Выводит первые 500 символов текста
        print(f"{Colors.INFO}(Показаны первые 500 символов){Colors.RESET}")  # Информационное сообщение
        print("-"*80)  # Выводит разделительную линию

        # Очистка текста
        print(f"\n{Colors.INFO}Выполняется очистка текста...{Colors.RESET}")  # Сообщение о начале очистки текста
        self.show_progress("Очистка текста", 1)  # Показывает прогресс-бар очистки текста (1 секунда)
        cleaned_text = self.extractor.cleaner.clean_and_log(original_text)  # Очищает текст

        if not cleaned_text:  # Проверяет, успешно ли очищен текст
            print(f"{Colors.ERROR}Ошибка: Не удалось очистить текст{Colors.RESET}")  # Выводит сообщение об ошибке
            return False  # Возвращает False в случае ошибки

        cleaned_length = len(cleaned_text)  # Вычисляет длину очищенного текста
        reduction = ((original_length - cleaned_length) / original_length) * 100  # Вычисляет процент сокращения текста

        print(f"\n{Colors.SUCCESS}Статистика очистки:{Colors.RESET}")  # Заголовок для статистики
        print(f"Исходный размер: {original_length} символов")  # Выводит исходный размер
        print(f"После очистки: {cleaned_length} символов")  # Выводит размер после очистки
        print(f"Сокращение: {reduction:.1f}%")  # Выводит процент сокращения с одним знаком после запятой

        # Вывод очищенного текста
        print(f"\n{Colors.HEADER}Очищенный текст:{Colors.RESET}")  # Заголовок для очищенного текста
        print("-"*80)  # Выводит разделительную линию
        print(f"{Colors.SUCCESS}{cleaned_text[:500]}...{Colors.RESET}")  # Выводит первые 500 символов очищенного текста
        print(f"{Colors.INFO}(Показаны первые 500 символов){Colors.RESET}")  # Информационное сообщение
        print("-"*80)  # Выводит разделительную линию

        filename = os.path.basename(file_path)  # Извлекает имя файла из пути

        # Обработка через ИИ
        while True:  # Цикл для получения корректного ответа пользователя
            ai_choice = input(f"\n{Colors.INFO}Отправить текст на обработку через ИИ? (да/нет): {Colors.RESET}").lower()  # Запрашивает выбор пользователя
            if ai_choice in ['да', 'нет']:  # Проверяет корректность ввода
                break  # Выходит из цикла, если ввод корректен
            print(f"{Colors.WARNING}Пожалуйста, введите 'да' или 'нет'{Colors.RESET}")  # Выводит предупреждение при некорректном вводе

        if ai_choice == 'да':  # Если пользователь выбрал обработку через ИИ
            print(f"\n{Colors.INFO}Отправка текста на обработку через ИИ...{Colors.RESET}")  # Сообщение о начале обработки
            self.ai_processor.model_name = None  # Сбрасывает имя модели ИИ для запроса у пользователя
            result = self.ai_processor.process_text(cleaned_text)  # Обрабатывает текст через ИИ
            
            if result == "return_to_main":  # Проверяет специальный флаг для возврата в главное меню
                return "return_to_main"  # Возвращает специальный флаг
            
            if not result:  # Проверяет успешность обработки
                print(f"{Colors.ERROR}Ошибка: Не удалось обработать текст через ИИ{Colors.RESET}")  # Выводит сообщение об ошибке
                return False  # Возвращает False в случае ошибки

            self.display_terms(result)  # Отображает найденные термины

            while True:  # Цикл для получения корректного ответа пользователя о сохранении
                save_choice = input(f"\n{Colors.INFO}Сохранить результаты? (да/нет): {Colors.RESET}").lower()  # Запрашивает выбор пользователя
                if save_choice in ['да', 'нет']:  # Проверяет корректность ввода
                    break  # Выходит из цикла, если ввод корректен
                print(f"{Colors.WARNING}Пожалуйста, введите 'да' или 'нет'{Colors.RESET}")  # Выводит предупреждение при некорректном вводе

            if save_choice == 'да':  # Если пользователь выбрал сохранение результатов
                print(f"\n{Colors.INFO}Сохранение результатов...{Colors.RESET}")  # Сообщение о начале сохранения
                self.show_progress("Сохранение", 1)  # Показывает прогресс-бар сохранения (1 секунда)
                if not self.data_saver.save_terms(result, filename):  # Сохраняет термины и проверяет успешность
                    print(f"{Colors.WARNING}Предупреждение: Возникли проблемы при сохранении терминов{Colors.RESET}")  # Выводит предупреждение
                else:
                    print(f"{Colors.SUCCESS}Результаты успешно сохранены!{Colors.RESET}")  # Сообщение об успешном сохранении
        else:
            print(f"\n{Colors.INFO}Возврат к предыдущему шагу...{Colors.RESET}")  # Сообщение о возврате, если пользователь отказался от обработки

        return True  # Возвращает True при успешном завершении

    def show_available_files(self):  # Метод для отображения доступных файлов
        print(f"\n{Colors.HEADER}Доступные файлы в папке data:{Colors.RESET}")  # Заголовок для списка файлов
        print("-" * 80)  # Выводит разделительную линию
        
        data_folder = 'data'  # Имя папки с данными
        if not os.path.exists(data_folder):  # Проверяет существование папки
            print(f"{Colors.ERROR}Папка 'data' не найдена{Colors.RESET}")  # Выводит сообщение об ошибке
            return []  # Возвращает пустой список, если папка не найдена

        files = []  # Инициализирует список для хранения имен файлов
        for file in os.listdir(data_folder):  # Перебирает все файлы в папке
            if file.lower().endswith(self.supported_formats):  # Проверяет, имеет ли файл поддерживаемый формат
                files.append(file)  # Добавляет файл в список
                print(f"{Colors.INFO}{len(files)}. {file}{Colors.RESET}")  # Выводит номер и имя файла
        
        if not files:  # Проверяет, найдены ли файлы
            print(f"{Colors.WARNING}Нет доступных файлов поддерживаемых форматов{Colors.RESET}")  # Выводит предупреждение
        
        print("-" * 80)  # Выводит разделительную линию
        return files  # Возвращает список файлов

    def run(self):  # Основной метод запуска интерфейса
        while True:  # Бесконечный цикл для работы программы
            os.system('cls' if os.name == 'nt' else 'clear')  # Очищает консоль (cls для Windows, clear для Unix)
            self.show_logo()  # Отображает логотип программы
            
            available_files = self.show_available_files()  # Получает список доступных файлов
            
            print(f"\n{Colors.HEADER}Выберите действие:{Colors.RESET}")  # Заголовок для меню
            print(f"{Colors.INFO}1. Обработать файл{Colors.RESET}")  # Пункт меню 1
            print(f"{Colors.INFO}2. Выйти из программы{Colors.RESET}")  # Пункт меню 2
            
            choice = input(f"\n{Colors.INFO}Ваш выбор (1-2): {Colors.RESET}")  # Запрашивает выбор пользователя
            
            if choice == '1':  # Если выбрана обработка файла
                if available_files:  # Если есть доступные файлы
                    file_input = input(f"\n{Colors.INFO}Введите номер файла из списка выше\nили название файла (или полный путь к другому файлу): {Colors.RESET}")  # Запрашивает выбор файла
                    
                    if file_input.isdigit():  # Если введен номер файла
                        file_num = int(file_input)  # Преобразует строку в число
                        if 1 <= file_num <= len(available_files):  # Проверяет, что номер в допустимом диапазоне
                            file_path = os.path.join('data', available_files[file_num-1])  # Формирует путь к файлу
                        else:
                            print(f"{Colors.ERROR}\nОшибка: Неверный номер файла{Colors.RESET}")  # Выводит сообщение об ошибке
                            input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")  # Ожидает нажатия Enter
                            continue  # Переходит к следующей итерации цикла
                    else:  # Если введено имя файла или путь
                        if file_input in available_files:  # Если файл есть в списке доступных
                            file_path = os.path.join('data', file_input)  # Формирует путь к файлу в папке data
                        else:
                            file_path = file_input  # Использует введенный путь как есть

                    if not os.path.exists(file_path):  # Проверяет существование файла
                        print(f"{Colors.ERROR}\nОшибка: Файл не найден{Colors.RESET}")  # Выводит сообщение об ошибке
                        input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")  # Ожидает нажатия Enter
                        continue  # Переходит к следующей итерации цикла
                        
                    result = self.process_file(file_path)  # Обрабатывает выбранный файл
                    if result != "return_to_main":  # Если не получен специальный флаг для возврата
                        input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")  # Ожидает нажатия Enter
                else:  # Если нет доступных файлов
                    print(f"{Colors.WARNING}\nПоместите файлы в папку 'data' для обработки{Colors.RESET}")  # Выводит предупреждение
                    input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")  # Ожидает нажатия Enter
                
            elif choice == '2':  # Если выбран выход из программы
                print(f"\n{Colors.SUCCESS}Завершение работы программы...{Colors.RESET}")  # Выводит сообщение о завершении
                break  # Выходит из бесконечного цикла
            else:  # Если введен некорректный выбор
                print(f"{Colors.ERROR}\nНеверный выбор. Пожалуйста, выберите 1 или 2{Colors.RESET}")  # Выводит сообщение об ошибке
                input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")  # Ожидает нажатия Enter
