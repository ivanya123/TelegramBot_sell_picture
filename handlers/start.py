from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboard.all_kb import main_kb, admin_kb, kb_shape, kb_base, kb_size, kb_height_and_width
from keyboard.inline_kbs import inline_link_kb, inline_canvas_base, inline_canvas_size, inline_canvas_height_and_width, \
    inline_choice, admin_add_picture
import asyncio
from aiogram.utils.chat_action import ChatActionSender
import json
from create_bot import bot
from create_bot import admins
from db_handler.db_class import add_pictures, async_session, full_picture_table, add_buyer, get_id_pictures, \
    get_pictures, all_pictures

start_router = Router()


class StartState(StatesGroup):
    canvas_shape = State()
    canvas_base = State()
    canvas_size = State()
    canvas_height_and_width = State()
    canvas_price = State()


class AdminAddPicture(StatesGroup):
    canvas_shape = State()
    canvas_base = State()
    canvas_size = State()
    canvas_height_and_width = State()
    price = State()
    choice = State()


@start_router.message(F.text == 'Выбрать основу холста')
@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, это Любовь, готовьте свои денежки",
                         reply_markup=main_kb(message.from_user.id))


@start_router.message(F.text == 'Админка')
async def admin_start(message: Message):
    if message.from_user.id in admins:
        await message.answer('Дорогой админ, выберите действие', reply_markup=admin_kb())
    else:
        await message.answer('Вы не админ, нечего тут делать')


@start_router.message(F.text == "Показать все картины")
async def admin_look_pictures(message: Message):
    async with async_session() as session:
        text = await full_picture_table(session)
    if len(text) < 4096:
        await message.answer(text)
    if len(text) > 4096:
        for i in range((len(text) // 4096) + 1):
            await message.answer(text[i * 4096:(i + 1) * 4096])


@start_router.message(F.text == "Добавить новый формат картины в базу данных")
async def add_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        pictures = await all_pictures(session)
    if message.from_user.id in admins:
        await state.clear()
        await message.answer("Введите название формата картины", reply_markup=kb_shape(pictures))
        await state.set_state(AdminAddPicture.canvas_shape)
    else:
        await message.answer('Вы не админ, нечего тут делать')


@start_router.message(F.text, AdminAddPicture.canvas_shape)
async def add_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        pictures = await all_pictures(session)
    await state.update_data(canvas_shape=message.text)
    await message.answer("Напишите основу холста", reply_markup=kb_base(pictures))
    await state.set_state(AdminAddPicture.canvas_base)


@start_router.message(F.text, AdminAddPicture.canvas_base)
async def add_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        pictures = await all_pictures(session)
    await state.update_data(canvas_base=message.text)
    await message.answer("Напишите размер холста", reply_markup=kb_size(pictures))
    await state.set_state(AdminAddPicture.canvas_size)


@start_router.message(F.text, AdminAddPicture.canvas_size)
async def add_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        pictures = await all_pictures(session)
    data = await state.get_data()
    shape = data["canvas_shape"]
    await state.update_data(canvas_size=message.text)
    await message.answer("Напишите габариты холста", reply_markup=kb_height_and_width(pictures, shape))
    await state.set_state(AdminAddPicture.canvas_height_and_width)


@start_router.message(F.text, AdminAddPicture.canvas_height_and_width)
async def add_picture(message: Message, state: FSMContext):
    await state.update_data(canvas_height_and_width=message.text)
    await message.answer("Напишите цену холста")
    await state.set_state(AdminAddPicture.price)


@start_router.message(F.text, AdminAddPicture.price)
async def add_picture(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text))
    data = await state.get_data()
    text = (f"Добавить картину в базу данных:\n"
            f"Форма: {data['canvas_shape']}\n"
            f"Основа: {data['canvas_base']}\n"
            f"Размер: {data['canvas_size']}\n"
            f"Габариты: {data['canvas_height_and_width']}\n"
            f"Цена: {data['price']}\n")
    await message.answer(text, reply_markup=admin_add_picture())
    await state.set_state(AdminAddPicture.choice)


@start_router.callback_query(F.data, AdminAddPicture.choice)
async def add_picture(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'Да':
        try:
            async with async_session() as session:
                await add_pictures(session,
                                   data['canvas_shape'],
                                   data['canvas_base'],
                                   data['canvas_size'],
                                   data['canvas_height_and_width'],
                                   data['price'])

            await call.message.answer("Вы успешно добавили картину в базу данных")
        except Exception as e:
            await call.message.answer("Произошла ошибка при добавлении картини в базу данных")
    else:
        await call.message.answer("Вы отменили добавление картины в базу данных")
    await state.clear()


@start_router.message(F.text == 'Обо мне')
async def about_me(message: Message):
    await message.answer("Я Любовь, я помогу вам создать картину, которую вы захотите. "
                         "Для начала выберите формат картины",
                         reply_markup=main_kb(message.from_user.id))


@start_router.message(F.text == 'Выбрать формат картины')
async def start_question(message: Message, state: FSMContext):
    await state.clear()
    with open('info.json', 'r') as f:
        data = json.load(f)
    await message.answer("Выберите формат картины",
                         reply_markup=inline_link_kb(data))
    await state.set_state(StartState.canvas_shape)


@start_router.callback_query(F.data, StartState.canvas_shape)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_shape=call.data)
    with open('info.json', 'r') as f:
        data = json.load(f)

    data_state = await state.get_data()
    await call.answer("Выберите основу холста")
    await call.message.edit_reply_markup(reply_markup=None)
    if data_state["canvas_shape"] == "Нестандартный формат":
        await call.message.answer('Выберите фигуру', reply_markup=inline_canvas_base(data, data_state))
    else:
        await call.message.answer('Выберите основу холста', reply_markup=inline_canvas_base(data, data_state))
    await state.set_state(StartState.canvas_base)


@start_router.callback_query(F.data, StartState.canvas_base)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_base=call.data)
    with open('info.json', 'r') as f:
        data = json.load(f)

    data_state = await state.get_data()
    await call.answer("Выберите размер холста")
    await call.message.edit_reply_markup(reply_markup=None)
    if data_state["canvas_shape"] == "Нестандартный формат":
        await call.message.answer('Только на картоне', reply_markup=inline_canvas_size(data, data_state))
    else:
        await call.message.answer('Выберите размер холста', reply_markup=inline_canvas_size(data, data_state))
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


