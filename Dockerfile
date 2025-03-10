FROM python:3.10-slim

WORKDIR /dronetermsai

# Установка системных зависимостей для работы с PDF и DOCX
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p results/csv results/excel db

# Установка прав на директории
RUN chmod -R 777 results db data

CMD ["python", "main.py"]
