from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from create_bot import admins


def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text='Выбрать формат картины'), KeyboardButton(text='Обо мне')]
    ]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text='Админка')])
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder='Воспользуйтесь меню:')
    return keyboard


def admin_kb():
    kb_list = [
        [KeyboardButton(text='Добавить новый формат картины в базу данных'),
         KeyboardButton(text='Удалить картину')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True,
                               input_field_placeholder='Админ панель')


def kb_shape(pictures):
    list_shapes = list(set(picture.canvas_shape for picture in pictures))
    kb_list = [
        [KeyboardButton(text=shape) for shape in list_shapes]
    ]

    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)


def kb_base(pictures):
    list_bases = list(set(picture.canvas_base for picture in pictures))
    kb_list = [
        [KeyboardButton(text=base) for base in list_bases]
    ]

    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)


def kb_size(pictures):
    list_sizes = list(set(picture.canvas_size for picture in pictures))
    kb_list = [
        [KeyboardButton(text=size) for size in list_sizes]
    ]

    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)


def kb_height_and_width(pictures, shape):
    list_heights_and_widths = list(
        set(picture.canvas_height_and_width for picture in pictures if picture.canvas_shape == shape))
    kb_list = [
        [KeyboardButton(text=height_and_width) for height_and_width in list_heights_and_widths]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)


def ad_update_choice():
    list_choice = ['Все', "Цену", "Форму", "Размер", "Габариты"]
    kb_list_choice = [
        [KeyboardButton(text=choice) for choice in list_choice]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list_choice, resize_keyboard=True, one_time_keyboard=True)
