from telebot import types
from telebot.types import InlineKeyboardButton


# Клавиатура для выбора "да" или "нет"
def get_confirmation_markup():
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Да ✅", callback_data="confirm_yes")
    no_button = types.InlineKeyboardButton("Нет ❌", callback_data="confirm_no")
    markup.add(yes_button, no_button)
    return markup


# Клавиатура для отмены действий
def get_cancel_markup():
    markup = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("Отменить действие", callback_data="cancel_action")
    markup.add(cancel_button)
    return markup
