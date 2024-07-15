from typing import List
from sqlalchemy import create_engine, insert, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from decouple import config
import json

# Загрузка строки подключения из файла .env
pg_link = config("PG_LINK")

# Создание объекта Engine с правильной строкой подключения
engine = create_engine(pg_link, echo=True)


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
    picture_id: Mapped[int] = mapped_column(ForeignKey("pictures.id"), nullable=False)

    picture: Mapped[Picture] = relationship(back_populates="buyer")


# Base.metadata.create_all(engine)


def add_picture(canvas_shape: str, canvas_base: str, canvas_size: str, canvas_height_and_width: str, price: int):
    stmt = insert(Picture).values(canvas_shape=canvas_shape, canvas_base=canvas_base, canvas_size=canvas_size,
                                  canvas_height_and_width=canvas_height_and_width, price=price)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def add_buyers(username: str, chat_id: str, picture_id: int):
    stmt = insert(Buyer).values(username=username, chat_id=chat_id, picture_id=picture_id)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()



if __name__ == '__main__':
    with open(r"C:\Users\aples\PycharmProjects\TelegramBot\info.json", 'r') as f:
        data = json.load(f)
    for shape in data:
        for base in data[shape]:
            for size in data[shape][base]:
                for height_and_width in data[shape][base][size]:
                    price = data[shape][base][size][height_and_width]
                    add_picture(shape, base, size, height_and_width, price)
