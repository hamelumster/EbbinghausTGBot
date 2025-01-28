from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot, State, custom_filters
from telebot.states import StatesGroup

from bot.scheduler import ReminderScheduler, Reminder
from db.db_core import Database
from db.models import Word, User
from db.user import UserManager
from handlers.buttons import get_confirmation_markup, get_cancel_markup
from utils.config import Config


class MyStates(StatesGroup):
    waiting_for_english_word = State()
    waiting_for_translation = State()
    waiting_for_confirmation = State()
    waiting_for_deletion = State()


# Вспомогательные функции
def save_cancel_message_id(bot, user_id, chat_id, cancel_message):
    """
    Сохраняет ID сообщения с кнопкой отмены в состояние пользователя.
    Используется для удаления инлайн-кнопок, когда они уже неактуальны.
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        data['cancel_message_id'] = cancel_message.message_id


def check_if_command(bot, message):
    """
    Проверяет, является ли сообщение командой. Если да, сбрасывает состояние и отправляет сообщение об отмене.
    """
    if message.text.startswith('/'):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Команда отменена. Введи команду заново.")
        return True
    return False


class Bot:
    def __init__(self):
        self.bot = TeleBot(Config.TELEGRAM_TOKEN)
        self.bot.add_custom_filter(custom_filters.StateFilter(self.bot))
        self.db = Database()
        # self.logger = Logger()
        self.scheduler = BackgroundScheduler()
        self.reminder_scheduler = ReminderScheduler(self.bot, self.scheduler)
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            username = message.from_user.username
            chat_id = message.chat.id

            with next(self.db.get_session()) as db_session:
                user_manager = UserManager(db_session)
                user_manager.get_or_create_user(chat_id)
                self.bot.send_message(
                    chat_id,
                    "👋 Привет! Я помогу тебе выучить английские слова по системе Эббингауза! 📚\n"
                    "\n"
                    "🔠 Для начала добавления слов, нажми /add и введи слово на английском:\n"
                    "\n"
                    "Например, 🇬🇧world\n"
                    "Затем я попрошу тебя ввести перевод слова на русском. Например, 🇷🇺мир\n"
                    "\n"
                    "🕒 Я буду напоминать тебе слова с интервалами, чтобы у тебя была возможность их запомнить.\n Вот график напоминаний:\n"
                    "\n"
                    f"1️⃣ Первое напоминание - через {Reminder.FIRST_REMINDER};\n"
                    f"2️⃣ Второе напоминание - через {Reminder.SECOND_REMINDER};\n"
                    f"3️⃣ Третье напоминание - через {Reminder.THIRD_REMINDER};\n"
                    f"4️⃣ Четвертое напоминание - через {Reminder.FOURTH_REMINDER};\n"
                    f"5️⃣ Пятое напоминание - через {Reminder.FIFTH_REMINDER}.\n"
                    f"6️⃣ Шестое напоминание - через {Reminder.SIXTH_REMINDER}.\n"
                    f"7️⃣ Седьмое напоминание - через {Reminder.SEVENTH_REMINDER}.\n"
                    "\n"
                    "✍️ Для добавления слов используй /add\n"
                    "🗑️ Также ты можешь удалить слово из словаря по команде /delete\n"
                    "ℹ️ Для вызова справки нажми /help\n"
                    "📖 Узнай больше о системе Эббингауза: /what_is_it"
                )

            # Логирование начала сессии
            # self.logger.add_user_to_json(username)

        # Обработчик команды /what_is_it
        @self.bot.message_handler(commands=['what_is_it'])
        def send_what_is_it(message):
            text = (
                "[Кривая забывания Эббингауза](https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D0%B8%D0%B2%D0%B0%D1%8F_%D0%B7%D0%B0%D0%B1%D1%8B%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)"
            )
            self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

        # Обработчик команды /help
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            help_text = (
                "Это бот, который помогает учить слова на английском языке по системе Эббингауза.\n"
                "\n"
                "Доступные команды:\n"
                "✍️ /add - Добавить слово для изучения\n"
                "🗑️ /delete - Удалить слово из словаря\n"
                "📚 /my_words - Посмотреть список всех добавленных слов\n"
                "\n"
                "📖 /what_is_it - Подробнее о системе Эббингауза\n"
                "ℹ️ /help - Показать это сообщение"
            )
            self.bot.send_message(message.chat.id, help_text)

        @self.bot.message_handler(commands=['add'])
        def start_adding_word(message):
            chat_id = message.chat.id
            cancel_markup = get_cancel_markup()

            cancel_message = self.bot.send_message(chat_id, "Введи слово на английском🇬🇧", reply_markup=cancel_markup)
            self.bot.set_state(message.from_user.id, MyStates.waiting_for_english_word, chat_id)

            # Сохраняем ID отправленного сообщения
            save_cancel_message_id(self.bot, message.from_user.id, chat_id, cancel_message)

        # Обработчик для получения английского слова
        @self.bot.message_handler(state=MyStates.waiting_for_english_word)
        def get_english_word(message):
            if check_if_command(self.bot, message):
                return

            chat_id = message.chat.id
            english_word = message.text.strip()
            cancel_markup = get_cancel_markup()

            # Проверка: слово должно состоять только из латинских букв
            if not english_word.isalpha() or not english_word.isascii():
                with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                    cancel_message_id = data.get('cancel_message_id')
                    if cancel_message_id:
                        self.bot.edit_message_reply_markup(chat_id, cancel_message_id, reply_markup=None)

                cancel_message = self.bot.send_message(chat_id,
                                      "Пожалуйста, введи корректное английское слово (только латинские буквы)🇬🇧",
                                      reply_markup=cancel_markup)

                # Сохраняем ID нового сообщения с кнопкой отмены
                save_cancel_message_id(self.bot, message.from_user.id, chat_id, cancel_message)
                return

            # Если слово введено корректно
            with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                cancel_message_id = data.get('cancel_message_id')
                if cancel_message_id:
                    self.bot.edit_message_reply_markup(chat_id, cancel_message_id, reply_markup=None)

                data['english_word'] = english_word.lower()

            # Переход к следующему шагу
            cancel_message = self.bot.send_message(chat_id, "Теперь введи перевод на русском🇷🇺.\n"
                                                            "Если слов несколько, введи их строго через запятую", reply_markup=cancel_markup)
            self.bot.set_state(message.from_user.id, MyStates.waiting_for_translation, chat_id)

            # Сохраняем ID нового сообщения с кнопкой отмены
            save_cancel_message_id(self.bot, message.from_user.id, chat_id, cancel_message)

        # Обработчик для получения перевода слова
        @self.bot.message_handler(state=MyStates.waiting_for_translation)
        def get_translation(message):
            if check_if_command(self.bot, message):
                return

            chat_id = message.chat.id
            translation = message.text.strip()

            # Определяем, как пользователь ввел перевод: через запятую или через пробел
            if "," in translation:
                # Если есть запятые, разделяем по запятым и удаляем лишние пробелы
                translations = [word.strip() for word in translation.split(",")]
            else:
                # Если запятых нет, разделяем по пробелам
                translations = translation.split()

            # Проверка: перевод должен состоять только из кириллических букв
            if any(not word.isalpha() or not all("а" <= char <= "я" for char in word.lower()) for word in translations):
                # Удаление предыдущей кнопки отмены
                with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                    cancel_message_id = data.get('cancel_message_id')
                    if cancel_message_id:
                        self.bot.edit_message_reply_markup(chat_id, cancel_message_id, reply_markup=None)

                # Отправка нового сообщения с кнопкой отмены
                cancel_markup = get_cancel_markup()
                cancel_message = self.bot.send_message(
                    chat_id,
                    "Пожалуйста, введи корректный перевод на русском (только кириллические буквы)🇷🇺.\n "
                    "Если несколько слов, пиши их через запятую.",
                    reply_markup=cancel_markup
                )

                # Сохраняем ID нового сообщения с кнопкой отмены
                save_cancel_message_id(self.bot, message.from_user.id, chat_id, cancel_message)
                return

            # Удаление кнопки "Отменить действие" после правильного ввода перевода
            with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                cancel_message_id = data.get('cancel_message_id')
                if cancel_message_id:
                    self.bot.edit_message_reply_markup(chat_id, cancel_message_id, reply_markup=None)

                    # Сохраняем перевод в зависимости от ввода
                    if "," in translation:
                        # Если перевод введен через запятую, сохраняем с запятыми
                        data['translation'] = ", ".join(translations).lower()
                    else:
                        # Если перевод введен через пробел, сохраняем как есть
                        data['translation'] = " ".join(translations).lower()

                # Отправка сообщения с подтверждением перевода
                confirmation_markup = get_confirmation_markup()
                self.bot.send_message(
                    chat_id,
                    f"Проверь: {data['english_word']} — {data['translation']}. Все верно?",
                    reply_markup=confirmation_markup
                )
                self.bot.set_state(message.from_user.id, MyStates.waiting_for_confirmation, chat_id)

            print(f"Пользователю отправлено подтверждение: {data['english_word']} — {data['translation']}")

        # Обработчик подтверждения
        @self.bot.callback_query_handler(func=lambda call: call.data in ["confirm_yes", "confirm_no"])
        def confirm_word(call):
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            username = call.from_user.username

            self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)

            if call.data == "confirm_yes":
                with self.bot.retrieve_data(user_id, chat_id) as data:
                    english_word = data['english_word']
                    translation = data['translation']

                with next(self.db.get_session()) as db_session:
                    user_manager = UserManager(db_session)
                    user = user_manager.get_or_create_user(chat_id)

                    # Проверка на наличие слова
                    existing_word = db_session.query(Word).filter(
                        Word.user_id == user.user_id,
                        Word.target_word == english_word
                    ).first()

                    if existing_word:
                        self.bot.send_message(chat_id, f"Слово '{english_word}' уже есть в твоем словаре 🤷‍♀️. Введи другое слово.\n"
                                                       f"Нажми /add для продолжения.\n"
                                                       f"\nДля просмотра уже добавленных слов нажми /my_words 📚")
                    else:
                        word = user_manager.add_word(user.user_id, english_word, translation)
                        self.reminder_scheduler.schedule_reminders(chat_id, word.word_id, english_word, translation)
                        self.bot.send_message(chat_id, f"Слово '{english_word}' с переводом '{translation}' добавлено.\n")
                        self.bot.send_message(chat_id, "Для продолжения добавления слов нажимай /add ✍️\n"
                                                       "Показать список всех слов - /my_words 📚")
                        # Логирование добавления слова
                        # self.logger.log_word(username, english_word, translation)

                self.bot.delete_message(chat_id, call.message.message_id)

            elif call.data == "confirm_no":
                # Логика при отказе подтверждения
                cancel_markup = get_cancel_markup()
                self.bot.send_message(chat_id, "Введи слово на английском еще раз", reply_markup=cancel_markup)
                self.bot.set_state(call.from_user.id, MyStates.waiting_for_english_word, chat_id)

        # Удаление слова
        @self.bot.message_handler(commands=['delete'])
        def delete_word(message):
            chat_id = message.chat.id

            with next(self.db.get_session()) as db_session:
                user_manager = UserManager(db_session)
                user = user_manager.get_or_create_user(chat_id)

                words = user_manager.get_user_words(user.user_id)
                if not words:
                    self.bot.send_message(chat_id, "У тебя пока нет добавленных слов. Добавь слова по команде /add ✍️")
                    return

                cancel_markup = get_cancel_markup()
                cancel_message = self.bot.send_message(chat_id, "Введи слово на английском, которое хочешь удалить.", reply_markup=cancel_markup)
                self.bot.set_state(message.from_user.id, MyStates.waiting_for_deletion, chat_id)

                # Сохраняем ID отправленного сообщения
                save_cancel_message_id(self.bot, message.from_user.id, chat_id, cancel_message)

        @self.bot.message_handler(state=MyStates.waiting_for_deletion)
        def process_deletion(message):
            if check_if_command(self.bot, message):
                return

            chat_id = message.chat.id
            word_to_delete = message.text.strip().lower()

            with next(self.db.get_session()) as db_session:
                user_manager = UserManager(db_session)
                user = user_manager.get_or_create_user(chat_id)

                word = user_manager.delete_word(user.user_id, word_to_delete)
                if word:
                    user_manager.delete_word(user.user_id, word_to_delete)
                    self.reminder_scheduler.cancel_reminder(word.word_id)
                    self.bot.send_message(chat_id, f"Слово '{word_to_delete}' удалено.")
                    with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                        cancel_message_id = data.get('cancel_message_id')
                        if cancel_message_id:
                            self.bot.delete_message(chat_id, cancel_message_id)

                    self.bot.send_message(chat_id, f"Если хочешь удалить другое слово - нажми /delete 🗑️\n"
                                                   f"Если хочешь добавить новое слово - нажми /add ✍️\n"
                                                   f"Для просмотра всех слов нажимай /my_words 📚")
                else:
                    self.bot.send_message(chat_id, f"Слово '{word_to_delete}' не найдено в твоем словаре.\n"
                                                   f"Нажми /delete 🗑️ и введи корректное слово на английском.\n"
                                                   f"\nДля просмотра всех своих слов нажимай /my_words 📚\n")
                    with self.bot.retrieve_data(message.from_user.id, chat_id) as data:
                        cancel_message_id = data.get('cancel_message_id')
                        if cancel_message_id:
                            self.bot.delete_message(chat_id, cancel_message_id)
                self.bot.delete_state(message.from_user.id, chat_id)

        @self.bot.message_handler(commands=['my_words'])
        def show_user_words(message):
            chat_id = message.chat.id

            with next(self.db.get_session()) as db_session:
                user_manager = UserManager(db_session)
                user = user_manager.get_or_create_user(chat_id)

                # Получаем список слов, добавленных пользователем
                words = user_manager.get_user_words(user.user_id)

                if not words:
                    self.bot.send_message(chat_id, "У тебя пока нет добавленных слов. Добавь слова по команде /add ✍️")
                else:
                    word_list = "\n".join([f"📚 {idx+1}) {word.target_word} — {word.translate_word}" for idx, word in enumerate(words)])
                    self.bot.send_message(chat_id, f"Твои добавленные слова:\n"
                                                   f"\n"
                                                   f"{word_list}")
                    self.bot.send_message(chat_id, f"\nДля добавления новых слов нажми /add ✍️,\n"
                                                   f"а для удаления 🗑️ - /delete"
                                                   f"\n"
                                                   f"\nℹ️ Вызов справки - /help")

        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_action")
        def cancel_action(call):
            chat_id = call.message.chat.id
            user_id = call.from_user.id

            # Сбрасываем состояние пользователя
            self.bot.delete_state(user_id, chat_id)

            # Отправляем сообщение, что процесс отменен
            self.bot.send_message(chat_id, "Действие отменено. Нажми /help для списка команд.")

            # Удаляем сообщение с инлайн-кнопкой
            self.bot.delete_message(chat_id, call.message.message_id)

    def start_bot(self):
        # Запуск планировщика напоминаний и бота
        self.scheduler.start()
        self.bot.infinity_polling()