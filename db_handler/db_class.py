from typing import List, Sequence
from datetime import datetime
from sqlalchemy import create_engine, insert, ForeignKey, UniqueConstraint, select, and_
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, selectinload
from sqlalchemy import String, Integer, DateTime, Float, Boolean
from decouple import config
import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg

pg_link = config("PG_LINK")

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
    final_price: Mapped[float] = mapped_column(Float)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    picture: Mapped[Picture] = relationship(back_populates="buyer")


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


if __name__ == '__main__':
    # asyncio.run(create_table())
    # asyncio.run(full_pictures_from_json())
    # asyncio.run(drop_table())
    i = [1, 2]
    print(int('qwe'))
    pass
