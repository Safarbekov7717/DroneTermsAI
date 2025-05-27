import PyPDF2  # Библиотека для работы с PDF-файлами
import docx    # Библиотека для работы с документами Microsoft Word
import os      # Модуль для работы с файловой системой и путями

class TextExtractor:  # Класс для извлечения текста из документов разных форматов
    def __init__(self, cleaner):  # Конструктор класса, принимает объект для очистки текста
        self.cleaner = cleaner    # Сохраняем объект cleaner как атрибут класса

    def extract_raw_text(self, file_path):  # Основной метод для извлечения текста из файла
        """Извлечение текста из файла"""
        try:  # Начало блока обработки исключений
            file_extension = os.path.splitext(file_path)[1].lower()  # Получаем расширение файла в нижнем регистре
            
            if file_extension == '.pdf':  # Если файл имеет расширение PDF
                return self._extract_from_pdf(file_path)  # Вызываем метод для обработки PDF
            elif file_extension in ['.doc', '.docx']:  # Если файл имеет расширение Word
                return self._extract_from_word(file_path)  # Вызываем метод для обработки Word
            else:  # Если расширение не поддерживается
                print(f"Неподдерживаемый формат файла: {file_extension}")  # Выводим сообщение об ошибке
                return None  # Возвращаем None при неподдерживаемом формате
        except Exception as e:  # Обрабатываем любые исключения
            print(f"Ошибка при извлечении текста: {str(e)}")  # Выводим сообщение об ошибке
            return None  # Возвращаем None при возникновении ошибки

    def _extract_from_pdf(self, file_path):  # Приватный метод для извлечения текста из PDF
        """Извлечение текста из PDF"""
        try:  # Начало блока обработки исключений
            with open(file_path, 'rb') as file:  # Открываем файл в бинарном режиме
                reader = PyPDF2.PdfReader(file)  # Создаем объект для чтения PDF
                text = ""  # Инициализируем пустую строку для текста
                for page in reader.pages:  # Перебираем все страницы документа
                    text += page.extract_text()  # Извлекаем текст с каждой страницы
                return text  # Возвращаем весь извлеченный текст
        except Exception as e:  # Обрабатываем исключения при чтении PDF
            print(f"Ошибка при чтении PDF: {str(e)}")  # Выводим сообщение об ошибке
            return None  # Возвращаем None при ошибке

    def _extract_from_word(self, file_path):  # Приватный метод для извлечения текста из Word
        """Извлечение текста из Word"""
        try:  # Начало блока обработки исключений
            doc = docx.Document(file_path)  # Создаем объект Document для работы с Word
            text = ""  # Инициализируем пустую строку для текста
            for paragraph in doc.paragraphs:  # Перебираем все абзацы в документе
                text += paragraph.text + "\n"  # Добавляем текст абзаца и перенос строки
            return text  # Возвращаем весь извлеченный текст
        except Exception as e:  # Обрабатываем исключения при чтении Word
            print(f"Ошибка при чтении Word: {str(e)}")  # Выводим сообщение об ошибке
            return None  # Возвращаем None при ошибке
