import os

from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

PG_DSN = f'postgresql+asyncpg://{os.getenv("PG_USER")}:{os.getenv("PG_PASSWORD")}@127.0.0.1:5431/{os.getenv("PG_DB")}'
engine = create_async_engine(PG_DSN)
Base = declarative_base()


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, autoincrement=True)
    birth_year = Column(String)
    eye_color = Column(String)
    films = Column(String)
    gender = Column(String)
    hair_color = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(String)
    created = Column(String)
    edited = Column(String)
    species = Column(String)
    starships = Column(String)
    url = Column(String)
    vehicles = Column(String)


Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


