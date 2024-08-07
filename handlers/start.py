from typing import Sequence
from sqlalchemy import select
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from keyboard.all_kb import main_kb, admin_kb, kb_shape, kb_base, kb_size, kb_height_and_width, ad_update_choice
from keyboard.inline_kbs import inline_link_kb, inline_canvas_base, inline_canvas_size, inline_canvas_height_and_width, \
    inline_choice, admin_add_picture
import asyncio
from aiogram.utils.chat_action import ChatActionSender
import json
from create_bot import bot
from create_bot import admins
from db_handler.db_function import add_pictures, async_session, full_picture_table, add_buyer, get_id_pictures, \
    get_pictures, all_pictures, delete_pictures, update_pictures, Picture, Buyer, full_buyer_table, update_buyer

start_router = Router()


@start_router.message(F.text == 'Выбрать основу холста')
@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
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


class AdminAddPicture(StatesGroup):
    canvas_shape = State()
    canvas_base = State()
    canvas_size = State()
    canvas_height_and_width = State()
    price = State()
    choice = State()
    pictures: Sequence[Picture] = None


@start_router.message(F.text == "Добавить новый формат картины в базу данных")
async def add_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        pictures = await all_pictures(session)
    AdminAddPicture.pictures = pictures
    if message.from_user.id in admins:
        await state.clear()
        await message.answer("Введите название формата картины", reply_markup=kb_shape(pictures))
        await state.set_state(AdminAddPicture.canvas_shape)
    else:
        await message.answer('Вы не админ, нечего тут делать')


@start_router.message(F.text, AdminAddPicture.canvas_shape)
async def add_picture(message: Message, state: FSMContext):
    await state.update_data(canvas_shape=message.text)
    await message.answer("Напишите основу холста", reply_markup=kb_base(AdminAddPicture.pictures))
    await state.set_state(AdminAddPicture.canvas_base)


@start_router.message(F.text, AdminAddPicture.canvas_base)
async def add_picture(message: Message, state: FSMContext):
    await state.update_data(canvas_base=message.text)
    await message.answer("Напишите размер холста", reply_markup=kb_size(AdminAddPicture.pictures))
    await state.set_state(AdminAddPicture.canvas_size)


@start_router.message(F.text, AdminAddPicture.canvas_size)
async def add_picture(message: Message, state: FSMContext):
    data = await state.get_data()
    shape = data["canvas_shape"]
    await state.update_data(canvas_size=message.text)
    await message.answer("Напишите габариты холста", reply_markup=kb_height_and_width(AdminAddPicture.pictures, shape))
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
        except Exception:
            await call.message.answer("Произошла ошибка при добавлении картини в базу данных")
    else:
        await call.message.answer("Вы отменили добавление картины в базу данных")
    await state.clear()


@start_router.message(F.text == 'Обо мне')
async def about_me(message: Message):
    await message.answer("Я Любовь, я помогу вам создать картину, которую вы захотите. "
                         "Для начала выберите формат картины",
                         reply_markup=main_kb(message.from_user.id))


class StartState(StatesGroup):
    canvas_shape = State()
    canvas_base = State()
    canvas_size = State()
    canvas_height_and_width = State()
    canvas_price = State()
    pictures: Sequence[Picture] = None

    def __str__(self):
        text = ', '.join(str(picture.id) for picture in self.pictures)
        return text


@start_router.message(F.text == 'Выбрать формат картины')
async def start_question(message: Message, state: FSMContext):
    await state.clear()
    StartState.pictures = None
    async with async_session() as session:
        pictures: Sequence[Picture] = await all_pictures(session)
    StartState.pictures = pictures
    await message.answer("Выберите формат картины",
                         reply_markup=inline_link_kb(StartState.pictures))
    await state.set_state(StartState.canvas_shape)


@start_router.callback_query(F.data, StartState.canvas_shape)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_shape=call.data)
    data_state = await state.get_data()
    StartState.pictures = [picture for picture in StartState.pictures if
                           picture.canvas_shape == data_state['canvas_shape']]
    await call.answer("Выберите основу холста")
    await call.message.edit_reply_markup(reply_markup=None)
    if data_state["canvas_shape"] == "Нестандартный формат":
        await call.message.answer('Выберите фигуру', reply_markup=inline_canvas_base(StartState.pictures, data_state))
    else:
        await call.message.answer('Выберите основу холста',
                                  reply_markup=inline_canvas_base(StartState.pictures, data_state))
    await state.set_state(StartState.canvas_base)


