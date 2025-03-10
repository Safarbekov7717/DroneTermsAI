from openai import OpenAI
import os
from dotenv import load_dotenv
from tqdm import tqdm
import threading
import time

class AIProcessor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            base_url=os.getenv('OPENAI_BASE_URL'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.available_models = {
            '1': 'gpt-4o',
            '2': 'deepseek-chat'
        }
        self.model_name = None
        self.processing = False

    def select_model(self):
        """Выбор модели ИИ"""
        while True:
            print("\nДоступные модели ИИ:")
            print("0. Вернуться в главное меню")
            print("1. GPT-4o")
            print("2. DeepSeek Chat")
            choice = input("\nВыберите модель (0-2): ")
            
            if choice == '0':
                print("\nВозвращаемся в главное меню...")
                return "return_to_main"  # Специальный флаг для возврата
            elif choice in self.available_models:
                self.model_name = self.available_models[choice]
                print(f"\nВыбрана модель: {self.model_name}")
                return True
            else:
                print("Пожалуйста, выберите 0, 1 или 2")

    def show_processing_progress(self):
        """Показывает бесконечный прогресс-бар обработки"""
        with tqdm(total=100, desc="Обработка текста", bar_format="{l_bar}{bar}| Ожидание ответа от ИИ...") as pbar:
            progress = 0
            while self.processing:
                progress = (progress + 1) % 100
                pbar.n = progress
                pbar.refresh()
                time.sleep(0.1)
            # Заполняем прогресс-бар до конца после получения ответа
            pbar.n = 100
            pbar.refresh()

    def process_text(self, cleaned_text):
        if not cleaned_text:
            print("Получен пустой текст для обработки")
            return None

        if not self.model_name:
            model_result = self.select_model()
            if model_result == "return_to_main":
                return "return_to_main"  # Передаем флаг возврата дальше
            elif not model_result:
                return None

        print(f"Начало обработки текста через ИИ (модель: {self.model_name})...")
        try:
            self.processing = True
            # Запускаем прогресс-бар в отдельном потоке
            progress_thread = threading.Thread(target=self.show_processing_progress)
            progress_thread.start()
            
            # Выполняем запрос к ИИ
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Извлеки из текста термины, связанные с беспилотными авиационными системами (БАС) и 
                                беспилотными летательными аппаратами (БПЛА). Верни результат строго в следующем формате:

                                Термин: [термин]
                                Определение: [определение]
                                Перевод: [перевод]
                                Релевантность: [процент]%

                                Текст для анализа:
                                {cleaned_text}"""
                            }
                        ]
                    }
                ]
            )
            
            # Останавливаем прогресс-бар
            self.processing = False
            progress_thread.join()
            
            print("\nОбработка текста через ИИ завершена")
            return completion.choices[0].message.content
            
        except Exception as e:
            self.processing = False
            progress_thread.join()
            print(f"\nОшибка при обработке текста ИИ: {e}")
            return None
