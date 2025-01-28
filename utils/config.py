import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Токен бота
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    # Переменные для подключения к базе данных
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST', 'localhost')  # Если хост не указан, по умолчанию используем localhost
    DB_PORT = os.getenv('DB_PORT', '5432')  # Если порт не указан, используем стандартный 5432

    # Формируем строку подключения
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'