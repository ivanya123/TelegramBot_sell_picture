from typing import List
from datetime import datetime
from sqlalchemy import create_engine, insert, ForeignKey, UniqueConstraint, select, and_
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, selectinload
from sqlalchemy import String, Integer, DateTime
from decouple import config
import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg

# Загрузка строки подключения из файла .env
pg_link = config("PG_LINK")

# Создание объекта Engine с правильной строкой подключения
engine = create_async_engine(pg_link, echo=True)
async_session = sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class Picture(Base):
    __tablename__ = "pictures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canvas_shape: Mapped[str] = mapped_column(String(30))
    canvas_base: Mapped[str] = mapped_column(String(30), nullable=False)
    canvas_size: Mapped[str] = mapped_column(String(30), nullable=False)
    canvas_height_and_width: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    buyer: Mapped[List["Buyer"]] = relationship(back_populates="picture")

    __table_args__ = (
        UniqueConstraint('canvas_shape', 'canvas_base', 'canvas_size', 'canvas_height_and_width',
                         name='_canvas_unique'),)


class Buyer(Base):
    __tablename__ = "buyers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(20))
    date_order: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    picture_id: Mapped[int] = mapped_column(ForeignKey("pictures.id"), nullable=False)

    picture: Mapped[Picture] = relationship(back_populates="buyer")


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
            picture_id=picture_id
        )
        session.add(buyer)
        await session.commit()


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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


async def full_picture_table(session: AsyncSession):
    result = await session.execute(select(Picture).options(selectinload(Picture.buyer)))
    pictures = result.scalars().all()
    text = ""
    for row in pictures:
        # buyers = ', '.join(buyer.username for buyer in row.buyer)
        text += (f'id: {row.id}, Формат: {row.canvas_shape},  '
                 f': {row.canvas_base},  '
                 f'canvas_size: {row.canvas_size},  '
                 f'canvas_height_and_width: {row.canvas_height_and_width},  '
                 f'price: {row.price}\n\n')
    return text


async def main():
    async with async_session() as session:
        text = await full_picture_table(session)
    print(text)


if __name__ == '__main__':
    asyncio.run(full_pictures_from_json())
