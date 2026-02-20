FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# 1. Установка системных зависимостей
# ffmpeg — нужен для Whisper (декодирование аудио)
# libpq-dev — нужен для драйвера PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Установка рабочей директории
# В образе tiangolo стандартная папка — /app
WORKDIR /app

# 3. Установка Python-зависимостей
# Сначала копируем только requirements.txt, чтобы Docker кэшировал слои
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Копирование кода проекта
COPY . .

# 5. Подготовка папки для медиафайлов
# Создаем папку uploads и даем права на запись
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# 6. Настройки среды
# Отключаем создание .pyc файлов и включаем буферизацию логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# По умолчанию запускается FastAPI через Gunicorn (настройки в docker-compose)
# Порт 80 — стандарт для этого базового образа
EXPOSE 80