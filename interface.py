import os
from datetime import datetime
from modules.text_extractor import TextExtractor
from modules.text_cleaner import TextCleaner
from modules.ai_processor import AIProcessor
from modules.data_saver import DataSaver
import time
from colorama import init, Fore, Back, Style
from tqdm import tqdm

# Инициализация colorama для Windows
init()

class Colors:
    HEADER = Fore.CYAN
    PRIMARY = Fore.BLUE
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    INFO = Fore.WHITE
    RESET = Style.RESET_ALL
    
class Interface:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.extractor = TextExtractor(self.cleaner)
        self.ai_processor = AIProcessor()
        self.data_saver = DataSaver()
        self.supported_formats = ('.pdf', '.doc', '.docx')
        
    def show_logo(self):
        logo = """
    ██████╗ ██████╗  ██████╗ ███╗   ██╗███████╗████████╗███████╗██████╗ ███╗   ███╗███████╗
    ██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝
    ██║  ██║██████╔╝██║   ██║██╔██╗ ██║█████╗     ██║   █████╗  ██████╔╝██╔████╔██║███████╗
    ██║  ██║██╔══██╗██║   ██║██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║╚════██║
    ██████╔╝██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║███████║
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
    """
        print(f"{Colors.PRIMARY}{logo}{Colors.RESET}")
        print(f"{Colors.INFO}DroneTerms AI - Система обработки терминологии БАС{Colors.RESET}")
        print(f"{Colors.INFO}Версия 1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print("="*80)

    def show_progress(self, description, seconds):
        for _ in tqdm(range(100), desc=description, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
            time.sleep(seconds/100)

    def display_terms(self, ai_response):
        print(f"\n{Colors.HEADER}Найденные термины:{Colors.RESET}")
        print("="*80)
        print(f"{Colors.INFO}{ai_response}{Colors.RESET}")
        print("="*80)

    def process_file(self, file_path):
        print(f"\n{Colors.HEADER}Обработка файла:{Colors.RESET} {file_path}")
        print("="*80)

        # Извлечение текста
        print(f"\n{Colors.INFO}Извлечение текста из файла...{Colors.RESET}")
        self.show_progress("Чтение файла", 1)
        original_text = self.extractor.extract_raw_text(file_path)
        
        if not original_text:
            print(f"{Colors.ERROR}Ошибка: Не удалось извлечь текст из файла{Colors.RESET}")
            return False

        original_length = len(original_text)
        print(f"\n{Colors.SUCCESS}Успешно извлечено символов: {original_length}{Colors.RESET}")

        # Вывод статистики исходного текста
        print(f"\n{Colors.HEADER}Исходный текст:{Colors.RESET}")
        print("-"*80)
        print(f"{Colors.WARNING}{original_text[:500]}...{Colors.RESET}")
        print(f"{Colors.INFO}(Показаны первые 500 символов){Colors.RESET}")
        print("-"*80)

        # Очистка текста
        print(f"\n{Colors.INFO}Выполняется очистка текста...{Colors.RESET}")
        self.show_progress("Очистка текста", 1)
        cleaned_text = self.extractor.cleaner.clean_and_log(original_text)

        if not cleaned_text:
            print(f"{Colors.ERROR}Ошибка: Не удалось очистить текст{Colors.RESET}")
            return False

        cleaned_length = len(cleaned_text)
        reduction = ((original_length - cleaned_length) / original_length) * 100

        print(f"\n{Colors.SUCCESS}Статистика очистки:{Colors.RESET}")
        print(f"Исходный размер: {original_length} символов")
        print(f"После очистки: {cleaned_length} символов")
        print(f"Сокращение: {reduction:.1f}%")

        # Вывод очищенного текста
        print(f"\n{Colors.HEADER}Очищенный текст:{Colors.RESET}")
        print("-"*80)
        print(f"{Colors.SUCCESS}{cleaned_text[:500]}...{Colors.RESET}")
        print(f"{Colors.INFO}(Показаны первые 500 символов){Colors.RESET}")
        print("-"*80)

        filename = os.path.basename(file_path)

        # Обработка через ИИ
        while True:
            ai_choice = input(f"\n{Colors.INFO}Отправить текст на обработку через ИИ? (да/нет): {Colors.RESET}").lower()
            if ai_choice in ['да', 'нет']:
                break
            print(f"{Colors.WARNING}Пожалуйста, введите 'да' или 'нет'{Colors.RESET}")

        if ai_choice == 'да':
            print(f"\n{Colors.INFO}Отправка текста на обработку через ИИ...{Colors.RESET}")
            self.ai_processor.model_name = None
            result = self.ai_processor.process_text(cleaned_text)
            
            if result == "return_to_main":
                return "return_to_main"  # Возвращаем специальный флаг
            
            if not result:
                print(f"{Colors.ERROR}Ошибка: Не удалось обработать текст через ИИ{Colors.RESET}")
                return False

            self.display_terms(result)

            while True:
                save_choice = input(f"\n{Colors.INFO}Сохранить результаты? (да/нет): {Colors.RESET}").lower()
                if save_choice in ['да', 'нет']:
                    break
                print(f"{Colors.WARNING}Пожалуйста, введите 'да' или 'нет'{Colors.RESET}")

            if save_choice == 'да':
                print(f"\n{Colors.INFO}Сохранение результатов...{Colors.RESET}")
                self.show_progress("Сохранение", 1)
                if not self.data_saver.save_terms(result, filename):
                    print(f"{Colors.WARNING}Предупреждение: Возникли проблемы при сохранении терминов{Colors.RESET}")
                else:
                    print(f"{Colors.SUCCESS}Результаты успешно сохранены!{Colors.RESET}")
        else:
            print(f"\n{Colors.INFO}Возврат к предыдущему шагу...{Colors.RESET}")

        return True

    def show_available_files(self):
        print(f"\n{Colors.HEADER}Доступные файлы в папке data:{Colors.RESET}")
        print("-" * 80)
        
        data_folder = 'data'
        if not os.path.exists(data_folder):
            print(f"{Colors.ERROR}Папка 'data' не найдена{Colors.RESET}")
            return []

        files = []
        for file in os.listdir(data_folder):
            if file.lower().endswith(self.supported_formats):
                files.append(file)
                print(f"{Colors.INFO}{len(files)}. {file}{Colors.RESET}")
        
        if not files:
            print(f"{Colors.WARNING}Нет доступных файлов поддерживаемых форматов{Colors.RESET}")
        
        print("-" * 80)
        return files

    def run(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_logo()
            
            available_files = self.show_available_files()
            
            print(f"\n{Colors.HEADER}Выберите действие:{Colors.RESET}")
            print(f"{Colors.INFO}1. Обработать файл{Colors.RESET}")
            print(f"{Colors.INFO}2. Выйти из программы{Colors.RESET}")
            
            choice = input(f"\n{Colors.INFO}Ваш выбор (1-2): {Colors.RESET}")
            
            if choice == '1':
                if available_files:
                    file_input = input(f"\n{Colors.INFO}Введите номер файла из списка выше\nили название файла (или полный путь к другому файлу): {Colors.RESET}")
                    
                    if file_input.isdigit():
                        file_num = int(file_input)
                        if 1 <= file_num <= len(available_files):
                            file_path = os.path.join('data', available_files[file_num-1])
                        else:
                            print(f"{Colors.ERROR}\nОшибка: Неверный номер файла{Colors.RESET}")
                            input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")
                            continue
                    else:
                        if file_input in available_files:
                            file_path = os.path.join('data', file_input)
                        else:
                            file_path = file_input

                    if not os.path.exists(file_path):
                        print(f"{Colors.ERROR}\nОшибка: Файл не найден{Colors.RESET}")
                        input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")
                        continue
                        
                    result = self.process_file(file_path)
                    if result != "return_to_main":
                        input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")
                else:
                    print(f"{Colors.WARNING}\nПоместите файлы в папку 'data' для обработки{Colors.RESET}")
                    input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")
                
            elif choice == '2':
                print(f"\n{Colors.SUCCESS}Завершение работы программы...{Colors.RESET}")
                break
            else:
                print(f"{Colors.ERROR}\nНеверный выбор. Пожалуйста, выберите 1 или 2{Colors.RESET}")
                input(f"\n{Colors.INFO}Нажмите Enter для продолжения...{Colors.RESET}")