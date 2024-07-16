from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_link_kb(data: dict[str, dict[str, dict[str, dict[str, int]]]]) -> InlineKeyboardMarkup:
    list_inline_kb = [[InlineKeyboardButton(text=key, callback_data=key)] for key in data]
    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_base(data: dict[str, dict[str, dict[str, dict[str, int]]]],
                       data_state: dict[str, any]) -> InlineKeyboardMarkup:
    canvas_shape = data_state['canvas_shape']
    list_inline_kb = [[InlineKeyboardButton(text=key, callback_data=key)] for key in data[canvas_shape]]

    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_size(data: dict[str, dict[str, dict[str, dict[str, int]]]],
                       data_state: dict[str, any]) -> InlineKeyboardMarkup:
    list_inline_kb = [[InlineKeyboardButton(text=key, callback_data=key)] for key in
                      data[data_state['canvas_shape']][data_state['canvas_base']]]

    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_height_and_width(data: dict[dict[dict[list[str]]]],
                                   data_state: dict[str, any]) -> InlineKeyboardMarkup:
    list_shapes = data[data_state['canvas_shape']][data_state['canvas_base']][data_state['canvas_size']]
    inline_list = [[InlineKeyboardButton(text=elem, callback_data=elem)] for elem in list_shapes]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def inline_choice():
    list_choice = [
        [InlineKeyboardButton(text="Да, возьмите мои деньги!!!", callback_data="Да"),
         InlineKeyboardButton(text="Нет, не берите мои деньги!!!", callback_data="Нет")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=list_choice)


def admin_add_picture():
    list_choice = [
        [InlineKeyboardButton(text="Да, добавьте картину!!!", callback_data="Да"),
         InlineKeyboardButton(text="Нет, не добавляйте картину!!!", callback_data="Нет")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=list_choice)