@start_router.callback_query(F.data, StartState.canvas_base)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_base=call.data)
    data_state = await state.get_data()
    StartState.pictures = [picture for picture in StartState.pictures if
                           picture.canvas_base == data_state['canvas_base']]

    await call.answer("Выберите размер холста")
    await call.message.edit_reply_markup(reply_markup=None)
    if data_state["canvas_shape"] == "Нестандартный формат":
        await call.message.answer('Только на картоне', reply_markup=inline_canvas_size(StartState.pictures, data_state))
    else:
        await call.message.answer('Выберите размер холста',
                                  reply_markup=inline_canvas_size(StartState.pictures, data_state))
    await state.set_state(StartState.canvas_size)


@start_router.callback_query(F.data, StartState.canvas_size)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_size=call.data)
    data_state = await state.get_data()
    StartState.pictures = [picture for picture in StartState.pictures if
                           picture.canvas_size == data_state['canvas_size']]
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Выберите габарит холста',
                              reply_markup=inline_canvas_height_and_width(StartState.pictures, data_state))
    await state.set_state(StartState.canvas_height_and_width)


@start_router.callback_query(F.data, StartState.canvas_height_and_width)
async def start_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(canvas_height_and_width=call.data)
    await call.message.edit_reply_markup(reply_markup=None)
    data_state = await state.get_data()
    StartState.pictures = [picture for picture in StartState.pictures if
                           picture.canvas_height_and_width == data_state['canvas_height_and_width']][0]

    text = f'Вы выбрали:\n<b>Формат:</b>{StartState.pictures.canvas_shape}\n' \
           f'<b>Основа</b>: {StartState.pictures.canvas_base}\n' \
           f'<b>Размер</b>: {StartState.pictures.canvas_size}\n' \
           f'<b>Габариты</b>: {StartState.pictures.canvas_height_and_width}\n' \
           f'<tg-spoiler>Но мои картины бесценны,\n' \
           f'Для вас сделаю исключение\n' \
           f'Максимальная цена: <b>{StartState.pictures.price} руб.</b></tg-spoiler>'
    await call.message.reply(text)
    await bot.send_message(call.from_user.id, text='Хотите заказать картину???', reply_markup=inline_choice())
    await state.set_state(StartState.canvas_price)
    StartState.pictures = None


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
        for admin in admins:
            await bot.send_message(admin, text=f"Сделан заказ картины:\n"
                                               f"id: <b>{picture.id}</b>\n"
                                               f"Форма: <b>{picture.canvas_shape}</b>\n"
                                               f"Основа: <b>{picture.canvas_base}</b>\n"
                                               f"Размер: <b>{picture.canvas_size}</b>, <b>{picture.canvas_height_and_width}</b>\n"
                                               f"Цена: <b>{picture.price}</b>\n"
                                               f"Покупатель: <b>{call.from_user.username}</b>\n"
                                               f"<a href='tg://user?id={call.from_user.id}'>Связаться с покупателем</a>")
        await state.clear()
    else:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(text=r'Очень жаль, для выбора другой картины напишите \start')
        await state.clear()


class AdminDeletePictures(StatesGroup):
    id = State()


