from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from create_bot import admins

def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text='Выбрать формат картины'),KeyboardButton(text='Обо мне')]
    ]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text='Админка')])
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder='Воспользуйтесь меню:')
    return keyboard
