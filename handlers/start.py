from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboard.all_kb import main_kb
from keyboard.inline_kbs import inline_link_kb, inline_canvas_base, inline_canvas_size, inline_canvas_height_and_width
import asyncio
from aiogram.utils.chat_action import ChatActionSender
import json

start_router = Router()


class StartState(StatesGroup):
    canvas_shape = State()
    canvas_base = State()
    canvas_size = State()
    canvas_height_and_width = State()


@start_router.message(F.text == 'Выбрать основу холста')
@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, это Любовь, готовьте свои денежки",
                         reply_markup=main_kb(message.from_user.id))


@start_router.message(F.text == 'Обо мне')
async def about_me(message: Message):
    await message.answer("Я Любовь, я помогу вам создать картину, которую вы захотите. "
                         "Для начала выберите формат картины",
                         reply_markup=main_kb(message.from_user.id))


@start_router.message(F.text == 'Выбрать формат картины')
async def start_question(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите формат картины",
                         reply_markup=inline_link_kb())
    await state.set_state(StartState.canvas_shape)


@start_router.callback_query(F.data, StartState.canvas_shape)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_shape=call.data)
    await call.answer("Выберите основу холста")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Выберите основу холста', reply_markup=inline_canvas_base())
    await state.set_state(StartState.canvas_base)


@start_router.callback_query(F.data, StartState.canvas_base)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_base=call.data)
    await call.answer("Выберите размер холста")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Выберите размер холста', reply_markup=inline_canvas_size())
    await state.set_state(StartState.canvas_size)


@start_router.callback_query(F.data, StartState.canvas_size)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_size=call.data)
    with open('info.json', 'r') as f:
        data = json.load(f)

    data_state = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Выберите габарит холста', reply_markup=inline_canvas_height_and_width(data, data_state))
    await state.set_state(StartState.canvas_height_and_width)
    print(data_state)


@start_router.callback_query(F.data, StartState.canvas_height_and_width)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_height_and_width=call.data)
    data_state = await state.get_data()
    print(data_state)
    text = f'Вы выбрали:\n<b>Формат:</b>{data_state["canvas_shape"]}\n' \
           f'<b>Основу</b>: {data_state["canvas_base"]}\n' \
           f'<b>Размер</b>: {data_state["canvas_size"]}\n' \
           f'<b>Габарит</b>: {data_state["canvas_height_and_width"]}\n' \
           f'<tg-spoiler>Но мои картины бесценны</tg-spoiler>'
    await call.message.reply(text)
    await state.set_state(StartState.canvas_height_and_width)
    await state.clear()
