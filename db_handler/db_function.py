from typing import List, Sequence
from datetime import datetime
from sqlalchemy import create_engine, insert, ForeignKey, UniqueConstraint, select, and_
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, selectinload
from sqlalchemy import String, Integer, DateTime, Float
from decouple import config
import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg
from db_handler.db_class import engine, async_session, Picture, Buyer, Base


async def add_pictures(session: AsyncSession, canvas_shape: str, canvas_base: str, canvas_size: str,
                       canvas_height_and_width: str, price: int):
    picture = Picture(
        canvas_shape=canvas_shape,
        canvas_base=canvas_base,
        canvas_size=canvas_size,
        canvas_height_and_width=canvas_height_and_width,
        price=price
    )
    session.add(picture)
    await session.commit()


async def get_id_pictures(session: AsyncSession,
                          canvas_shape: str,
                          canvas_base: str,
                          canvas_size: str,
                          canvas_height_and_width: str) -> int:
    text = select(Picture).where(and_(
        Picture.canvas_shape == canvas_shape,
        Picture.canvas_base == canvas_base,
        Picture.canvas_size == canvas_size,
        Picture.canvas_height_and_width == canvas_height_and_width
    ))
    result = await session.execute(text)
    picture_id = result.scalar_one_or_none()
    if picture_id:
        return picture_id.id
    else:
        return


async def get_pictures(session: AsyncSession,
                       canvas_shape: str,
                       canvas_base: str,
                       canvas_size: str,
                       canvas_height_and_width: str):
    text = select(Picture).where(and_(Picture.canvas_shape == canvas_shape,
                                      Picture.canvas_base == canvas_base,
                                      Picture.canvas_size == canvas_size,
                                      Picture.canvas_height_and_width == canvas_height_and_width))
    result = await session.execute(text)
    picture = result.scalar_one_or_none()
    if picture:
        return picture
    else:
        return


async def delete_pictures(session: AsyncSession, index: int) -> None:
    picture_delete = await session.get(Picture, index)
    await session.delete(picture_delete)
    await session.commit()


async def update_pictures(session: AsyncSession, index: int, values: dict) -> None:
    picture_update = await session.get(Picture, index)
    for key, value in values.items():
        exec(f"picture_update.{key}=values['{key}']")
    picture = select(Picture).where(Picture.id == index)
    await session.execute(picture)
    await session.commit()


async def full_picture_table(session: AsyncSession):
    result = await session.execute(select(Picture).options(selectinload(Picture.buyer)))
    pictures = result.scalars().all()
    text = ""
    for row in pictures:
        text += (f'id: {row.id}, Формат: {row.canvas_shape},  '
                 f': {row.canvas_base},  '
                 f'canvas_size: {row.canvas_size},  '
                 f'canvas_height_and_width: {row.canvas_height_and_width},  '
                 f'price: {row.price}\n\n')
    return text


async def all_pictures(session: AsyncSession):
    result = await session.execute(select(Picture))
    pictures: Sequence[Picture] = result.scalars().all()
    return pictures


async def full_buyer_table(session: AsyncSession):
    result = await session.execute(select(Buyer).options(selectinload(Buyer.picture)))
    buyers = result.scalars().all()
    text = ''
    for buyer in buyers:
        text += (f"ID заказа: {buyer.id}\n"
                 f"Покупатель: {buyer.username}\n"
                 f"Дата: {buyer.date_order}\n"
                 f"Картина: {buyer.picture.id} -- {buyer.picture.price} руб.\n"
                 f"Финальная цена: {buyer.final_price if buyer.final_price else 'Не назначена'}\n"
                 f"Статус: {'Активен' if buyer.status else 'Не активен'}\n\n")
    return text, buyers


async def add_buyer(session: AsyncSession,
                    username: str,
                    chat_id: str,
                    canvas_shape: str,
                    canvas_base: str,
                    canvas_size: str,
                    canvas_height_and_width: str):
    picture_id = await get_id_pictures(session,
                                       canvas_shape,
                                       canvas_base,
                                       canvas_size,
                                       canvas_height_and_width)

    if picture_id:
        buyer = Buyer(
            username=username,
            chat_id=chat_id,
            picture_id=picture_id,
            final_price=0
        )
        session.add(buyer)
        await session.commit()


async def update_buyer(session: AsyncSession, buyer: Buyer, final_price: int) -> None:
    buyer = await session.get(Buyer, buyer.id)
    buyer.final_price = final_price
    buyer.status = True
    stmt = select(Buyer)
    await session.execute(stmt)
    await session.commit()


async def full_pictures_from_json():
    with open(r"C:\Users\aples\PycharmProjects\TelegramBot_sell_picture\info.json", "r") as f:
        data = json.load(f)
    async with async_session() as session:
        for shape in data:
            for base in data[shape]:
                for size in data[shape][base]:
                    for height_and_width in data[shape][base][size]:
                        price = data[shape][base][size][height_and_width]
                        await add_pictures(session, shape, base, size, height_and_width, price)


if __name__ == '__main__':
    asyncio.run(full_pictures_from_json())