@start_router.callback_query(F.data, StartState.canvas_height_and_width)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_height_and_width=call.data)
    data_state = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    with open('info.json', 'r') as f:
        data = json.load(f)

    canvas_shape = data_state["canvas_shape"]
    canvas_base = data_state["canvas_base"]
    canvas_size = data_state["canvas_size"]
    canvas_height_and_width = data_state["canvas_height_and_width"]
    price = data[canvas_shape][canvas_base][canvas_size][canvas_height_and_width]

    text = f'Вы выбрали:\n<b>Формат:</b>{data_state["canvas_shape"]}\n' \
           f'<b>Основа</b>: {data_state["canvas_base"]}\n' \
           f'<b>Размер</b>: {data_state["canvas_size"]}\n' \
           f'<b>Габариты</b>: {data_state["canvas_height_and_width"]}\n' \
           f'<tg-spoiler>Но мои картины бесценны,\n' \
           f'Для вас сделаю исключение\n' \
           f'Цена составит: <b>{price} руб.</b></tg-spoiler>'
    await call.message.reply(text)
    await bot.send_message(call.from_user.id, text='Хотите заказать картину???', reply_markup=inline_choice())
    await state.set_state(StartState.canvas_price)


@start_router.callback_query(F.data, StartState.canvas_price)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_price=call.data)
    data_state = await state.get_data()

    if data_state["canvas_price"] == "Да":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(text='Отлично, ждите сообщение с подробностями.\n'
                                       'Если хоите уточнить какие то вопросы пишите мне:\n')
        async with async_session() as session:
            await add_buyer(session,
                            call.from_user.username,
                            str(call.from_user.id),
                            data_state["canvas_shape"],
                            data_state["canvas_base"],
                            data_state["canvas_size"],
                            data_state["canvas_height_and_width"])
            picture = await get_pictures(session,
                                         data_state["canvas_shape"],
                                         data_state["canvas_base"],
                                         data_state["canvas_size"],
                                         data_state["canvas_height_and_width"])
        print(call.from_user.id)
        for admin in admins:
            await bot.send_message(admin, text=f"Сделан заказ картины:\n"
                                               f"id: <b>{picture.id}</b>\n"
                                               f"Форма: <b>{picture.canvas_shape}</b>\n"
                                               f"Основа: <b>{picture.canvas_base}</b>\n"
                                               f"Размер: <b>{picture.canvas_size}</b>, <b>{picture.canvas_height_and_width}</b>\n"
                                               f"Цена: <b>{picture.canvas_base}</b>\n"
                                               f"Покупатель: <b>{call.from_user.username}</b>\n"
                                               f"<a href='tg://user?id={call.from_user.id}'>Связаться с покупателем</a>")
        await state.clear()
    else:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(text=r'Очень жаль, для выбора другой картины напишите \start')
        await state.clear()
