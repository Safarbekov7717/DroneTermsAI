import re

class TextCleaner:
    def __init__(self):
        # Паттерны для очистки
        self.patterns = {
            'literature': r'(?i)(Литература.*|Список.*литературы.*|Библиографический список.*|References.*)',
            'figures': r'(?i)Рисунок\s+\d+.*?\.|\bРис\.\s*\d+.*?\.',
            'names': r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.|[А-ЯЁ]\.\s*[А-ЯЁ]\.\s+[А-ЯЁ][а-яё]+|[А-ЯЁ][а-яё]+\s+и\s+[А-ЯЁ][а-яё]+',
            'special_chars': r'[^\w\s.,!?;:()\-"«»]',
            'multiple_spaces': r'\s+',
            'multiple_punctuation': r'\.{2,}|,{2,}|!{2,}|\?{2,}|;{2,}',
            'spaces_before_punctuation': r'\s+([.,!?;:])',
            'empty_lines': r'\n\s*\n',
            'dashes_underscores': r'[-_]+',  # Новый паттерн для тире и подчеркиваний
        }

    def remove_literature_section(self, text):
        """Удаление раздела литературы и всего после него"""
        return re.split(self.patterns['literature'], text)[0]

    def remove_figures(self, text):
        """Удаление упоминаний рисунков"""
        return re.sub(self.patterns['figures'], '', text)

    def remove_names(self, text):
        """Удаление имен авторов в различных форматах"""
        return re.sub(self.patterns['names'], '', text)

    def clean_text(self, text):
        if not text:
            return text

        print("Начало очистки текста...")

        # Удаление раздела литературы и всего после него
        text = self.remove_literature_section(text)

        # Удаление упоминаний рисунков
        text = self.remove_figures(text)

        # Удаление имен авторов
        text = self.remove_names(text)

        # Удаление тире и подчеркиваний
        text = re.sub(self.patterns['dashes_underscores'], ' ', text)

        # Удаление специальных символов
        text = re.sub(self.patterns['special_chars'], ' ', text)

        # Замена множественных знаков препинания на одиночные
        text = re.sub(self.patterns['multiple_punctuation'], lambda m: m.group()[0], text)

        # Удаление пробелов перед знаками препинания
        text = re.sub(self.patterns['spaces_before_punctuation'], r'\1', text)

        # Удаление множественных пробелов и пустых строк
        text = re.sub(self.patterns['multiple_spaces'], ' ', text)
        text = re.sub(self.patterns['empty_lines'], '\n', text)

        # Дополнительная очистка
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace(' !', '!')
        text = text.replace(' ?', '?')
        text = text.replace(' ;', ';')
        text = text.replace(' :', ':')

        # Удаление пробелов в начале и конце текста
        text = text.strip()

        print("Очистка текста завершена")
        return text

    def clean_and_log(self, text):
        """Метод для отладки с выводом информации о каждом этапе очистки"""
        print("Исходный размер текста:", len(text))
        
        # Очистка с логированием каждого этапа
        text = self.remove_literature_section(text)
        print("После удаления литературы:", len(text))
        
        text = self.remove_figures(text)
        print("После удаления рисунков:", len(text))
        
        text = self.remove_names(text)
        print("После удаления имен:", len(text))
        
        text = re.sub(self.patterns['dashes_underscores'], ' ', text)
        print("После удаления тире и подчеркиваний:", len(text))
        
        text = re.sub(self.patterns['special_chars'], ' ', text)
        print("После удаления специальных символов:", len(text))
        
        text = self.clean_text(text)
        print("Финальный размер текста:", len(text))
        
        return text