@start_router.message(F.text == "Удалить картину")
async def delete_picture(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        async with async_session() as session:
            text = await full_picture_table(session)
        if len(text) < 4096:
            await message.answer(text)
        if len(text) > 4096:
            for i in range((len(text) // 4096) + 1):
                await message.answer(text[i * 4096:(i + 1) * 4096])
        await message.answer(text='Напишите id картины которую хотите удалить. Или несколько id через запятую')
        await state.set_state(AdminDeletePictures.id)


@start_router.message(F.text, AdminDeletePictures.id)
async def delete_picture(message: Message):
    list_id = [int(i.strip()) for i in message.text.split(',')]
    print(list_id)
    try:
        async with async_session() as session:
            for i in list_id:
                await delete_pictures(session, i)

        await message.answer(text=f"Удалены картины {', '.join(str(i) for i in list_id)}")
    except Exception as e:
        await message.answer(f'При удалении произошла ошибка {e}')


class AdminUpdatePicture(StatesGroup):
    id = State()
    choice = State()
    price = State()
    all = State()
    picture = None


@start_router.message(F.text == 'Изменить картину')
async def update_picture(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        async with async_session() as session:
            text = await full_picture_table(session)
        if len(text) < 4096:
            await message.answer(text)
        if len(text) > 4096:
            for i in range((len(text) // 4096) + 1):
                await message.answer(text[i * 4096:(i + 1) * 4096])
        await message.answer(text='Напишите id картины которую хотите изменить.')
        await state.set_state(AdminUpdatePicture.id)


@start_router.message(F.text, AdminUpdatePicture.id)
async def update_picture(message: Message, state: FSMContext):
    async with async_session() as session:
        all_picture = await all_pictures(session)
    list_id_picture = [picture.id for picture in all_picture]
    await state.update_data(id=int(message.text.strip()))
    if int(message.text.strip()) in list_id_picture:
        picture = [picture for picture in all_picture if picture.id == int(message.text.strip())][0]
        AdminUpdatePicture.picture = picture
        await message.answer(text='Что хотите изменить', reply_markup=ad_update_choice())
        await state.set_state(AdminUpdatePicture.choice)
    else:
        await message.answer(text=f"{message.text} нет в базе данных. Для изменения начните сценарий заново.")
        await state.clear()


@start_router.message(F.text, AdminUpdatePicture.choice)
async def update_picture(message: Message, state: FSMContext):
    await state.update_data(choice=message.text)
    if message.text == "Цену":
        await message.answer(text=f"Напишите цену для картины {AdminUpdatePicture.picture.id}:"
                                  f"\n{AdminUpdatePicture.picture.canvas_shape};"
                                  f"{AdminUpdatePicture.picture.canvas_base};"
                                  f"{AdminUpdatePicture.picture.canvas_height_and_width}")
        await state.set_state(AdminUpdatePicture.price)
    elif message.text == "Все":
        await message.answer(text=f"Напишите данные картины в формате(ничего не пропуская)\n"
                                  f"Форма, основа, размер, габариты, цена")
        await state.set_state(AdminUpdatePicture.all)


@start_router.message(F.text, AdminUpdatePicture.price)
async def update_picture(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text.strip()))
    values = {'price': int(message.text.strip())}
    async with async_session() as session:
        await update_pictures(session, index=AdminUpdatePicture.picture.id, values=values)
    await message.answer(text=f"Цена картины {AdminUpdatePicture.picture.id} изменена на "
                              f"<b>{int(message.text.strip())}</b>")


@start_router.message(F.text, AdminUpdatePicture.all)
async def update_picture(message: Message):
    list_param = ['canvas_shape', 'canvas_base', 'canvas_size', 'canvas_height_and_width', 'price']
    if len(message.text.split()) == 5:
        values = {key: value.strip() for key, value in zip(list_param, message.text.split(','))}
        values['price'] = int(values['price'])
        async with async_session() as session:
            await update_pictures(session, index=AdminUpdatePicture.picture.id, values=values)
        await message.answer(text=f"Картина изменена {AdminUpdatePicture.picture.id}")


class AdSetPrice(StatesGroup):
    id = State()
    price = State()
    buyer: Sequence[Buyer] = None
    pictures: Sequence[Picture] = None


@start_router.message(F.text == "Изменить статус заказа")
async def set_price(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admins:
        async with async_session() as session:
            text, AdSetPrice.buyer = await full_buyer_table(session)
        if len(text) < 4096:
            await message.answer(text)
        if len(text) > 4096:
            for i in range((len(text) // 4096) + 1):
                await message.answer(text[i * 4096:(i + 1) * 4096])
        await message.answer(text=f"Выберите ID заказа для активации и назначении цены!!!")
        await state.set_state(AdSetPrice.id)


@start_router.message(F.text, AdSetPrice.id)
async def set_price(message: Message, state: FSMContext):
    await state.update_data(id=int(message.text.strip()))
    try:
        AdSetPrice.buyer = [buyer for buyer in AdSetPrice.buyer if buyer.id == int(message.text.strip())][0]
        await message.answer(
            text="Напишите цену на картину в данном заказе\n"
                 "Для деактивации заказа напишите 'Убрать заказ'",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text='Убрать заказ')]], resize_keyboard=True, one_time_keyboard=True
            )
        )
        await state.set_state(AdSetPrice.price)
    except IndexError:
        await message.answer(text=f"Картины с таким id нет в Базе Данных, введите снова:")


@start_router.message(F.text, AdSetPrice.price)
async def set_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=int(message.text.strip()))
        async with async_session() as session:
            await update_buyer(session, AdSetPrice.buyer, int(message.text.strip()))
        await message.answer(text=f"Заказ активен:\n"
                                  f"ID заказа: {AdSetPrice.buyer.id}\n"
                                  f"Картина: {AdSetPrice.buyer.picture.canvas_shape}-"
                                  f"{AdSetPrice.buyer.picture.canvas_base}-"
                                  f"{AdSetPrice.buyer.picture.canvas_height_and_width}\n"
                                  f"Финальная цена: {int(message.text.strip())}")
        await state.clear()

    elif message.text == 'Убрать заказ':
        async with async_session() as session:
            buyer = await session.get(Buyer, AdSetPrice.buyer.id)
            buyer.status = False
            stmt = select(Buyer)
            await session.execute(stmt)
            await session.commit()
            await message.answer("Изменения внесены!")
            await state.clear()

    else:
        await message.answer(text="Введите целое число или 'Убрать заказ'.")


@start_router.message(F.text == "Посмотреть заказы")
async def see_orders(message: Message):
    if message.from_user.id in admins:
        async with async_session() as session:
            text = await full_buyer_table(session)
        await message.answer(text=text)
