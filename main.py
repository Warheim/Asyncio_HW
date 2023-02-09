import asyncio
from aiohttp import ClientSession
from database import Base, Session, engine


async def create_db():
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_db())
