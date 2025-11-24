from openai import OpenAI  # Импортируем класс OpenAI из библиотеки openai
import os  # Импортируем модуль для работы с операционной системой
from dotenv import load_dotenv  # Импортируем функцию для загрузки переменных окружения из .env файла
from tqdm import tqdm  # Импортируем класс для отображения прогресс-бара
import threading  # Импортируем модуль для работы с потоками
import time  # Импортируем модуль для работы со временем
import textwrap  # Импортируем модуль для работы с текстом
import tiktoken  # Импортируем библиотеку для подсчета токенов
import requests  # Импортируем библиотеку для HTTP-запросов
import json  # Импортируем библиотеку для работы с JSON

class AIProcessor:  # Класс для обработки текста с помощью ИИ
    def __init__(self):  # Конструктор класса
        load_dotenv()  # Загружаем переменные окружения из .env файла
        self.client = OpenAI(  # Инициализируем клиент OpenAI
            base_url=os.getenv('OPENAI_BASE_URL'),  # Получаем базовый URL из переменных окружения
            api_key=os.getenv('OPENAI_API_KEY')  # Получаем API ключ из переменных окружения
        )
        self.available_models = {  # Словарь доступных моделей
            '1': 'gpt-4o',  # Модель GPT-4o
            '2': 'deepseek-chat'  # Модель DeepSeek Chat
        }
        # Максимальные размеры контекста для разных моделей
        self.model_context_limits = {
            'gpt-4o': 128000,  # Примерное ограничение для GPT-4o
            'deepseek-chat': 16000  # Уменьшаем лимит для DeepSeek Chat из-за нестабильности
        }
        self.model_name = None  # Имя выбранной модели, изначально не выбрано
        self.processing = False  # Флаг, указывающий на процесс обработки
        self.timeout = 180  # Уменьшаем таймаут для запросов к API в секундах (3 минуты)
        self.max_retries = 5  # Увеличиваем количество попыток при ошибках
        self.retry_delay = 5  # Задержка между повторными попытками в секундах
        self.current_progress = 0  # Текущий прогресс обработки (для прогресс-бара)
        self.current_chunk = 0  # Номер текущего обрабатываемого фрагмента
        self.total_chunks = 0  # Общее количество фрагментов для обработки
        self.chunk_completed = False  # Флаг завершения обработки текущего фрагмента

    def select_model(self):  # Метод для выбора модели ИИ
        """Выбор модели ИИ"""
        while True:  # Бесконечный цикл для выбора модели
            print("\nДоступные модели ИИ:")  # Выводим заголовок
            print("0. Вернуться в главное меню")  # Опция возврата в главное меню
            print("1. GPT-4o")  # Опция выбора GPT-4o
            print("2. DeepSeek Chat")  # Опция выбора DeepSeek Chat
            choice = input("\nВыберите модель (0-2): ")  # Запрашиваем выбор пользователя
            
            if choice == '0':  # Если выбран возврат в главное меню
                print("\nВозвращаемся в главное меню...")  # Выводим сообщение
                return "return_to_main"  # Возвращаем специальный флаг для возврата
            elif choice in self.available_models:  # Если выбрана доступная модель
                self.model_name = self.available_models[choice]  # Устанавливаем имя выбранной модели
                print(f"\nВыбрана модель: {self.model_name}")  # Выводим сообщение о выбранной модели
                return True  # Возвращаем True, указывая на успешный выбор
            else:  # Если выбор некорректен
                print("Пожалуйста, выберите 0, 1 или 2")  # Выводим сообщение об ошибке

    def select_domain(self):
        """Ввод предметной области для извлечения терминов"""
        print("\nВведите предметную область для извлечения терминов")
        print("(например: нефтегазовая отрасль, беспилотные летательные аппараты, медицина и т.д.)")
        print("0. Вернуться в главное меню")
        
        domain_input = input("\nВведите название предметной области: ")
        
        if domain_input == '0':
            print("\nВозвращаемся в главное меню...")
            return "return_to_main"
        elif domain_input.strip():  # Проверяем, что ввод не пустой
            return domain_input.strip()  # Возвращаем введенную область
        else:
            print("Пожалуйста, введите название предметной области")
            return self.select_domain()  # Рекурсивно вызываем метод снова при пустом вводе

    def show_chunk_progress(self, chunk_num, total_chunks):
        """Показывает прогресс-бар для текущего фрагмента"""
        with tqdm(total=100, desc=f"Обработка части {chunk_num}/{total_chunks}", 
                  bar_format="{desc}: {percentage:3.0f}%|{bar}| Ожидание ответа от ИИ...") as pbar:
            self.current_progress = 0
            while self.processing and self.current_chunk == chunk_num and not self.chunk_completed:
                # Имитируем прогресс, увеличивая его постепенно
                # Начинаем медленно, затем ускоряемся, но не доходим до 100%
                if self.current_progress < 95:
                    step = max(1, min(5, self.current_progress // 10))  # Шаг увеличивается с прогрессом
                    self.current_progress = min(95, self.current_progress + step)
                    pbar.n = self.current_progress
                    pbar.refresh()
                time.sleep(0.2)
            
            # Завершаем прогресс-бар при окончании обработки
            pbar.n = 100
            pbar.refresh()

    def show_total_progress(self):
        """Показывает общий прогресс обработки всех фрагментов"""
        with tqdm(total=100, desc="Обработка текста", 
                  bar_format="Обработка текста: {percentage:3.0f}%|{bar}| Ожидание ответа от ИИ...") as pbar:
            last_progress = 0
            while self.processing:
                # Обновляем общий прогресс на основе текущего фрагмента и его прогресса
                if self.total_chunks > 0:
                    # Базовый прогресс на основе завершенных фрагментов
                    completed_chunks_progress = (self.current_chunk - 1) * 100 / self.total_chunks
                    # Прогресс текущего фрагмента
                    current_chunk_progress = self.current_progress / self.total_chunks
                    # Общий прогресс
                    total_progress = int(completed_chunks_progress + current_chunk_progress)
                    # Ограничиваем прогресс до 99% до полного завершения
                    total_progress = min(99, total_progress)
                else:
                    total_progress = min(99, self.current_progress)
                
                # Обновляем прогресс-бар только если значение изменилось
                if total_progress != last_progress:
                    pbar.n = total_progress
                    pbar.refresh()
                    last_progress = total_progress
                
                time.sleep(0.2)
            
            # Завершаем прогресс-бар при окончании обработки
            pbar.n = 100
            pbar.refresh()

    def count_tokens(self, text, model_name="gpt-4o"):
        """Подсчет количества токенов в тексте"""
        try:
            # Получаем кодировщик для модели
            if "gpt-4" in model_name:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif "deepseek" in model_name:
                encoding = tiktoken.get_encoding("cl100k_base")  # Используем базовую кодировку для DeepSeek
            else:
                encoding = tiktoken.get_encoding("cl100k_base")  # Используем базовую кодировку по умолчанию
                
            # Подсчитываем токены
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"Ошибка при подсчете токенов: {e}")
            # Возвращаем примерную оценку (1 токен ~ 4 символа)
            return len(text) // 4

    def split_text(self, text, max_tokens=4000):
        """Разделение текста на части с учетом ограничения токенов"""
        if not text:
            return []
            
        # Подсчитываем токены в тексте
        total_tokens = self.count_tokens(text, self.model_name)
        
        # Если текст помещается в лимит, возвращаем его целиком
        if total_tokens <= max_tokens:
            return [text]
            
        # Разделяем текст на абзацы
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self.count_tokens(paragraph, self.model_name)
            
            # Если абзац слишком большой, разделяем его на предложения
            if paragraph_tokens > max_tokens:
                sentences = paragraph.replace('. ', '.\n').split('\n')
                for sentence in sentences:
                    sentence_tokens = self.count_tokens(sentence, self.model_name)
                    
                    # Если предложение все еще слишком большое, разделяем его на части
                    if sentence_tokens > max_tokens:
                        words = sentence.split(' ')
                        temp_sentence = ""
                        temp_tokens = 0
                        
                        for word in words:
                            word_tokens = self.count_tokens(word + ' ', self.model_name)
                            if temp_tokens + word_tokens > max_tokens:
                                if temp_sentence:
                                    if current_tokens + temp_tokens > max_tokens and current_chunk:
                                        chunks.append(current_chunk)
                                        current_chunk = temp_sentence
                                        current_tokens = temp_tokens
                                    else:
                                        current_chunk += " " + temp_sentence if current_chunk else temp_sentence
                                        current_tokens += temp_tokens
                                temp_sentence = word
                                temp_tokens = word_tokens
                            else:
                                temp_sentence += " " + word if temp_sentence else word
                                temp_tokens += word_tokens
                        
                        if temp_sentence:
                            if current_tokens + temp_tokens > max_tokens and current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = temp_sentence
                                current_tokens = temp_tokens
                            else:
                                current_chunk += " " + temp_sentence if current_chunk else temp_sentence
                                current_tokens += temp_tokens
                    else:
                        # Если текущий чанк + предложение превышает лимит, начинаем новый чанк
                        if current_tokens + sentence_tokens > max_tokens and current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = sentence
                            current_tokens = sentence_tokens
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
                            current_tokens += sentence_tokens
            else:
                # Если текущий чанк + абзац превышает лимит, начинаем новый чанк
                if current_tokens + paragraph_tokens > max_tokens and current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                    current_tokens = paragraph_tokens
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                    current_tokens += paragraph_tokens
        
        # Добавляем последний чанк, если он не пустой
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def process_text_chunk(self, chunk, domain, retry_count=0):
        """Обработка одного фрагмента текста"""
        try:
            # Проверяем размер чанка и уменьшаем его, если он слишком большой
            chunk_tokens = self.count_tokens(chunk, self.model_name)
            max_allowed = self.model_context_limits.get(self.model_name, 4000) // 4
            
            if chunk_tokens > max_allowed:
                print(f"Предупреждение: размер фрагмента ({chunk_tokens} токенов) превышает рекомендуемый максимум.")
                # Обрезаем текст до допустимого размера
                words = chunk.split()
                reduced_chunk = ""
                current_tokens = 0
                
                for word in words:
                    word_tokens = self.count_tokens(word + ' ', self.model_name)
                    if current_tokens + word_tokens <= max_allowed:
                        reduced_chunk += word + " "
                        current_tokens += word_tokens
                    else:
                        break
                
                chunk = reduced_chunk.strip()
                print(f"Фрагмент сокращен до {self.count_tokens(chunk, self.model_name)} токенов.")
            
            # Выполняем запрос к ИИ с оптимизированным промтом
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Ты - высококвалифицированный терминолог и эксперт в области "{domain}". 
                        
                        Твоя задача - тщательно проанализировать текст и извлечь из него ВСЕ специализированные термины, 
                        относящиеся к области "{domain}", даже если они встречаются в тексте лишь один раз.
                        
                        При анализе обращай особое внимание на:
                        1. Специальную терминологию и профессиональный жаргон
                        2. Технические термины и названия оборудования
                        3. Названия процессов, методов и технологий
                        4. Аббревиатуры и сокращения
                        5. Единицы измерения и специфические параметры
                        6. Названия материалов, веществ и компонентов
                        7. Специализированные понятия и концепции
                        
                        Для каждого термина ты должен определить его значение на основе контекста, 
                        предоставить перевод (если термин на иностранном языке) и оценить его релевантность 
                        к области "{domain}" в процентах."""
                    },
                    {
                        "role": "user",
                        "content": f"""Проанализируй предоставленный текст и составь глоссарий всех терминов, 
                        относящихся к области "{domain}".

                        ИНСТРУКЦИИ:
                        
                        1. Извлеки ВСЕ термины, связанные с областью "{domain}", включая:
                           - Узкоспециализированные термины
                           - Общеотраслевые термины
                           - Технические термины
                           - Аббревиатуры и сокращения
                           
                        2. Для КАЖДОГО термина укажи:
                           - Точное написание термина из текста
                           - Краткое и точное определение на основе контекста
                           - Перевод (с русского на английский или с английского на русский)
                           - Оценку релевантности к области "{domain}" (от 0% до 100%)
                        
                        3. Формат вывода для КАЖДОГО термина СТРОГО следующий:
                        
                        Термин: [термин как он встречается в тексте]
                        Определение: [четкое определение на основе контекста]
                        Перевод: [перевод термина]
                        Релевантность: [число]%
                        
                        ---
                        
                        Текст для анализа:
                        {chunk}
                        
                        ---
                        
                        Не пропускай ни одного термина, относящегося к указанной области. Твоя задача - создать максимально полный глоссарий."""
                    }
                ],
                timeout=self.timeout,  # Устанавливаем таймаут для запроса
                max_tokens=4000  # Ограничиваем размер ответа
            )
            
            return completion.choices[0].message.content
            
        except requests.exceptions.Timeout:
            # Специальная обработка таймаутов
            print(f"\nТаймаут при обработке фрагмента. Повторная попытка через {self.retry_delay} секунд...")
            time.sleep(self.retry_delay)
            # Увеличиваем задержку для следующей попытки
            self.retry_delay = min(self.retry_delay * 2, 60)  # Не более 60 секунд
            
            # Уменьшаем размер фрагмента при повторной попытке
            if len(chunk) > 1000:
                reduced_size = int(len(chunk) * 0.8)  # Уменьшаем на 20%
                chunk = chunk[:reduced_size]
                print(f"Размер фрагмента уменьшен до {len(chunk)} символов.")
            
            if retry_count < self.max_retries:
                return self.process_text_chunk(chunk, domain, retry_count + 1)
            else:
                return f"Не удалось обработать фрагмент из-за таймаута после {self.max_retries} попыток."
                
        except Exception as e:
            error_str = str(e)
            
            # Проверяем на наличие HTML-ответа с ошибкой 504
            if "504 Gateway Time-out" in error_str or "Gateway Time-out" in error_str:
                print(f"\nОшибка шлюза (504) при обработке фрагмента. Повторная попытка через {self.retry_delay} секунд...")
                time.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, 60)
                
                # Уменьшаем размер фрагмента при повторной попытке
                if len(chunk) > 1000:
                    reduced_size = int(len(chunk) * 0.7)  # Уменьшаем на 30%
                    chunk = chunk[:reduced_size]
                    print(f"Размер фрагмента уменьшен до {len(chunk)} символов.")
                
                if retry_count < self.max_retries:
                    return self.process_text_chunk(chunk, domain, retry_count + 1)
                else:
                    return f"Не удалось обработать фрагмент из-за ошибки шлюза после {self.max_retries} попыток."
            
            # Проверяем на ошибку EOF
            elif "EOF" in error_str:
                print(f"\nОшибка EOF при обработке фрагмента. Повторная попытка через {self.retry_delay} секунд...")
                time.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, 60)
                
                # Значительно уменьшаем размер фрагмента при ошибке EOF
                if len(chunk) > 500:
                    reduced_size = int(len(chunk) * 0.5)  # Уменьшаем на 50%
                    chunk = chunk[:reduced_size]
                    print(f"Размер фрагмента уменьшен до {len(chunk)} символов из-за ошибки EOF.")
                
                if retry_count < self.max_retries:
                    return self.process_text_chunk(chunk, domain, retry_count + 1)
                else:
                    return f"Не удалось обработать фрагмент из-за ошибки EOF после {self.max_retries} попыток."
            
            # Общая обработка других ошибок
            else:
                print(f"\nОшибка при обработке фрагмента: {e}. Повторная попытка {retry_count + 1}/{self.max_retries}...")
                time.sleep(self.retry_delay)
                
                if retry_count < self.max_retries:
                    return self.process_text_chunk(chunk, domain, retry_count + 1)
                else:
                    print(f"\nНе удалось обработать фрагмент после {self.max_retries} попыток: {e}")
                    return f"Ошибка обработки фрагмента: {e}"

    def merge_results(self, results):
        """Объединение результатов обработки нескольких фрагментов текста"""
        if not results:
            return "Не удалось извлечь термины из текста."
            
        # Словарь для хранения уникальных терминов
        terms_dict = {}
        
        # Обрабатываем каждый результат
        for result in results:
            # Пропускаем результаты с ошибками
            if result.startswith("Ошибка") or result.startswith("Не удалось"):
                continue
                
            # Разделяем результат на отдельные термины
            # Используем более надежный способ разделения
            try:
                # Сначала пробуем разделить по двойному переносу строки
                terms = result.split("\n\n")
                
                # Если получился только один элемент, пробуем другие разделители
                if len(terms) <= 1:
                    # Пробуем разделить по "Термин:" с учетом возможных пробелов
                    result = result.replace("Термин: ", "\n\nТермин: ")
                    terms = result.split("\n\nТермин: ")
                    # Удаляем пустые элементы и добавляем префикс обратно
                    terms = ["Термин: " + term for term in terms if term.strip()]
            except Exception as e:
                print(f"Ошибка при разделении результата: {e}")
                continue
            
            for term_block in terms:
                try:
                    lines = term_block.strip().split("\n")
                    
                    # Проверяем, что блок содержит информацию о термине
                    if len(lines) >= 1 and lines[0].startswith("Термин:"):
                        # Извлекаем название термина
                        term_name = lines[0].replace("Термин:", "").strip()
                        
                        # Если термин еще не добавлен в словарь или текущее определение более полное
                        if term_name not in terms_dict or len(term_block) > len(terms_dict[term_name]):
                            terms_dict[term_name] = term_block
                except Exception as e:
                    print(f"Ошибка при обработке блока термина: {e}")
                    continue
        
        # Если не удалось извлечь ни одного термина
        if not terms_dict:
            return "Не удалось извлечь термины из текста. Возможно, в тексте нет специализированных терминов по указанной области."
        
        # Объединяем все уникальные термины в один результат
        merged_result = "\n\n".join(terms_dict.values())
        
        return merged_result

    def process_text(self, cleaned_text):  # Метод для обработки текста
        if not cleaned_text:  # Если текст пустой
            print("Получен пустой текст для обработки")  # Выводим сообщение об ошибке
            return None  # Возвращаем None

        if not self.model_name:  # Если модель не выбрана
            model_result = self.select_model()  # Предлагаем выбрать модель
            if model_result == "return_to_main":  # Если выбран возврат в главное меню
                return "return_to_main"  # Передаем флаг возврата дальше
            elif not model_result:  # Если выбор модели не удался
                return None  # Возвращаем None
        
        # Всегда запрашиваем предметную область при каждом вызове process_text
        domain_result = self.select_domain()  # Предлагаем ввести предметную область
        if domain_result == "return_to_main":  # Если выбран возврат в главное меню
            return "return_to_main"  # Передаем флаг возврата дальше
        
        # Используем полученную область для текущего запроса
        domain = domain_result

        # Определяем максимальный размер чанка (в токенах)
        # Оставляем место для промта и ответа
        model_limit = self.model_context_limits.get(self.model_name, 4000)
        
        # Для DeepSeek Chat используем более консервативный подход
        if self.model_name == 'deepseek-chat':
            max_chunk_tokens = min(2000, model_limit // 8)  # Используем 1/8 от лимита модели или 2000, что меньше
        else:
            max_chunk_tokens = min(4000, model_limit // 4)  # Используем 1/4 от лимита модели или 4000, что меньше
        
        # Разделяем текст на части, если он слишком большой
        text_chunks = self.split_text(cleaned_text, max_chunk_tokens)
        self.total_chunks = len(text_chunks)
        
        if self.total_chunks > 1:
            print(f"Текст разделен на {self.total_chunks} частей для обработки")
        
        print(f"Начало обработки текста через ИИ (модель: {self.model_name}, область: {domain})...")
        
        try:
            self.processing = True  # Устанавливаем флаг обработки
            
            # Запускаем общий прогресс-бар в отдельном потоке
            total_progress_thread = threading.Thread(target=self.show_total_progress)
            total_progress_thread.start()
            
            results = []
            
            # Обрабатываем каждый фрагмент текста
            for i, chunk in enumerate(text_chunks):
                self.current_chunk = i + 1
                self.current_progress = 0
                self.chunk_completed = False
                
                # Запускаем прогресс-бар для текущего фрагмента в отдельном потоке
                chunk_progress_thread = threading.Thread(
                    target=self.show_chunk_progress, 
                    args=(self.current_chunk, self.total_chunks)
                )
                chunk_progress_thread.start()
                
                # Сбрасываем задержку перед каждой новой частью
                self.retry_delay = 5
                
                # Обрабатываем текущий фрагмент
                chunk_result = self.process_text_chunk(chunk, domain)
                results.append(chunk_result)
                
                # Сигнализируем о завершении обработки фрагмента и ждем завершения потока прогресс-бара
                self.chunk_completed = True
                self.current_progress = 100
                chunk_progress_thread.join(timeout=1)  # Ждем завершения потока с таймаутом
                
                # Добавляем небольшую паузу между обработкой частей
                if i < self.total_chunks - 1:
                    time.sleep(0.5)
            
            # Объединяем результаты обработки всех фрагментов
            final_result = self.merge_results(results)
            
            # Останавливаем общий прогресс-бар
            self.processing = False
            total_progress_thread.join(timeout=1)  # Ждем завершения потока с таймаутом
            
            print("\nОбработка текста через ИИ завершена")
            return final_result
            
        except Exception as e:
            self.processing = False
            self.chunk_completed = True
            if 'total_progress_thread' in locals() and total_progress_thread.is_alive():
                total_progress_thread.join(timeout=1)
            print(f"\nОшибка при обработке текста ИИ: {e}")
            return None