from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Sequence
from db_handler.db_class import Picture, Buyer


def inline_link_kb(pictures: Sequence[Picture]) -> InlineKeyboardMarkup:
    list_picture = list(set([picture.canvas_shape for picture in pictures]))
    list_inline_kb = [[InlineKeyboardButton(text=shape, callback_data=shape)] for shape in list_picture]
    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_base(pictures: Sequence[Picture],
                       data_state: dict[str, any]) -> InlineKeyboardMarkup:
    canvas_shape = data_state['canvas_shape']
    list_picture = list(set([picture.canvas_base for picture in pictures if picture.canvas_shape == canvas_shape]))
    print(list_picture)
    list_inline_kb = [[InlineKeyboardButton(text=base, callback_data=base)] for base in list_picture]

    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_size(pictures: Sequence[Picture],
                       data_state: dict[str, any]) -> InlineKeyboardMarkup:
    canvas_base = data_state['canvas_base']
    list_picture = list(set([picture.canvas_size for picture in pictures if picture.canvas_base == canvas_base]))
    print(list_picture)
    list_inline_kb = [[InlineKeyboardButton(text=key, callback_data=key)] for key in
                      list_picture]

    return InlineKeyboardMarkup(inline_keyboard=list_inline_kb)


def inline_canvas_height_and_width(pictures: Sequence[Picture],
                                   data_state: dict[str, any]) -> InlineKeyboardMarkup:
    canvas_size = data_state['canvas_size']
    list_picture = list(
        set([picture.canvas_height_and_width for picture in pictures if picture.canvas_size == canvas_size]))
    print(list_picture)
    inline_list = [[InlineKeyboardButton(text=elem, callback_data=elem)] for elem in list_picture]
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
