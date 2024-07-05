from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_link_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text='Квадрат', callback_data='Квадрат')],
        [InlineKeyboardButton(text='Прямоугольник', callback_data='Прямоугольник')],
        [InlineKeyboardButton(text='Круг', callback_data='Круг')],
        [InlineKeyboardButton(text='Овал', callback_data='Овал')],
        [InlineKeyboardButton(text='Не стандартный формат', callback_data='Не стандартный формат')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def inline_canvas_base() -> InlineKeyboardMarkup:
    inline_list = [
        [InlineKeyboardButton(text='На подрамнике', callback_data='На подрамнике')],
        [InlineKeyboardButton(text='На картоне', callback_data='На картоне')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def inline_canvas_size() -> InlineKeyboardMarkup:
    inline_list = [
        [InlineKeyboardButton(text='Малый', callback_data='Малый')],
        [InlineKeyboardButton(text='Средний', callback_data='Средний')],
        [InlineKeyboardButton(text='Большой', callback_data='Большой')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def inline_canvas_height_and_width(data: dict[dict[dict[list[str]]]], data_state: dict[str, any]) -> InlineKeyboardMarkup:
    list_shapes = data[data_state['canvas_shape']][data_state['canvas_base']][data_state['canvas_size']]
    inline_list = [[InlineKeyboardButton(text=elem, callback_data=elem)] for elem in list_shapes]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)
