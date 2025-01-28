from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import Config

class Database:
    Base = declarative_base()

    def __init__(self):
        self.engine = create_engine(Config.DB_URL)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        db = self.Session()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self):
        # Создание таблиц в базе данных, если они еще не существуют
        self.Base.metadata.create_all(bind=self.engine)