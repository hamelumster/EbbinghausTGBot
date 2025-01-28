from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from db.db_core import Database


class User(Database.Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, unique=True, index=True)
    words = relationship("Word", back_populates="user", cascade="all, delete-orphan")

class Word(Database.Base):
    __tablename__ = 'words'

    word_id = Column(Integer, primary_key=True, index=True)
    target_word = Column(String, nullable=False)
    translate_word = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="words")