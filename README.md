# Телеграм-бот для эффективного запоминания английских слов 🚀

[![Лицензия](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## Оглавление
- [Установка](#установка-)
- [Возможности бота](#возможности-✨)
- [Лицензия](#лицензия-)
- [Связь](#связь-)

## Установка ⚙️

### ⚠️ Рекомендуется: Создание виртуального окружения
Перед установкой зависимостей создайте виртуальное окружение:
```bash
python -m venv venv

# Активация:
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```
### Способ 1️⃣: Через Git Clone
1. **Получите токен бота**:
   - Создайте нового бота через [@BotFather](https://t.me/BotFather)
   - Скопируйте полученный API-токен

2. **Клонируйте и установите**:
```bash
git clone https://github.com/hamelumster/EbbinghausTGBot.git
cd EbbinghausTGBot

# Создайте и активируйте окружение (см. раздел выше)
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate для Windows

# Установите зависимости ВНУТРИ окружения
pip install -r requirements.txt
```

3. **Настройка конфигурации**:
   - Создайте файл `.env` в корне проекта
   - Заполните его по примеру:
```ini
# .env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
DB_USER=ваш_пользователь_базы_данных
DB_PASSWORD=ваш_пароль
DB_NAME=название_базы_данных
DB_HOST=хост_базы_данных  # если локально - оставьте localhost
DB_PORT=порт_базы_данных  # для PostgreSQL обычно 5432
```

4. **Запуск бота**:
```bash
python main.py
```
---

### Способ 2️⃣: Установка без Git (Скачивание проекта с GitHub)
1. **Получите токен бота**:
   - Создайте нового бота через [@BotFather](https://t.me/BotFather)
   - Скопируйте полученный API-токен
2. **Скачайте и распакуйте проект** 
3. **Установите зависимости**:
```bash
cd путь_к_проекту  # перейдите в папку проекта

# Создайте и активируйте окружение
python -m venv venv
source venv/bin/activate  # или для Windows

# Установка внутри окружения
pip install -r requirements.txt
```
4. **Создайте и настройте `.env` файл** (как показано выше)
5. **Запустите бота**:
```bash
python main.py
```

### Важно! 🔔
- Все значения в `.env` должны быть заключены в кавычки, если содержат специальные символы
- Для работы с базой данных убедитесь, что PostgreSQL сервер запущен
- Пример структуры Config-класса (уже реализован в проекте):
```python
# config.py
import os

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
```

---

> 💡 Для работы с PostgreSQL вам потребуется:
> - [Установить PostgreSQL](https://www.postgresql.org/download/)
> - Создать базу данных: `CREATE DATABASE your_db_name;` или через терминал IDE: `createdb -U your_user your_db_name`
> - Проверить подключение: `psql -h localhost -U your_user -d your_db_name`


## Возможности бота✨
- ✅ Добавлять слова
- ❌ Удалять слова, которые уже остались в памяти (вашей, не компьютера) :)
- 📖 Просматривать список слов 

---
### Некоторые части кода закомментированы, но так нужно 😉
---

## Лицензия 📄
Этот проект распространяется под лицензией MIT. Подробнее см. в [LICENSE](LICENSE).

---

**Связь**:  
[![Telegram](https://img.shields.io/badge/Telegram-@nkerios-blue)](https://t.me/nkerios)
