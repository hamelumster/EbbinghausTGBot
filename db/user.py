from typing import Optional
from sqlalchemy.orm import Session
from db.models import User, Word


class UserManager:
    def __init__(self, db: Session, logger=None):
        self.db = db
        self.logger = logger

    def get_or_create_user(self, chat_id: int) -> User:
        user = self.db.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            user = User(chat_id=chat_id)
            self.db.add(user)
            try:
                self.db.commit()
                self.db.refresh(user)
            except Exception as e:
                self.db.rollback()
                raise ValueError(f"Ошибка при сохранении пользователя: {e}")
        return user

    def add_word(self, user_id: int, target_word: str, translate_word: str) -> Optional[Word]:
        existing_word = self.db.query(Word).filter(
            Word.user_id == user_id,
            Word.target_word == target_word
        ).first()

        if existing_word:
            return None

        word = Word(target_word=target_word, translate_word=translate_word, user_id=user_id)
        self.db.add(word)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Ошибка при добавлении слова: {e}")
        return word

    def delete_word(self, user_id: int, target_word: str):
        word = self.db.query(Word).filter(
            Word.user_id == user_id,
            Word.target_word == target_word
        ).first()

        if word:
            self.db.delete(word)
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise ValueError(f"Ошибка при удалении слова: {e}")
            return word
        return None

    def get_user_words(self, user_id: int):
        return self.db.query(Word).filter(Word.user_id == user_id).all()
