from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from decouple import config
import os
from pprint import pprint


class Base(DeclarativeBase):
    pass


class Picture(Base):
    __tablename__ = "pictures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canvas_shape: Mapped[str] = mapped_column(String(30))
    canvas_base: Mapped[str] = mapped_column(String(30), nullable=False)
    canvas_size: Mapped[str] = mapped_column(String(30), nullable=False)
    canvas_height_and_width: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    buyers: Mapped[List["Buyer"]] = relationship(back_populates="picture")


class Buyer(Base):
    __tablename__ = "buyers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(20))
    picture_id = mapped_column(ForeignKey("pictures.id"), nullable=False)

    picture: Mapped[Picture] = relationship(back_populates="buyer")


def add_picture(canvas_shape: str, canvas_base: str, canvas_size: str, canvas_height_and_width: str, price: int):
    stmt = insert(Picture).values(canvas_shape=canvas_shape, canvas_base=canvas_base, canvas_size=canvas_size,
                                  canvas_height_and_width=canvas_height_and_width, price=price)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


with open("info.json", 'r') as f:
    data = json.load(f)

if __name__ == '__main__':
    with open("info.json", 'r') as f:
        data = json.load(f)
    for shape in data:
        for base in data[shape]:
            for size in data[shape][base]:
                for height_and_width in data[shape][base][size]:
                    price = data[shape][base][size][height_and_width]
                    add_picture(shape, base, size, height_and_width, price)