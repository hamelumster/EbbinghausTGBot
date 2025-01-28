from db.db_core import Database
from bot.bot import Bot
from utils.logger import Logger

if __name__ == '__main__':
    db = Database()
    db.create_tables()  # Создаем таблицы, если их нет
    print('Бот запущен!')
    bot = Bot()
    # logger = Logger()
    bot.start_bot()