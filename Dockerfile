# Используем легкий образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
# ffmpeg нужен для работы Whisper (конвертация аудио)
# libpq-dev нужен для подключения к PostgreSQL
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем только requirements, чтобы закэшировать установку библиотек
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Создаем папку для загрузок, если её нет
RUN mkdir -p uploads

# Открываем порт для FastAPI
EXPOSE 8000

# Команда для запуска (через uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]