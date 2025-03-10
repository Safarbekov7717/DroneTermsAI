import PyPDF2
import docx
import os

class TextExtractor:
    def __init__(self, cleaner):  # Добавляем параметр cleaner
        self.cleaner = cleaner

    def extract_raw_text(self, file_path):
        """Извлечение текста из файла"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_from_word(file_path)
            else:
                print(f"Неподдерживаемый формат файла: {file_extension}")
                return None
        except Exception as e:
            print(f"Ошибка при извлечении текста: {str(e)}")
            return None

    def _extract_from_pdf(self, file_path):
        """Извлечение текста из PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Ошибка при чтении PDF: {str(e)}")
            return None

    def _extract_from_word(self, file_path):
        """Извлечение текста из Word"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Ошибка при чтении Word: {str(e)}")
            return None
